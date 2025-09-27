# steps/train.py
# 3. train model on the cleaned data and saving models
import os
import joblib
import yaml
from sklearn.preprocessing import StandardScaler, OneHotEncoder, MinMaxScaler
from sklearn.compose import ColumnTransformer
from imblearn.over_sampling import SMOTE # data aug: over-sampling for imbalance called "Synthetic Minority Oversampling Technique"
from imblearn.pipeline import Pipeline 
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.tree import DecisionTreeClassifier

class Trainer:
    def __init__(self):
        self.config = self.load_config()
        self.model_name = self.config['model']['name']
        self.model_params = self.config['model']['params']
        self.model_path = self.config['model']['store_path']
        self.pipeline = self.create_pipeline()

    def load_config(self):
        with open('config.yml', 'r') as config_file:
            return yaml.safe_load(config_file)
        
    def create_pipeline(self):
        # normalize data
        preprocessor = ColumnTransformer(transformers=[
            ('minmax', MinMaxScaler(), ['AnnualPremium']), # use minmax strategy (calculate: (value - min)/(max - min)) | don't reduce effect of outliers, but linearly scales them down into a fix range | # can use for decision trees, KNN, SVM (data is not follow normal distribution, best for minimal outlier or absent)
            ('standardize', StandardScaler(), ['Age','RegionID']), # use standardize strategy (scaling mean to 0 (centering) ) (calculate: (value - mean)/std) | ! sensitive t outlier | # can use for SVM, logistic regression, NN (assume data is normally distribute)
            ('onehot', OneHotEncoder(handle_unknown='ignore'), ['Gender', 'PastAccident']), # one hot to add value as column eg. male have male column 1 and female 0 | and female have 0 and 1
        ])
        # first oversample the minority class to have 10 percent the number of examples of the majority class
        smote = SMOTE(sampling_strategy=1.0) # new examples can be synthesized from the existing examples
        # can combine SMOTE with random undersampling of the majority class
        # e.g. use random undersampling to reduce the number of examples in the majority class to have 50 percent more
        # than the minority class
        # under = RandomUnderSampler(sampling_strategy=0.5)
        
        model_map = {
            'RandomForestClassifier': RandomForestClassifier,
            'DecisionTreeClassifier': DecisionTreeClassifier,
            'GradientBoostingClassifier': GradientBoostingClassifier
        }
    
        model_class = model_map[self.model_name]
        model = model_class(**self.model_params) # unpacks a dictionary of parameters, so each key-value pair in self.model_params becomes a named argument to the class constructor.

        pipeline = Pipeline([
            ('preprocessor', preprocessor),
            ('smote', smote),
            ('model', model)
        ])

        return pipeline

    def feature_target_separator(self, data):
        # separate X and y
        X = data.iloc[:, :-1]
        y = data.iloc[:, -1]
        return X, y

    def train_model(self, X_train, y_train):
        self.pipeline.fit(X_train, y_train)

    def save_model(self):
        model_file_path = os.path.join(self.model_path, 'model.pkl')
        joblib.dump(self.pipeline, model_file_path)
