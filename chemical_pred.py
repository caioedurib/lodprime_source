import pubchempy as pcp
from csv import reader
import numpy as np
from pickle import load
from classify_inputs import check_knownclasslabels
#link to pcp package github: https://github.com/mcs07/PubChemPy/blob/master/examples/Chemical%20fingerprints%20and%20similarity.ipynb
# paper link: https://jcheminf.biomedcentral.com/articles/10.1186/s13321-017-0195-1
from classify_inputs import validate_str_ids

keep_positions_mixedsexds = []
keep_positions_maleonlyds = []
with open(f"internal_files/input_source/male dataset feature lists/Feature List - Fingerprints - mixed-sex.txt") as f:
    csv_reader = reader(f)
    for bit in csv_reader:
        keep_positions_mixedsexds.append((bit[0].split(' ')[0]))
    f.close()

with open(f"internal_files/input_source/male dataset feature lists/FeatureList - Fingerprints - male-only.txt") as f:
    csv_reader = reader(f)
    for bit in csv_reader:
        keep_positions_maleonlyds.append((bit[0].split(' ')[0]))
    f.close()


def make_predictions(model, dict_InputTable):
    if model == 'mixed-sex':
        model_name = 'model_Fingerprints_mixedsex'
    elif model == 'male-only':
        model_name = 'model_Fingerprints_maleonly'
    with open(f'internal_files/models/{model_name}.pkl', "rb") as f:  # add try-catch for file not found error
        rf_model = load(f)
        dict_KEGG_predictions = {}
        for row_number in dict_InputTable.keys():
            if dict_InputTable[row_number][1] == "":  # if no cid is provided in the table for this row, use name as identifier
                fingerprint = get_filteredfingerprint(dict_InputTable[row_number][0], model, False)
            else:
                fingerprint = get_filteredfingerprint(dict_InputTable[row_number][1], model, True)  # otherwise, use cid
            if np.sum(fingerprint) > 0:  # valid input, with at least one '1' value
                prediction = rf_model.predict_proba(fingerprint.reshape(1, -1))  # .values to convert Series to array, then .reshape to make it into a dataframe object that can be passed as parameter to predict
                prediction = round(prediction[0][1]*100) # pos 5: male prediction
            else:
                prediction = 0
                dict_InputTable[row_number][2] = f'Warning: compound in row {row_number} not found, skipped. Provided identifiers: Name={dict_InputTable[row_number][0]} CID={dict_InputTable[row_number][1]}.'
            if model == 'mixed-sex':
                dict_InputTable[row_number][4] = prediction  # position 4 for female mouse prediction
            elif model == 'male-only':
                dict_InputTable[row_number][3] = prediction  # position 3 for male mouse prediction
    return dict_InputTable


def get_filteredfingerprint(identifier, model, cid_provided):
    if cid_provided:  # identifier is a cid (row[1] in dictInputTable)
        try:
            pubchem_compound_data = pcp.Compound.from_cid(identifier)
        except:
            pubchem_compound_data =-1
    else:  # identifier is a name (row[0] in dictInputTable)
        try:
            compound_cid_from_name = pcp.get_compounds(identifier={identifier}, namespace='name')[0].cid
            pubchem_compound_data = pcp.Compound.from_cid(compound_cid_from_name)
        except:
            pubchem_compound_data = -1
    if pubchem_compound_data != -1:
        temp_fingerprint = bin(int(pubchem_compound_data.fingerprint, 16))
        list_form_temp_fingerprint = list(temp_fingerprint)
        full_fingerprint = list_form_temp_fingerprint[12:-7]  # remove the first 12 bits prefix (the 0b + 1101110001, which indicates the 881 bit lenght of the fingerprint) and the 7 bits sufix (0s padding)
        if model == 'mixed-sex':  # filter fingerprint using mixed-sex dataset features list
            global keep_positions_mixedsexds
            filtered_fingerprint = np.take(full_fingerprint, keep_positions_mixedsexds)
        elif model == 'male-only': # filter fingerprint using male-only dataset features list
            global keep_positions_maleonlyds
            filtered_fingerprint = np.take(full_fingerprint, keep_positions_maleonlyds)
    else:
        print(f'Warning: Identifier not found: {identifier}. Skipping entry for chemical prediction.')
        return [0]
    if model == 'mixed-sex':
        filtered_fingerprint = np.insert(filtered_fingerprint, 0, 1) # add a 1 value at the beggining of the array for sex = F
    return filtered_fingerprint.astype(np.int32)


def Btn_MakeChemPredictions(targets_list):
    dict_inputTable = {}
    # CHEMICAL positions in dict: 0: "compound_name", 1: "cid", 2: "warnings", 3: "male_predprob", 4: "female_predprob"
    rowcount = 0
    for row in targets_list:
        rowcount = rowcount + 1
        compound_name = row["compound"]
        if compound_name == "":
            compound_name = f'Row_{rowcount}'
        #compound_names, warnings = validate_str_ids(row["compound"])
        dict_inputTable.setdefault(rowcount, [compound_name, row["cid"], "", 0, 0])

    dict_inputTable = check_knownclasslabels(dict_inputTable, 2)  # warning position is 2 for chem predictions
    dict_inputTable = make_predictions('mixed-sex', dict_inputTable)  # make F predictions for each row of the table
    dict_inputTable = make_predictions('male-only', dict_inputTable)  # make M predictions for each row of the table
    # Second run-through of table, writing outputs back on the web object
    rowcount = 0
    for row in targets_list:
        rowcount = rowcount + 1
        # positions in dict: 0: "compound_name", 1: "cid", 2: "warnings", 3: "male_predprob", 4: "female_predprob"
        print(f'Received compound: {dict_inputTable[rowcount][0]}')
        row["compound"] = dict_inputTable[rowcount][0]
        row["cid"] = dict_inputTable[rowcount][1]
        row["m_prediction"] = dict_inputTable[rowcount][3]
        row["f_prediction"] = dict_inputTable[rowcount][4]

        if len(dict_inputTable[rowcount][2]) > 0:  # if there are any errors or warnings to print
            warning_string = ""
            for warning in dict_inputTable[rowcount][2]:
                warning_text = warning_string + warning + "\n"
            row["detailed_results"] = warning_text
        else:
            row["detailed_results"] = ""
    return targets_list

