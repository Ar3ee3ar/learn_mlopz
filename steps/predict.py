# steps/predict.py
# 4. evaluate model performance
import os
import joblib
from sklearn.metrics import accuracy_score, classification_report, roc_auc_score

class Predictor:
    def __init__(self):
        self.model_path = self.load_config()['model']['store_path']
        self.pipeline = self.load_model()

    def load_config(self):
        import yaml
        with open('config.yml', 'r') as config_file:
            return yaml.safe_load(config_file)
        
    def load_model(self):
        model_file_path = os.path.join(self.model_path, 'model.pkl')
        return joblib.load(model_file_path)

    def feature_target_separator(self, data):
        X = data.iloc[:, :-1]
        y = data.iloc[:, -1]
        return X, y

    def evaluate_model(self, X_test, y_test):
        y_pred = self.pipeline.predict(X_test)
        accuracy = accuracy_score(y_test, y_pred)
        class_report = classification_report(y_test, y_pred)
        # ROC curve(aoc) [interested positive class (interested class)] summarize trad-off between 
        #   True Positive Rate <same as Recall> [how good the model is at predicting the positive class when actual class is positive {how model correctly classify our interested class (P)}] (TPR{hit rate, sensitivity} - y-axis | TP/(TP+FN)) 
        #   and 
        #   False Positive Rate [how often a positive class is predicted when actual class is negative {inverted specificity(inverted of how model correctly classify uninterested class (N))}]
        #       (FPR{false alarm rate} - x-axis | FP/(FP+TN) or 1-[TN/(TN+FP)])
        # area under ROC curve(auc) can tell
        #   - smaller value on x-axis mean lower FP and higher TN # personal conclude need to be checked -> [model good at classify negative class as negative but also have prob. to classify positive class as negative (FN)]
        #   - larger value on y-axis mean higher TP and lower FN # personal conclude need to be checked -> [model good at classify positive class as positive but also have prob. to classify negative class as positive (FP)]
        # appropriate when observations are balanced between each class  
        roc_auc = roc_auc_score(y_test, y_pred)
        return accuracy, class_report, roc_auc
    
# Note: more evaluate class
# - Precision-Recall curves summarize the trade-off between TPR and the positive predictive value
# appropriate for the imbalanced datasets
