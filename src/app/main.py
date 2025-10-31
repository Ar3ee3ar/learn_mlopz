# use model registry
from fastapi import FastAPI
from pydantic import BaseModel
import pandas as pd
import joblib
import mlflow
from dotenv import load_dotenv
import os
# logging library
import logging
# import ecs_logging
import time
from logging.handlers import SocketHandler, TimedRotatingFileHandler
import json
from app.model_loader import load_model_from_registered
# from app.logging_config import setup_logging
from shared.config_loader import load_environment

# load_dotenv()
load_environment()

# logger = setup_logging()
LOG_PATH = os.getenv("LOG_PATH", "logs/ml-logger.log")
logger = logging.getLogger('ml-logger')
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s | %(data)s')
# socket_handler = SocketHandler('127.0.0.1', 5000)
file_handler = TimedRotatingFileHandler(LOG_PATH, when="midnight", backupCount=7) # delete old log when backupcount = 0 (1 count = 1 rotating('when' or 'interval')) (delete every 7 day)
console_handler = logging.StreamHandler()
# # handler = logging.FileHandler("logs/ml-logger.log", mode='a')
# socket_handler.setFormatter(formatter)
file_handler.setFormatter(formatter)
console_handler.setFormatter(formatter)
# logger.addHandler(socket_handler)
logger.addHandler(file_handler)
logger.addHandler(console_handler)
logger.setLevel(logging.INFO)
# logger.setLevel(logging.DEBUG)
# logger = logging.getLogger("ml-logger")
# logger.setLevel(logging.INFO)

# Load model once at startuo
MODEL = None
MODEL_VERSION = None

# logged_model = f'runs:/{os.getenv("REGISTRY_ID")}/model'

app = FastAPI()

class InputData(BaseModel):
    Gender: str
    Age: float
    HasDrivingLicense: float
    RegionID: float
    Switch: float
    PastAccident: str
    AnnualPremium: float

# class LogstashSockerHandler(SocketHandler):
#     def emit(self, record):
#         try:
#             # print(record)
#             #print(self.format(record))
#             #message = json.loads(self.format(record))
#             #print(type(message))
#             #print(message)
#             log_entry = self.format(record)
#             message = getattr(record, "data", None)
#             log_entry_write = {
#             "message": log_entry,
#             "timestamp": time.strftime('%Y-%m-%dT%H:%M:%S%z'),
#             "features": message['features'],
#             "predictions": message['predictions'],
#             "confidence": message['confidence'],
#             "latency_ms": message['latency_ms']
#             }
#             # print(json.dumps(log_entry).encode('utf-8') + b'\n')
#             self.send(json.dumps(log_entry_write).encode('utf-8') + b'\n')
#         except:
#             self.handleError(record)
         

# model = joblib.load('models/model.pkl')
# model = mlflow.sklearn.load_model(logged_model)
# logstash_host = 'http://elasticsearch'
# logstash_port = 9200
# # Add the custom handler to the logger
# handler = LogstashSockerHandler(logstash_host, logstash_port)
# logger.addHandler(handler)

@app.on_event("startup")
async def startup_event():
    global MODEL, MODEL_VERSION
    try:
        MODEL, MODEL_VERSION = load_model_from_registered()
    except Exception as e:
        log_entry = {
            "error":"model_loaded_failed",
            "exception":str(e),
            "request_id":"startup",
            "model_version":MODEL_VERSION
        }
        logger.error("System activity", extra={"data": json.dumps(log_entry)})
        


@app.get("/")
async def read_root():
    logging.info("Health check OK")
    return {"health_check": "OK", "model_version": 1}

@app.post("/predict")
async def predict(input_data: InputData):
    global MODEL, MODEL_VERSION
    pred = None
    conf = None
    if MODEL is not None:
        df = pd.DataFrame([input_data.model_dump().values()], 
                            columns=input_data.model_dump().keys())
        start_time = time.time()
        try:
            pred = MODEL.predict(df)
            conf = MODEL.predict_proba(df)
            print(pred,' ',conf)
            pred = int(pred[0])
            conf = max(conf[0])
            # print(log_entry)
        except Exception as e:
            logger.error("System activity", extra={"data": json.dumps({
                "error": "prediction_failed",
                "exception": str(e),
                "features": input_data.model_dump(),
            })})

        log_entry = {
            "features": input_data.model_dump(),
            "predictions": pred,
            "confidence": conf,
            "latency_ms": (time.time() - start_time)
        }
        logger.info("User activity", extra={"data": json.dumps(log_entry)})

        return {"predicted_class": pred}
    else:
        return {"error": "model not loaded"}



