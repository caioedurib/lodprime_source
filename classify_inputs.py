#classify_inputs.py
from pickle import load
from random import randint
import numpy as np
import pandas as pd
import sklearn
from csv import reader
'''
# working example of pickle load
from sklearn import datasets
X, y = datasets.load_iris(return_X_y=True)
with open("files/classifier.pkl", "rb") as f: #add try-catch for file not found error
    clf = load(f)
    print(clf.predict(X[0:1]))
'''

'''
 - get input objects from HTML form post, they should be comma separated lists
 - Separate lists of targets into different arrays
 - Validate each component of the list a valid UniProt ID
 - List the annotations from the listed targets, with a flag indicating whether it exists in the training data
 - Output warnings for annotations that will be disregarded
 - Load the pre-trained model (pickled)
 - Classify the input instances
 - Run similarity checks from input instances and existing instances, output nearest neighbours (flag if high similarity)
'''
def load_allcatsdataset():
    df1 = pd.read_csv(f'internal_files/input_source/Annotation_Source - NE All Categories - part 1.tsv', sep='\t', index_col=0)
    df2 = pd.read_csv(f'internal_files/input_source/Annotation_Source - NE All Categories - part 2.tsv', sep='\t', index_col=0)
    df3 = pd.read_csv(f'internal_files/input_source/Annotation_Source - NE All Categories - part 3.tsv', sep='\t', index_col=0)
    return pd.concat([df1, df2, df3])

def filter_male_dataset(df_mixed_sex, feature_list):
    featureList = []
    with open(f'internal_files/input_source/male dataset feature lists/{feature_list}.txt', encoding='utf-8') as read_obj:
        csv_reader = reader(read_obj, delimiter="\t")
        for row in csv_reader:
            featureList.append(row[0])
    df_male = df_mixed_sex.loc[:, featureList]  # Select columns between two columns plus sex column
    return df_male

print('Loading files into memory (this may take about a minute)')
df_AllCategories = load_allcatsdataset()

df_KEGG_Mixed = df_AllCategories.loc[:, ['sex', *df_AllCategories.loc[:, 'hsa04024':'hsa03013'].columns]]  # Select columns between two columns plus sex column
df_RCTM_Mixed = df_AllCategories.loc[:, ['sex', *df_AllCategories.loc[:, 'HSA-373076':'HSA-198933'].columns]]  # Select columns between two columns plus sex column
df_Component_Mixed = df_AllCategories.loc[:, ['sex', *df_AllCategories.loc[:, 'GO:0005667':'GO:0033553'].columns]]  # Select columns between two columns plus sex column
df_WikiPathways_Mixed = df_AllCategories.loc[:, ['sex', *df_AllCategories.loc[:, 'WP4320':'WP5053'].columns]]  # Select columns between two columns plus sex column
df_FAInterPro_Mixed = pd.read_csv(f'internal_files/input_source/Annotation_Source - FA InterPro.tsv', sep='\t', index_col=0)

df_FAInterPro_Male = filter_male_dataset(df_FAInterPro_Mixed, 'FeatureList - FAInterPro')
df_Process_Male = filter_male_dataset(df_AllCategories, 'FeatureList - Process')  # uses all cats ds, must be before it gets filtered in next line
df_AllCategories = filter_male_dataset(df_AllCategories, 'FeatureList - All Categories')
df_Component_Male = filter_male_dataset(df_Component_Mixed, 'FeatureList - Component')
df_KEGG_Male = filter_male_dataset(df_KEGG_Mixed, 'FeatureList - KEGG')
print('Files loaded succesfully :)')

df_DrugBank_source = pd.read_csv('static/files/datasets/DrugBank_TargetsSource.tsv', sep='\t', index_col=0, encoding='utf-8')
df_KnownClassLabel_source = pd.read_csv('static/files/datasets/Compounds with known class label.tsv', sep='\t', index_col=0, encoding='utf-8')


def check_knownclasslabels(dict_InputTable, warning_position):
    print(f'checking known class labels with pos {warning_position}')
    global df_KnownClassLabel_source
    for row_number in dict_InputTable.keys():
        current_compound = dict_InputTable[row_number][0]
        try:
            Class_M = df_KnownClassLabel_source.loc[current_compound]['Class_M']  # exact name search
            Class_F = df_KnownClassLabel_source.loc[current_compound]['Class_F']  # exact name search
            print(f'Known compound found: {current_compound}. It has Class_Male = {Class_M} and Class_Female = {Class_F}')
            dict_InputTable[row_number][warning_position].append(f'Known compound found: {current_compound}. It has Class_Male = {Class_M} and Class_Female = {Class_F}')  # errors and warnings in position 3.
        except:
            print(f'Compound not found: {current_compound}.')
    return dict_InputTable


def find_targets(input_string):
    input_string = str.lower(input_string)
    try:
        targets_list = df_DrugBank_source.loc[input_string]['Targets_List_STRINGIDs']  # exact name search
    except:
        targets_list = "Not found"
    if targets_list == "Not found":
        for row in df_DrugBank_source.itertuples():
            try:
                if row[1].find(input_string) != -1:  # drugbank id search
                    targets_list = row[3]
                    break
                if row[2].find(input_string) != -1:  # synonyms list search
                    targets_list = row[3]
                    break
            except:
                continue
    try:
        genenames_list = df_DrugBank_source.loc[input_string]['Targets_List_GeneNames']  # exact name search
    except:
        genenames_list = "Not found"
    if genenames_list == "Not found":
        for row in df_DrugBank_source.itertuples():
            try:
                if row[1].find(input_string) != -1:  # drugbank id search
                    genenames_list = row[4]
                    break
                if row[2].find(input_string) != -1:  # synonyms list search
                    genenames_list = row[4]
                    break
            except:
                continue
    return targets_list, genenames_list


def Btn_Autofill_Targets(input_table):
    for row in input_table:
        compound_name = row["compound"]
        if compound_name != "":
            targets_list, genenames_list = find_targets(compound_name)
            row["str_ids"] = targets_list
            row["gene_names"] = genenames_list
    return input_table

#KEGG: model_NEKEGG_mixedsex
def make_predictions(filtered_df, model_name, dict_InputTable):
    with open(f'internal_files/models/{model_name}.pkl', "rb") as f:  # add try-catch for file not found error
        rf_model = load(f)
        dict_predictions_currentmodel = {}
        for row_number in dict_InputTable.keys():
            indexes_list = dict_InputTable[row_number][4]
            row_df_targets_source = filtered_df.loc[indexes_list]  # pos 4: indexes_list
            row_df_targets_source.loc['total'] = row_df_targets_source.sum()  # create row named 'total' with the sums of all column's values
            total_row = row_df_targets_source.loc['total']
            output_series = total_row[:] #transform into series
            output_series = np.clip(output_series, 0, 1)
            if np.sum(output_series) > 0:  # valid input, with at least one '1' value
                prediction = rf_model.predict_proba(output_series.values.reshape(1, -1))  # .values to convert Series to array, then .reshape to make it into a dataframe object that can be passed as parameter to predict
                prediction = round(prediction[0][1]*100) # pos 5: male prediction
            else:
                prediction = -1
            dict_predictions_currentmodel.setdefault(row_number, prediction)
    return dict_predictions_currentmodel


# Receives a dictionary object with each row in input table, with their respective list of indexes
# fills out a male and female predprob value for each row (dictionary item) (use test_combinerows to create this)
def get_ensemble_predictions(dict_InputTable):
    global df_AllCategories
    global df_Component_Male
    global df_KEGG_Male
    global df_Process_Male
    global df_FAInterPro_Male
    global df_KEGG_Mixed
    global df_RCTM_Mixed
    global df_Component_Mixed
    global df_WikiPathways_Mixed
    global df_FAInterPro_Mixed

    dict_predictions_FAInterPro_Male = make_predictions(df_FAInterPro_Male, 'model_FAInterPro_maleonly', dict_InputTable)
    dict_predictions_AllCats_Male = make_predictions(df_AllCategories, 'model_NEAllCats_maleonly', dict_InputTable)
    dict_predictions_Component_Male = make_predictions(df_Component_Male, 'model_NEComponent_maleonly', dict_InputTable)
    dict_predictions_KEGG_Male = make_predictions(df_KEGG_Male, 'model_NEKEGG_maleonly', dict_InputTable)
    dict_predictions_Process_Male = make_predictions(df_Process_Male, 'model_NEProcess_maleonly', dict_InputTable)

    for rownumber in dict_InputTable.keys():
        result_prediction = 0
        valid_predictions = 5
        if dict_predictions_FAInterPro_Male[rownumber] != -1:
            result_prediction = result_prediction + dict_predictions_FAInterPro_Male[rownumber]
        else:
            valid_predictions = valid_predictions -1
            dict_InputTable[rownumber][3].append(f'Warning: Model InterPro Domains (M) had no valid data for {dict_InputTable[rownumber][0]}.')
        if dict_predictions_AllCats_Male[rownumber] != -1:
            result_prediction = result_prediction + dict_predictions_AllCats_Male[rownumber]
        else:
            valid_predictions = valid_predictions -1
            dict_InputTable[rownumber][3].append(f'Warning: Model All Categories (M) had no valid data for {dict_InputTable[rownumber][0]}.')
        if dict_predictions_Component_Male[rownumber] != -1:
            result_prediction = result_prediction + dict_predictions_Component_Male[rownumber]
        else:
            valid_predictions = valid_predictions -1
            dict_InputTable[rownumber][3].append(f'Warning: Model GO Components (M) had no valid data for {dict_InputTable[rownumber][0]}.')
        if dict_predictions_KEGG_Male[rownumber] != -1:
            result_prediction = result_prediction + dict_predictions_KEGG_Male[rownumber]
        else:
            valid_predictions = valid_predictions -1
            dict_InputTable[rownumber][3].append(f'Warning: Model KEGG Pathways (M) had no valid data for {dict_InputTable[rownumber][0]}.')
        if dict_predictions_Process_Male[rownumber] != -1:
            result_prediction = result_prediction + dict_predictions_Process_Male[rownumber]
        else:
            valid_predictions = valid_predictions - 1
            dict_InputTable[rownumber][3].append(f'Warning: Model GO Process (M) had no valid data for {dict_InputTable[rownumber][0]}.')
        if valid_predictions != 0:  # if there are any valid predictions, average them
            result_prediction = round(result_prediction / valid_predictions)
        else:  # otherwise return defaul value of 0
            result_prediction = 0
        dict_InputTable[rownumber][5] = result_prediction  # pos 5: male mice prediction, from male-only model

    dict_predictions_KEGG_Female = make_predictions(df_KEGG_Mixed, 'model_NEKEGG_mixedsex', dict_InputTable)
    dict_predictions_RCTM_Female = make_predictions(df_RCTM_Mixed, 'model_NEReactome_mixedsex', dict_InputTable)
    dict_predictions_Component_Female = make_predictions(df_Component_Mixed, 'model_NEComponent_mixedsex', dict_InputTable)
    dict_predictions_WikiPathways_Female = make_predictions(df_WikiPathways_Mixed, 'model_NEWikiPathways_mixedsex', dict_InputTable)
    dict_predictions_FAInterPro_Female = make_predictions(df_FAInterPro_Mixed, 'model_FAInterPro_mixedsex', dict_InputTable)

    for rownumber in dict_InputTable.keys():
        result_prediction = 0
        valid_predictions = 5
        if dict_predictions_KEGG_Female[rownumber] != -1:
            result_prediction = result_prediction + dict_predictions_KEGG_Female[rownumber]
        else:
            valid_predictions = valid_predictions - 1
            dict_InputTable[rownumber][3].append(f'Warning: Model KEGG Pathways (F) had no valid data for {dict_InputTable[rownumber][0]}.')
        if dict_predictions_RCTM_Female[rownumber] != -1:
            result_prediction = result_prediction + dict_predictions_RCTM_Female[rownumber]
        else:
            valid_predictions = valid_predictions - 1
            dict_InputTable[rownumber][3].append(f'Warning: Model Reactome Pathways (F) had no valid data for {dict_InputTable[rownumber][0]}.')
        if dict_predictions_Component_Female[rownumber] != -1:
            result_prediction = result_prediction + dict_predictions_Component_Female[rownumber]
        else:
            valid_predictions = valid_predictions - 1
            dict_InputTable[rownumber][3].append(f'Warning: Model GO Component (F) had no valid data for {dict_InputTable[rownumber][0]}.')
        if dict_predictions_WikiPathways_Female[rownumber] != -1:
            result_prediction = result_prediction + dict_predictions_WikiPathways_Female[rownumber]
        else:
            valid_predictions = valid_predictions - 1
            dict_InputTable[rownumber][3].append(f'Warning: Model Wiki Pathways (F) had no valid data for {dict_InputTable[rownumber][0]}.')
        if dict_predictions_FAInterPro_Female[rownumber] != -1:
            result_prediction = result_prediction + dict_predictions_FAInterPro_Female[rownumber]
        else:
            valid_predictions = valid_predictions - 1
            dict_InputTable[rownumber][3].append(f'Warning: Model InterPro Domains (F) had no valid data for {dict_InputTable[rownumber][0]}.')
        if valid_predictions != 0:  # if there are any valid predictions, average them
            result_prediction = round(result_prediction / valid_predictions)
        else:  # otherwise return defaul value of 0
            result_prediction = 0
        dict_InputTable[rownumber][6] = result_prediction  # pos 6: female mice prediction, from mixed-sex model
    return dict_InputTable


# Receives a dictionary object with each row in input table, with their respecti str_ids and gene_names, to be looked up on Indexing_Source - Annotation Datasets
# fills out a list of numeric indexes for each row (dictionary item), which can then be used in iloc (faster than loc) on the prediction function
def update_indexes_list(dict_InputTable):
    df_index_source = pd.read_csv(f'internal_files/input_source/Indexing_Source - Annotation Datasets.tsv', sep='\t', index_col=0)
    for compound in dict_InputTable.keys():
        strids_indexes_list = []
        geneids_indexes_list = []
        str_ids = dict_InputTable[compound][1]  # pos 1: str_ids
        gene_ids = dict_InputTable[compound][2]  # pos 2: gene_ids
        if len(str_ids) > 0:  # does not assume all input str_ids will be part of the dataset.
            # Can compare this to len to count not found and update warnings in dictionary object
            strids_indexes_list = df_index_source[df_index_source['STRING_ID'].isin(str_ids)].index.tolist()
        if len(gene_ids) > 0:
            geneids_indexes_list = df_index_source[df_index_source['Protein_Name'].isin(gene_ids)].index.tolist()
        indexes_list = strids_indexes_list + geneids_indexes_list
        indexes_list = [i for n, i in enumerate(indexes_list) if i not in indexes_list[:n]] #remove duplicates list comprehension
        dict_InputTable[compound][4] = indexes_list  # pos 4: indexes
    return dict_InputTable


# TODO: merge repeating sections of these validation functions into one.
def validate_str_ids(str_id_list):
    """
    Check for potential malformed str_ids.
    :param str_id_list: string of str_ids from user input
    :return: string array of str_id's, string array of warnings
    """
    warnings = []

    str_id_list = str_id_list.upper()  # Make comparison easier, as str_id's are stored in uppercase.
    if '\t' in str_id_list:
        warnings.append("String IDs contains tabs! This application expects comma delimited data.")

    str_id_array = str_id_list.split(',')
    stripped_gene_name_array = [s.strip() for s in str_id_array]

    for str_id in stripped_gene_name_array:
        if str_id != "" and str_id[:9] != '9606.ENSP':
            #warnings.append(f"String ID '{str_id}' does not have human protein preamble (9606.ENSP).")
            warnings.append(f"Warning: String ID '{str_id}' not recognized. A full list of human protein identifiers is available for download in the Data page.")
    return stripped_gene_name_array, warnings


def validate_gene_names(gene_names_list):
    """
    Check for potential malformed gene names.
    :param gene_names_list:
    :return: string array of gene names, string array of warnings
    """
    warnings = []
    gene_names_list = gene_names_list.upper()  # Gene names are always capitalized
    if '\t' in gene_names_list:
        warnings.append(f"Gene name not recognized. A full list of human protein identifiers is available for download in the Data page.")

    gene_name_array = gene_names_list.split(',')
    stripped_gene_name_array = [s.strip() for s in gene_name_array]

    return stripped_gene_name_array, warnings


def Btn_DetailedResultsFile(dict_inputTable):
    """
    Generate a text file to be downloaded by the user with the detailed results of all predictions in their input
    File should contain detailed information such as the warning/erros and results of each prediction.
    :param dict_inputTable: dictionary object representing the entire input from user and the additional info processed
    :return: no returns, but prompts user to save output fiile
    """
    for rowcount in range(0, len(dict_inputTable.keys())):
        m_pos_prob = dict_inputTable[rowcount][5]
        f_pos_prob = dict_inputTable[rowcount][6]
        if m_pos_prob >= 50 and f_pos_prob >= 50:
            prediction = "Positive class (can promote mice longevity) for both male and female mice"
        elif m_pos_prob >= 50:
            prediction = "Positive class (can promote mice longevity) for male mice but Negative class (cannot promote mice longevity) for female mice"
        elif f_pos_prob >= 50:
            prediction = "Positive class (can promote mice longevity) for female mice but Negative class (cannot promote mice longevity) for male mice"
        else:
            prediction = "Negative class (cannot promote mice longetivty) for both male and female mice"
        row_prediction_message = f'The model predicted that the compound {dict_inputTable[rowcount][0]} belongs to the {prediction}'
        row_warning_messages = dict_inputTable[rowcount][3]


def Btn_MakeTargetPredictions(targets_list):
    """
    Take input, validate the data, do processing on it, and return an output to be printed on the page.
    :param targets_list: table data
    :return: Result of processed data.
    """
    # Dictionary with all relevant information for each row (compound) in input table, some user-input and some processed
    dict_inputTable = {}
    # positions in dict: 0: "compound_name", 1: "str_ids", 2: "gene_ids", 3: "warnings", 4: "indexes", 5: "male_predprob", 6: "female_predprob"

    # First run-through of the table, reading each row and filling a dictionary object, to process data.
    # The Dict uses rowcount as key, to avoid issues with repeated compound names being used as key.
    rowcount = 0
    for row in targets_list:
        rowcount = rowcount + 1
        compound_name = row["compound"]
        if compound_name == "":
            compound_name = f'Row_{rowcount}'

        string_ids, str_id_warnings = validate_str_ids(row["str_ids"])
        gene_names, gene_name_warnings = validate_gene_names(row["gene_names"])

        warnings = str_id_warnings + gene_name_warnings
        dict_inputTable.setdefault(rowcount, [compound_name, string_ids, gene_names, warnings, [1], 0, 0])

    dict_inputTable = check_knownclasslabels(dict_inputTable, 3) # warning position is 3 for target predictions
    dict_inputTable = update_indexes_list(dict_inputTable) # get indexes of hits in the provided lists of ids and genes
    dict_inputTable = get_ensemble_predictions(dict_inputTable) # make predictions for each row of the table

    # Second run-through of table, writing outputs back on the web object
    rowcount = 0
    for row in targets_list:
        rowcount = rowcount + 1
        # positions in dict: 0: "compound_name", 1: "str_ids", 2: "gene_ids", 3: "warnings", 4: "indexes", 5: "male_predprob", 6: "female_predprob"
        print(f'Received compound: {dict_inputTable[rowcount][0]}')
        row["str_ids"] = dict_inputTable[rowcount][1]
        row["gene_names"] = dict_inputTable[rowcount][2]
        row["target_number"] = len(dict_inputTable[rowcount][4])
        row["m_prediction"] = dict_inputTable[rowcount][5]
        row["f_prediction"] = dict_inputTable[rowcount][6]

        if len(dict_inputTable[rowcount][3]) > 0:  # if there are any errors or warnings to print
            warning_string = ""
            for warning in dict_inputTable[rowcount][3]:
                warning_text = warning_string + warning + "\n"
            row["detailed_results"] = warning_text
        else:
            row["detailed_results"] = ""
    return targets_list

