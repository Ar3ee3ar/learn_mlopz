import mlflow
import os
from pprint import pprint
from dotenv import load_dotenv
import pandas as pd

load_dotenv()

MLFLOW_TRACKING_URI = os.getenv('MLFLOW_TRACKING_URI')
print(os.getenv('MLFLOW_TRACKING_URI'))
name = "insurance_model"
tag = 'manual-retrain'
alias = 'champion'
input = {"Gender": "Male", "Age": 22, "HasDrivingLicense": 1, "RegionID": 32.0, "Switch": 0, "PastAccident": "Yes", "AnnualPremium": 1030.0}
data = pd.DataFrame([list(input.values())],columns=list(input.keys()))
infer_data = data.iloc[[0]]
print((data.iloc[[0]]).head)
print(data.head)
# print(data)
mlflow.set_tracking_uri(MLFLOW_TRACKING_URI)

client = mlflow.tracking.MlflowClient()

# search registered model
selected_model = [client.search_model_versions(filter_string=f"name='{name}'",), # can use like SQL  e.g. AND tags.source='{tag}' | order_by=['last_updated_timestamp DESC'] # DESC 4->1 ASC(default) 1->4
                  client.search_registered_models(filter_string=f"name='{name}'"),
                  client.search_experiments(order_by=["name"])]
for rm in selected_model[0]:
    pprint(dict(rm), indent=4)
    # print(dict(dict(rm)['latest_versions'][0])['source']) # format for search_registered_models
    print(dict(rm)['source']) # format for search_model_version

# get model by version
# model = mlflow.pyfunc.load_model(model_uri=f"models:/{name}/{4}")
# print(selected_model[1][0])
# get model by alias
# model = mlflow.pyfunc.load_model(f"models:/{name}@{alias}")

model = mlflow.pyfunc.load_model(model_uri=f"{dict(selected_model[0][0])['source']}") # format for search_model_version
# # model = mlflow.pyfunc.load_model(model_uri=f"{dict(dict(selected_model[1][0])['latest_versions'][0])['source']}") # format for search_registered_model
pred = model.predict(infer_data)
print(pred)