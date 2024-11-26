'''
Code to train and save the classifier model. Reusable if the source dataset files happen to change in the future.
Saved model file (pickled) is loaded by classify_inputs.py
'''

import pickle
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier

def removeLowFrequencyFeatures(df, threshold):
    if threshold < 0:
        return df
    number_instances = df.shape[0]
    for feature in df:
        if feature != 'Compound_name':
            try:
                if df[feature].isin([0, 1]).all():
                    zero_counts = (df[feature] == 0).sum()
                    one_counts = (df[feature] == 1).sum()
                    if number_instances - zero_counts < threshold:
                        df = df.drop(feature, axis=1)
                    elif number_instances - one_counts < threshold:
                        df = df.drop(feature, axis=1)
                else:
                    print(f'Warning: skipped {feature} for having values different from 0 and 1')
            except:
                print(f'Error on {feature} when trying to apply minimum threshold filter')
    return removeInvalidInstances(df)


def removeInvalidInstances(df):
    df = df.reset_index()
    df = df.drop('Index', axis=1)
    features_only_df = df.copy(deep=True)  # create a copy of the df including only valid binary features
    features_only_df = features_only_df.drop('class', axis=1)
    try:
        features_only_df = features_only_df.drop('sex', axis=1)
    except:
        print('Warning: sex feature not found when trying to remove it for removeLowFrequencyFeatures. Expected for M+F datasets.')
    drop_instances = []
    for key in range(len(features_only_df)):
        if features_only_df.iloc[key].sum() == 0:  # remove instances with only 0 values
            drop_instances.append(key)  # used reset_index to make sure it starts from 0, so no +1 needed here
    df = df.drop(drop_instances, axis=0)
    return df


# TODO: check columns of input datasets to make sure features and class are correctly placed/removed
def load_dataset(path, fixed_sex):
    df = pd.read_csv(path, na_values='?', sep='\t', encoding='unicode_escape', index_col=0)
    #remove possible header features not used in internal code
    if 'Full_Targets_List' in df:
        df = df.drop('Full_Targets_List', 1)
    if 'Number_of_Targets' in df:
        df = df.drop('Number_of_Targets', 1)
    if 'LINCS_ID' in df:
        df = df.drop('LINCS_ID', 1)
    if 'Pubchem_ID' in df:
        df = df.drop('Pubchem_ID', 1)
    if 'Compound_name' in df:
        df = df.drop('Compound_name', axis=1)

    sex_values = {'M': 0, 'F': 1} #map string values into numeric values for sex variable
    df['sex'] = df['sex'].map(sex_values)
    if fixed_sex == 'M':
        print('Male-only dataset filter applied.')
        df = df.query('sex == 0')
        df = df.drop('sex', axis=1)
    elif fixed_sex == 'F':
        print('Female-only dataset filter applied.')
        df = df.query('sex == 1')
        df = df.drop('sex', axis=1)
    df = removeLowFrequencyFeatures(df, 3)
    return df

# Receives a filepath for a dataset file, trains a model from it and pickles it, saving it with the desired filename.
# Includes sex_filter option for loading only data from a specific type of instance (male, female, all)

def train_and_save_model(filepath, sex_filter, classifier_savename):
    print(f'Training: {classifier_savename}')
    df = load_dataset(filepath, sex_filter)  # if fixed_sex is M or F, this will filter the dataset to include only instances from that sex.
    rf = RandomForestClassifier(n_estimators=500, class_weight='balanced_subsample', random_state=0)
    X = df.iloc[:, :-1]
    y = df.iloc[:, -1]
    rf = rf.fit(X.values, y)  # using X.values removes a warning about feature names in X
    with open(f"internal_files/models/{classifier_savename}.pkl", "wb") as f:
        pickle.dump(rf, f, protocol=pickle.HIGHEST_PROTOCOL)
    print(f'Model saved: {classifier_savename}')

# loads a dataset, trains a model using all its data and tests saving it to a file, loading the model from the file
# and using it to make a prediction on dummy data.
def test_model():
    dataset_name = 'MM Molecular Fingerprints dataset.tsv'
    df = load_dataset(f'static/files/datasets/{dataset_name}', "both")  # if fixed_sex is M or F, this will filter the dataset to include only instances from that sex.
    X = df.iloc[:, :-1]
    print(df.shape)
    print(df.head())
    classifier_name = 'model_Fingerprints_mixedsex'
    #train_and_save_model(f'static/files/datasets/{dataset_name}', 'M', classifier_name)
    with open(f"internal_files/models/{classifier_name}.pkl", "rb") as f:
        rf_model = pickle.load(f)
        list_predictions = []
        test_entry = [np.zeros(len(X.columns))]   # this will be a list of lists, each with len(X.columns) elements
        y_pred_prob = rf_model.predict_proba(test_entry)
        list_pred = y_pred_prob.tolist()
        for i in range(0, len(list_pred)):
            list_predictions.append(list(list_pred[i])[1])
            print(list_predictions)


if __name__ == "__main__":
    #test_model()  # False: NoFilter, False: skip grid search
    filepath = 'static/files/datasets/MM Molecular Fingerprints dataset.tsv'
    classifier_name = 'model_Fingerprints_maleonly'
    train_and_save_model(filepath, 'M', classifier_name)
    print('All done!')

'''
    NOTE: Inputs will NOT have a sex features in male-only models, and when using mixed-sex models we only need to generate F instances (M predictions should come from male-only models)
Changes agreeded uppon during meeting with Aleksey on 06/06/24:
    - No need for home page, straight to input (I disagree. To check with Alex) 
    - Load targets from DrugBank file, user's input of drug name should be enough to autocomplete targets
    - Use DrugBank synonym's file to get the correct drug's code/targets
        - recommending pubchemid from name
    - Add a new button which combines selected compounds into a new entry, merging their target lists
        - There should be a warning acknowledging if some of the selected entries currently has no targets
    - Separate option for classifying an entry using the Molecular Fingerprints models
    - Show outputs from each model separately (mixed-sex and male-only) - two male predictions? TBD
        - male-only and mixed-sex both on only target models
    - For the ensemble result, instead of majority voting, just average score and show each prediction separately
'''