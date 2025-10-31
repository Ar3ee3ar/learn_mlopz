import mlflow
from dotenv import load_dotenv
import os

load_dotenv()

MLFLOW_REGISTRY_URI = os.getenv('MLFLOW_REGISTRY_URI')
mlflow.set_registry_uri(MLFLOW_REGISTRY_URI)

client = mlflow.MlfllowClient()

def set_registered_alias(model_name, alias_name, model_version):
    # Set the model alias
    client.set_registered_model_alias(model_name, alias_name, model_version)

def get_registered_alias(model_name, alias):
    # get a model version by alias
    client.get_model_version_by_alias(model_name, alias)

def managed_alias(model_name, **kwargs):
    # create "champion" alias for version 1 of model "example-model"
    # Set the model alias
    client.set_registered_model_alias(model_name, kwargs['alias'], kwargs['version'])

    # reassign the "Champion" alias to version 2
    # client.set_registered_model_alias(model_name, "Champion", 2)

    # get a model version by alias
    # client.get_model_version_by_alias(model_name, "Champion")

    # delete the alias
    # client.delete_registered_model_alias(model_name, "Champion")

def managed_tag(model_name,**kwargs):
    # Set registered model tag
    # client.set_registered_model_tag(model_name, "task", "classification")

    # Delete registered model tag
    # client.delete_registered_model_tag(model_name, "task")

    # Set model version tag
    client.set_model_version_tag(model_name, kwargs['version'], kwargs['key'], kwargs['value'])

    # Delete model version tag
    # client.delete_model_version_tag(model_name, "1", "validation_status")

def promote_model():
    client.copy_model_version(
        src_model_uri="models:/regression-model-staging@candidate",
        dst_name="regression-model-production",
    )

def manage_description():
    client.update_model_version(
        name="sk-learn-random-forest-reg-model",
        version=1,
        description="This model version is a scikit-learn random forest containing 100 decision trees",
    )

def main():
    model_name = "insurance_model"
    alias_name = "champion" # pr "challenger"
    model_version = 4
    set_registered_alias(model_name, alias_name, model_version)