import mlflow
import mlflow.sklearn
import os
import tempfile
from dotenv import load_dotenv

load_dotenv()

MLFLOW_TRACKING_URI = os.getenv('MLFLOW_TRACKING_URI')
MLFLOW_MODEL_NAME = os.getenv('MLFLOW_MODEL_NAME', 'mymodel')
MLFLOW_ALIAS = os.getenv('MLFLOW_ALIAS', 'champion')

mlflow.set_tracking_uri(MLFLOW_TRACKING_URI)

def load_model_from_registered(name=MLFLOW_MODEL_NAME, alias=MLFLOW_ALIAS):
    # Get model using alias as referenced
    try:
        try:
            model = mlflow.sklearn.load_model(f"models:/{name}@{alias}")
            return model, f"{MLFLOW_MODEL_NAME}:champion"
        except:
            client = mlflow.tracking.MlflowClient()
            tag = 'pass'
            selected_model = client.search_model_versions(filter_string=f"name='{name}' AND tags.validation_status='{tag}'")
            model = mlflow.sklearn.load_model(model_uri=f"{dict(selected_model[0][0])['source']}") # format for search_model_version
            return model, f"{MLFLOW_MODEL_NAME}:{dict(selected_model[0][0])['version']}"
    except:
        raise RuntimeError(f"No model found in {name}")
