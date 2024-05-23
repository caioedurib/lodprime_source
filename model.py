'''
Code to train and save the classifier model. Reusable if the source dataset files happen to change in the future.
Saved model file (pickled) is loaded by classify_inputs.py
'''
import pickle
import random
import csv
from csv import reader
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from os import getenv
#pd.options.mode.chained_assignment = None #this can be a future issue, but is required to remove a warning every time

def train_RF_weighted(X_train, X_test, y_train, y_test, max_features):
    if np.all(y_test == 0) or np.all(y_test == 1):
        print('Constant test set error.')
        return 0, 0, 0, 0, 0, 0
    rf = RandomForestClassifier(n_estimators=500, class_weight='balanced_subsample', max_features=max_features, random_state=0)
    rf = rf.fit(X_train, y_train)
    y_pred = rf.predict(X_test)
    y_pred_prob = rf.predict_proba(X_test)
    TN, FP, FN, TP = confusion_matrix(y_test, y_pred).ravel()
    precision, recall, thresholds = precision_recall_curve(y_test, y_pred_prob[:, 1])
    auc_precision_recall = auc(recall, precision)
    AUC = roc_auc_score(y_test, y_pred_prob[:, 1])  # sample_weight parameter if there was manual weights
    return round(TP,2), round(TN,2), round(FP,2), round(FN,2), round(AUC,3), round(auc_precision_recall, 3)


#Returns the total weight of positive and negative examples in a dataframe (input is a dataframe filtered for a single compound)
def get_compound_weights(df):
    try:
        pos_weight = df[df['Class V1'] == 1].sum()
    except KeyError:
        pos_weight = 0
    try:
        neg_weight = df[df['Class V1'] == 0].sum()
    except KeyError:
        neg_weight = 0
    return pos_weight, neg_weight

#Find which of the folds in the CV should receive a compound, based on its pos/neg weights and the current weights in the folds
def find_best_fit(Folds_Dictionary, compound_pos_weight, compound_neg_weight, pos_class_fold_weight, neg_class_fold_weight):
    best_fit = "Fold1"
    min_overflow = 999
    for fold in Folds_Dictionary:
        fold_pos_weight = Folds_Dictionary[fold]["pos_weight"]
        fold_neg_weight = Folds_Dictionary[fold]["neg_weight"]
        pos_weight_overflow = (fold_pos_weight + compound_pos_weight) - pos_class_fold_weight
        neg_weight_overflow = (fold_neg_weight + compound_neg_weight) - neg_class_fold_weight
        if pos_weight_overflow < 0 and neg_weight_overflow < 0:
            return fold # compound completely fits inside the current fold, set it there
        elif pos_weight_overflow > 0 and neg_weight_overflow > 0:
            total_compound_overflow = pos_weight_overflow + neg_weight_overflow
            if total_compound_overflow < min_overflow:
                best_fit = fold
                min_overflow = total_compound_overflow
        elif pos_weight_overflow > 0:
            if pos_weight_overflow < min_overflow:
                best_fit = fold
                min_overflow = pos_weight_overflow
        else:
            if neg_weight_overflow < min_overflow:
                best_fit = fold
                min_overflow = neg_weight_overflow
    return best_fit


def create_Folds_Dictionary(df, random_seed, element_id_attribute):
    compounds_list = list(df[element_id_attribute].unique())
    random.seed(random_seed)
    random.shuffle(compounds_list) #shuffle list of compounds so that dataset order has no bearing on result
    n_instances = df.shape[0]
    positive_class_count = df['Class V1'].value_counts()[1]
    pos_class_fold_weight = round(positive_class_count/5, 2)
    neg_class_fold_weight = round(n_instances/5 - positive_class_count/5, 2)
    Folds_Dictionary = {"Fold1": {"pos_weight": 0, "neg_weight": 0, "compound_list": []},
            "Fold2": {"pos_weight": 0, "neg_weight": 0, "compound_list": []},
            "Fold3": {"pos_weight": 0, "neg_weight": 0, "compound_list": []},
            "Fold4": {"pos_weight": 0, "neg_weight": 0, "compound_list": []},
            "Fold5": {"pos_weight": 0, "neg_weight": 0, "compound_list": []}}

    for compound in compounds_list:
        compound_df = df[df[element_id_attribute] == compound]
        compound_neg_weight = compound_df[compound_df['Class V1'] == 0].shape[0]
        compound_pos_weight = compound_df[compound_df['Class V1'] == 1].shape[0]
        TargetFold = find_best_fit(Folds_Dictionary, compound_pos_weight, compound_neg_weight, pos_class_fold_weight, neg_class_fold_weight)
        Folds_Dictionary[TargetFold]["pos_weight"] = Folds_Dictionary[TargetFold]["pos_weight"] + compound_pos_weight
        Folds_Dictionary[TargetFold]["neg_weight"] = Folds_Dictionary[TargetFold]["neg_weight"] + compound_neg_weight
        Folds_Dictionary[TargetFold]["compound_list"].append(compound)
    return Folds_Dictionary



def print_metrics(TP_array, FP_array, TN_array, FN_array, AUC_array, PR_AUC_array, write_obj):
    global _cumulative_AUC
    print('Fold\tTP\tFP\tTN\tFN\tAUC\tPR_AUC')
    write_obj.write('Fold\tTP\tFP\tTN\tFN\tAUC\tPR_AUC\n')
    for i in range(0, 5):
        print(f'{i}\t{TP_array[i]}\t{FP_array[i]}\t{TN_array[i]}\t{FN_array[i]}\t{AUC_array[i]}\t{PR_AUC_array[i]}')
        write_obj.write(f'{i}\t{TP_array[i]}\t{FP_array[i]}\t{TN_array[i]}\t{FN_array[i]}\t{AUC_array[i]}\t{PR_AUC_array[i]}\n')
    print(f'Avg/Median\t{round(np.sum(TP_array),3)}\t{round(np.sum(FP_array),3)}\t{round(np.sum(TN_array),3)}\t{round(np.sum(FN_array),3)}\t{round(np.median(AUC_array),3)}\t{round(np.median(PR_AUC_array),3)}')
    write_obj.write(f'Avg/Median\t{round(np.sum(TP_array),3)}\t{round(np.sum(FP_array),3)}\t{round(np.sum(TN_array),3)}\t{round(np.sum(FN_array),3)}\t{round(np.median(AUC_array),3)}\t{round(np.median(PR_AUC_array),3)}\n')


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
    if 'Pubchem_id' in df:
        df = df.drop('Pubchem_id', 1)

    sex_values = {'M': 0, 'F': 1} #map string values into numeric values for sex variable
    df['sex'] = df['sex'].map(sex_values)
    if fixed_sex == 'M':
        print('Male-only dataset filter applied.')
        df = df.query('sex == 0')
        df = df.drop('sex', 1)
    elif fixed_sex == 'F':
        print('Female-only dataset filter applied.')
        df = df.query('sex == 1')
        df = df.drop('sex', 1)
    df = removeLowFrequencyFeatures(df, 3)
    return df


def removeInvalidInstances(df):
    df = df.reset_index()
    df = df.drop('Index', axis=1)
    features_only_df = df.copy(deep=True)  # create a copy of the df including only valid binary features
    features_only_df = features_only_df.drop('Class V1', axis=1)
    try:
        features_only_df = features_only_df.drop('sex', axis=1)
    except:
        print('Warning: sex feature not found when trying to remove it for removeLowFrequencyFeatures. Expected for M+F datasets.')
    try:
        features_only_df = features_only_df.drop('Compound_name', axis=1)
    except:
        print('Warning: Compound_name feature not found when trying to remove it for removeLowFrequencyFeatures.')
    drop_instances = []
    for key in range(len(features_only_df)):
        if features_only_df.iloc[key].sum() == 0:  # remove instances with only 0 values
            drop_instances.append(key)  # used reset_index to make sure it starts from 0, so no +1 needed here
    df = df.drop(drop_instances, axis=0)
    return df


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
                        df = df.drop(feature, 1)
                    elif number_instances - one_counts < threshold:
                        df = df.drop(feature, 1)
                else:
                    print(f'Warning: skipped {feature} for having values different from 0 and 1')
            except:
                print(f'Error on {feature} when trying to apply minimum threshold filter')
    return removeInvalidInstances(df)


def cross_validation(df, apply_filter, random_seed, write_obj):
    Compound_ID_feature = 'Compound_name'
    write_obj.write(f'Instances: {df.shape[0]} - Features: {df.shape[1]}')
    TP_array = []
    FP_array = []
    TN_array = []
    FN_array = []
    AUC_array = []
    PR_AUC_array = []
    Folds_Dictionary = create_Folds_Dictionary(df, random_seed, Compound_ID_feature)
    for fold in Folds_Dictionary:
        training_set = df.loc[~df[Compound_ID_feature].isin(Folds_Dictionary[fold]['compound_list'])]
        test_set = df.loc[df[Compound_ID_feature].isin(Folds_Dictionary[fold]['compound_list'])]
        training_set = training_set.drop([Compound_ID_feature], 1) # drop compound name feature
        test_set = test_set.drop([Compound_ID_feature], 1) # drop compound name feature
        X_train, X_test = training_set.iloc[:, :-1], test_set.iloc[:, :-1]
        y_train, y_test = training_set.iloc[:, -1], test_set.iloc[:, -1]
        max_features = "auto"  # default values
        TP, TN, FP, FN, AUC, PR_AUC = train_RF_weighted(X_train, X_test, y_train, y_test, max_features)
        TN_array.append(TN)
        FP_array.append(FP)
        FN_array.append(FN)
        TP_array.append(TP)
        AUC_array.append(AUC)
        PR_AUC_array.append(PR_AUC)
    print_metrics(TP_array, FP_array, TN_array, FN_array, AUC_array, PR_AUC_array, write_obj)
    return 1


def main(apply_filter, fixed_sex):
    username = getenv('username')
    input_file = f'C:/Users/{username}/Desktop/batch_input.txt' # scroll over lines of a file containing full paths to dataset files (.tsv)
    with open(input_file, 'r', encoding="utf8") as read_obj:
        csv_reader = csv.reader(read_obj, delimiter="\t", quoting=csv.QUOTE_NONE)
        for filepath in csv_reader:
            df = load_dataset(filepath[0], fixed_sex)  # if fixed_sex is M or F, this will filter the dataset to include only instances from that sex.
            dsname = get_dsname(filepath) # used to generate output name, hacky but fine for these experiments
            experiment_name = get_experiment_name(dsname, apply_filter, fixed_sex, experiment_type)
            print(f'Beggining experiment.\nConfig: {experiment_name}')
            output_file = f'C:/Users/{username}/OneDrive/OneDrive/PostDoc/Practice/Project 2 - Mus Musculus/Datasets/Results/V17 - GE fix/'+experiment_name+'.tsv'
            with open(output_file, 'w', encoding="utf8") as write_obj:
                cross_validation(df, apply_filter, 101, write_obj)
                write_obj.write('\n')
                cross_validation(df, apply_filter, 102, write_obj)
                write_obj.write('\n')
                cross_validation(df, apply_filter, 103, write_obj)
                write_obj.write('\n')
                cross_validation(df, apply_filter, 104, write_obj)
                write_obj.write('\n')
                cross_validation(df, apply_filter, 105, write_obj)
                write_obj.write('\n')
                cross_validation(df, apply_filter, 106, write_obj)
                write_obj.write('\n')
                cross_validation(df, apply_filter, 107, write_obj)
                write_obj.write('\n')
                cross_validation(df, apply_filter, 108, write_obj)
                write_obj.write('\n')
                cross_validation(df, apply_filter, 109, write_obj)
                write_obj.write('\n')
                cross_validation(df, apply_filter, 110, write_obj)
                write_obj.write('\n')
            write_obj.close()
    read_obj.close()
    return 0


if __name__ == "__main__":
    main(False, "all")  # False: NoFilter, False: skip grid search
    print('All done!')
'''    
    #test model
    from sklearn import ensemble
    from sklearn import datasets
    clf = ensemble.HistGradientBoostingClassifier()
    X, y = datasets.load_iris(return_X_y=True)
    clf.fit(X, y)
    
    #test pickle savefile
    with open("static/files/classifier.pkl", "wb") as f:
        pickle.dump(clf, f, protocol=pickle.HIGHEST_PROTOCOL)
'''