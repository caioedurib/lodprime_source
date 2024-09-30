from pickle import load
from random import randint
import numpy as np
import pandas as pd
import sklearn

rows = [1, 2, 3]
dict_InputTable = {}
for row in rows:
    compound_name = "A"+str(row)
    if row == 1:
        dict_InputTable.setdefault(row, [compound_name, ["a", "b", "c", "9606.ENSP00000000233", "9606.ENSP00000000412"], ["M6PR", "FKBP4"], [""], [], 60, 100])
    elif row == 2:
        dict_InputTable.setdefault(row, [compound_name, ["9606.ENSP00000001146", "9606.ENSP00000002829", "9606.ENSP00000000412"], ["CFTR",], [""], [], 60, 100])
    elif row == 3:
        dict_InputTable.setdefault(row, [compound_name, [], ["CYP51A1", "BAIAP2L1", "TRAPPC6A", "AAAAAAAAAAAAA"], [""], [], 60, 100])

# positions in dict: 0: "compound_name", 1: "str_ids", 2: "gene_ids", 3: "warnings", 4: "indexes", 5: "male_predprob", 6: "female_predprob"
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

dict_InputTable = update_indexes_list(dict_InputTable)

#KEGG: model_NEKEGG_mixedsex
def ensemble_prediction_female_KEGG(filtered_df, model_name, sex, dict_InputTable):
    with open(f'internal_files/models/{model_name}.pkl', "rb") as f:  # add try-catch for file not found error
        rf_model = load(f)
        dict_KEGG_predictions = {}
        for row_number in dict_InputTable.keys():
            indexes_list = dict_InputTable[row_number][4]
            row_df_targets_source = filtered_df.loc[indexes_list]  # pos 4: indexes_list
            row_df_targets_source.loc['total'] = row_df_targets_source.sum()  # create row named 'total' with the sums of all column's values
            total_row = row_df_targets_source.loc['total']
            output_series = total_row[:] #transform into series
            output_series = np.clip(output_series, 0, 1)
            if sex == 'F':
                output_series[0] = 1
            prediction = rf_model.predict_proba(output_series.values.reshape(1, -1))  # .values to convert Series to array, then .reshape to make it into a dataframe object that can be passed as parameter to predict
            prediction = round(prediction[0][1]*100) # pos 5: male prediction
            dict_KEGG_predictions.setdefault(row_number, prediction)
    return dict_KEGG_predictions


# better version of applyThresholdFilter, replace if using it!
def removeLowFrequencyFeatures(df, threshold):
    if threshold < 0:
        return df
    number_instances = df.shape[0]
    for feature in df.columns:
        print(feature)
        try:
            mostFrequent = df[feature].value_counts(ascending=True)[0]
        except:
            mostFrequent = 0
        if number_instances - mostFrequent < threshold:
            df = df.drop(feature, 1)
    return df


# Receives a dictionary object with each row in input table, with their respective list of indexes
# fills out a male and female predprob value for each row (dictionary item) (use test_combinerows to create this)
def update_predictions(dict_InputTable):
    df_targets_source = pd.read_csv(f'internal_files/input_source/Annotation_Source - NE All Categories.tsv', sep='\t', index_col=0)
    #df_targets_source = removeLowFrequencyFeatures(df_targets_source, 3)
    #df_targets_source = df_targets_source.loc[:, ['sex', *df_targets_source.loc[:, 'WP4320':'WP5053'].columns]]  # Select columns between two columns plus sex column
    dict_predictions = ensemble_prediction_female_KEGG(df_targets_source, 'model_NEComponent_maleonly', 'F', dict_InputTable)
    for rownumber in dict_InputTable.keys():
        dict_InputTable[rownumber][5] = dict_predictions[rownumber]
    return dict_InputTable

dict_InputTable = update_predictions(dict_InputTable)

for row in rows:
    print(len(dict_InputTable[row][4]))
    print(dict_InputTable[row][4])
    print(dict_InputTable[row][5])