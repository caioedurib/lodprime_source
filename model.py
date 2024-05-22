'''
Code to train and save the classifier model. Reusable if the source dataset files happen to change in the future.
Saved model file (pickled) is loaded by classify_inputs.py
'''

#test model
from sklearn import ensemble
from sklearn import datasets
clf = ensemble.HistGradientBoostingClassifier()
X, y = datasets.load_iris(return_X_y=True)
clf.fit(X, y)

#test pickle savefile
import pickle
with open("static/files/classifier.pkl", "wb") as f:
    pickle.dump(clf, f, protocol=pickle.HIGHEST_PROTOCOL)