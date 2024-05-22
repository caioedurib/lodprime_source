from pickle import load

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
    with open("files/classifier.pkl", "rb") as f:  # add try-catch for file not found error
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


def create_instance(target_list):
    return ""
