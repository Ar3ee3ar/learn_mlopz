# If this .py file doesn't work, then use a notebook to run it.
import joblib
import pandas as pd
from steps.clean import Cleaner
from evidently import Report, Dataset
from evidently.presets import DataDriftPreset, DataSummaryPreset
from evidently import DataDefinition
from evidently.sdk.models import PanelMetric
from evidently.sdk.panels import DashboardPanelPlot
from evidently.ui.workspace import CloudWorkspace

import warnings
import mlflow
import os
import numpy as np
from dotenv import load_dotenv

load_dotenv()

warnings.filterwarnings("ignore")


# # import mlflow model version 1
# import mlflow
# logged_model = f'runs:/{os.getenv("REGISTRY_ID")}/model'
# model = mlflow.pyfunc.load_model(logged_model)

# # OR import from models/
model = joblib.load('models/model.pkl')


# Loading data
reference = pd.read_csv("data/train.csv")
current = pd.read_csv("data/test.csv")
production = pd.read_csv("data/production.csv")


# Clean data
cleaner = Cleaner()
reference = cleaner.clean_data(reference)
reference['prediction'] = model.predict(reference.iloc[:, :-1])

current = cleaner.clean_data(current)
current['prediction'] = model.predict(current.iloc[:, :-1])

production = cleaner.clean_data(production)
production['prediction'] = model.predict(production.iloc[:, :-1])

reference['prediction'] = reference['prediction'].astype(np.int64)
reference['Result'] = reference['Result'].astype(np.int64)
current['prediction'] = current['prediction'].astype(np.int64)
current['Result'] = current['Result'].astype(np.int64)
production['prediction'] = production['prediction'].astype(np.int64)
production['Result'] = production['Result'].astype(np.int64)

# print(reference.head())

# Apply column mapping
target = 'Result'
prediction = 'prediction'
numerical_features = ['Age', 'AnnualPremium', 'HasDrivingLicense', 'RegionID', 'Switch']
categorical_features = ['Gender','PastAccident', 'prediction', 'Result']
column_mapping = DataDefinition()

# column_mapping.target = target
# column_mapping.prediction = prediction
column_mapping.numerical_columns = numerical_features
column_mapping.categorical_columns = categorical_features

reference_df = Dataset.from_pandas(
    pd.DataFrame(reference),
    data_definition=column_mapping
)

current_df = Dataset.from_pandas(
    pd.DataFrame(production),
    data_definition=column_mapping
)


# Data drift detaction part
data_drift_report = Report([
    DataDriftPreset(),
    DataSummaryPreset(),
    # TargetDriftPreset()
])
my_eval = data_drift_report.run(reference_data=reference_df, current_data=current_df)
# data_drift_report
# data_drift_report.json()
my_eval.save_html("test_drift_own.html")


# add dashboard
ws = CloudWorkspace(token=os.getenv('MONITOR_API_TOKEN'), url="https://app.evidently.cloud")
project = ws.get_project(os.getenv("MONITOR_PROJECT_ID"))
# or
# project = ws.create_project("My project name", org_id="YOUR_ORG_ID")
# project.description = "My project description"
# project.save()
# project.dashboard.add_panel(
#              DashboardPanelPlot(
#                 title="Dataset column drift",
#                 subtitle = "Share of drifted columns",
#                 size="half",
#                 values=[
#                     PanelMetric(
#                         legend="Share",
#                         metric="DriftedColumnsCount",
#                         metric_labels={"value_type": "share"} 
#                     ),
#                 ],
#                 plot_params={"plot_type": "line"},
#             ),
#             tab="Data Drift",
#         )
# project.dashboard.add_panel(
#              DashboardPanelPlot(
#                 title="Prediction drift",
#                 subtitle = """Drift in the prediction column ("class"), method: Jensen-Shannon distance""",
#                 size="half",
#                 values=[
#                     PanelMetric(
#                         legend="Drift score",
#                         metric="ValueDrift",
#                         metric_labels={"column": "prediction"} 
#                     ),
#                 ],
#                 plot_params={"plot_type": "bar"},
#             ),
#             tab="Data Drift",
#         )
ws.add_run(os.getenv("MONITOR_PROJECT_ID"), my_eval, include_data=False)