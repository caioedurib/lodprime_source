from pickle import load
from random import randint
import numpy as np
import pandas as pd

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


def Input_Make_Predictions(input_string):
    with open("static/files/models/classifier.pkl", "rb") as f:  # add try-catch for file not found error
        rf_model = load(f)
    list_predictions = []
    for compound_name, targets_list in input_string:
        target_list, tl_warnings = validate_input(target_list)
        instance = create_instance(targets_list)
        rf_model.predict(X[0:1])  # replace by instance when model is ready
    return -1


def validate_input(target_list):
    validated_targets_list = target_list
    tl_warnings = ""  # add a warning for each target that is not present in the dataset, to be shown with output
    return validated_targets_list, tl_warnings


def create_instance(compound_name, str_ids, gene_names, df_targets_source):
    str_ids_df = []
    gene_names_df = []
    if str_ids.__len__>0:
        str_ids_df = df_targets_source['STRING_ID'].isin(str_ids)
        if str_ids_df.shape[1] == str_ids.__len__:
            print('All STR IDs selected succesfully')
    if gene_names.__len__ > 0:
        gene_names_df = df_targets_source['GeneName'].isin(gene_names)
        if gene_names_df.shape[1] == gene_names.__len__:
            print('All Gene names selected succesfully')
    instance_source_df = pd.concat([str_ids_df, gene_names_df])
    print(str_ids_df.shape)
    print(gene_names_df.shape)
    print(instance_source_df.shape)

    total = instance_source_df.sum(axis=1)
    print(total)

    return -1


def test_combinerows():
    df_targets_source = pd.read_csv(f'internal_files/input_source/protein source sample.tsv', sep='\t', index_col=0)
    print(df_targets_source.shape)
    df_targets_source = df_targets_source.loc[df_targets_source['GeneName'].isin(['G1', 'G2'])]
    print(df_targets_source.shape)
    df_targets_source.loc['total'] = df_targets_source.sum()
    total_row = df_targets_source.loc['total']
    output_series = total_row[3:-1]
    print(type(output_series))
    output_series = np.clip(output_series, 0, 1)
    for a in output_series:
        print(a)

def input_placeholder(targets_list):
    """
    Take input, do processing on it, and return a string to be printed on the page.
    :param targets_list: table data
    :return: Result of processed data.
    """
    # TODO: May want to add some catch statements here in case of malformed data input
    # Get number of targets for each compound.

    df_targets_source = pd.read_csv(f'internal_files/input_source/protein source sample.tsv', sep='\t', index_col=0)

    for row in targets_list:
        compound_name = row["compound"]
        string_ids = row["str_ids"]
        gene_names = row["gene_names"]

        pos_prob = randint(1, 100)
        if pos_prob >= 50:
            prediction = "Positive class (can promote mice longevity)"
        else:
            prediction = "Negative class (cannot promote mice longevity)"
        print(f'Received compound: {compound_name}, ID: {row["str_ids"]}, Gene Names: {row["gene_names"]}')
        row["target_number"] = len(row["gene_names"])
        row["prediction"] = pos_prob
        if compound_name!="":
            row["detailed_results"] = f'The model predicted that the compound {str(compound_name)} belongs to the {prediction}, for male mice.'
        else:
            row["detailed_results"] = f'The model predicted that the unnamed compound with Targets List: {str(row["targets"])} belongs to the {prediction}, for male mice.'

    return targets_list

if __name__ == "__main__":
    test_combinerows()