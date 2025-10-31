import logging
import yaml
import mlflow
import mlflow.sklearn
from mlflow.models import infer_signature
from training.steps.ingest import Ingestion
from training.steps.clean import Cleaner
from training.steps.train import Trainer
from training.steps.predict import Predictor
from sklearn.metrics import classification_report
import dagshub
import os
import argparse

# Set up logging
logging.basicConfig(level=logging.INFO,format='%(asctime)s:%(levelname)s:%(message)s')
# setup dagshub tracking
dagshub.init(repo_owner='Ar3ee3ar', repo_name='mlopz-aws', mlflow=True)

def _argparse():
    # print('parsing args...')
    parser = argparse.ArgumentParser()
    parser.add_argument("--ttype", "-train_type",type=str, default='manual-retrain', help="tag to classify sources train")
    parser.add_argument("--mname", "-model_name",type=str, default='insurance_model_dev', help="model name to classify stage of model")
    parser.add_argument("--train_path", "-train_path",type=str, default='data/train.csv', help="path to training data")
    parser.add_argument("--test_path", "-test_path",type=str, default='data/test.csv', help="path to testing data")
    arg = parser.parse_args()
    return arg

def main():
    # Load data
    ingestion = Ingestion()
    train, test = ingestion.load_data()
    logging.info("Data ingestion completed successfully")

    # Clean data
    cleaner = Cleaner()
    train_data = cleaner.clean_data(train)
    test_data = cleaner.clean_data(test)
    logging.info("Data cleaning completed successfully")

    # Prepare and train model
    trainer = Trainer()
    X_train, y_train = trainer.feature_target_separator(train_data)
    trainer.train_model(X_train, y_train)
    trainer.save_model()
    logging.info("Model training completed successfully")

    # Evaluate model
    predictor = Predictor()
    X_test, y_test = predictor.feature_target_separator(test_data)
    accuracy, class_report, roc_auc_score = predictor.evaluate_model(X_test, y_test)
    logging.info("Model evaluation completed successfully")
    
    # Print evaluation results
    print("\n============= Model Evaluation Results ==============")
    print(f"Model: {trainer.model_name}")
    print(f"Accuracy Score: {accuracy:.4f}, ROC AUC Score: {roc_auc_score:.4f}")
    print(f"\n{class_report}")
    print("=====================================================\n")


def train_with_mlflow(**kwargs):
    train_path = ''
    test_path = ''
    try:
        try:
            model_name = kwargs['model_attr'].mname
            source = kwargs['model_attr'].ttype
            train_path = kwargs['model_attr'].train_path
            test_path = kwargs['model_attr'].test_path
        except KeyError:
            model_name = kwargs['model_name']
            source = kwargs['source']
            train_path = kwargs['train_path']
            test_path = kwargs['test_path']
    except KeyError:
        tmp_key = str([i for i in list(kwargs.keys())])
        logging.error(f"Receive unknown key : {tmp_key}")
        raise KeyError(f"Receive unknown key : {tmp_key}")
    except Exception as e:
        logging.error(e)
        raise Exception(e)

    with open('configs/config.yml', 'r') as file:
        config = yaml.safe_load(file)

    # set tracking url
    MLFLOW_TRACKING_URI = os.getenv('MLFLOW_TRACKING_URI')
    mlflow.set_tracking_uri(MLFLOW_TRACKING_URI)

    # mlflow.set_experiment("Model Training Experiment")
    
    with mlflow.start_run() as run:
        # Load data
        if train_path != '':
            ingestion = Ingestion(train_path, test_path)
        else:
            ingestion = Ingestion()
        train, test = ingestion.load_data()
        logging.info("Data ingestion completed successfully")

        # Clean data
        cleaner = Cleaner()
        train_data = cleaner.clean_data(train)
        test_data = cleaner.clean_data(test)
        logging.info("Data cleaning completed successfully")

        # Prepare and train model
        trainer = Trainer()
        X_train, y_train = trainer.feature_target_separator(train_data)
        trainer.train_model(X_train, y_train)
        trainer.save_model()
        logging.info("Model training completed successfully")
        
        # Evaluate model
        predictor = Predictor()
        X_test, y_test = predictor.feature_target_separator(test_data)
        accuracy, class_report, roc_auc_score = predictor.evaluate_model(X_test, y_test)
        report = classification_report(y_test, trainer.pipeline.predict(X_test), output_dict=True) # build text report (evaluate model using train pipeline)
        logging.info("Model evaluation completed successfully")

        # Infer the model signature
        # print(X_test.iloc[0, :])
        y_pred = trainer.pipeline.predict(X_test.iloc[[0]])
        signature = infer_signature(X_test.iloc[[0]], y_pred)
        
        # Tags 
        mlflow.set_tag('Model developer', 'prsdm')
        mlflow.set_tag('preprocessing', 'OneHotEncoder, Standard Scaler, and MinMax Scaler')
        mlflow.set_tag('source', source)
        
        # Log metrics
        model_params = config['model']['params']
        mlflow.log_params(model_params)
        mlflow.log_metric("accuracy", accuracy)
        mlflow.log_metric("roc", roc_auc_score)
        mlflow.log_metric('precision', report['weighted avg']['precision'])
        mlflow.log_metric('recall', report['weighted avg']['recall'])
        mlflow.sklearn.log_model(trainer.pipeline, "model", signature=signature) # logging training pipeline with name "model"
                
        # Register the model
        # model_name = kwargs['model_attr'].mname #"insurance_model"  # registered model name
        model_uri = f"runs:/{run.info.run_id}/model"
        mlflow.register_model(model_uri, 
                              model_name,
                              tags = {'source': source})

        logging.info("MLflow tracking completed successfully")

        # Print evaluation results
        print("\n============= Model Evaluation Results ==============")
        print(f"Model: {trainer.model_name}")
        print(f"Accuracy Score: {accuracy:.4f}, ROC AUC Score: {roc_auc_score:.4f}")
        print(f"\n{class_report}")
        print("=====================================================\n")
        
if __name__ == "__main__":
    # main()
    args = _argparse()
    train_with_mlflow(model_attr = args)
    # for calling via function
    # train_with_mlflow(model_name='insurance_model', source='manual-retrain')
