import logging.config
import os
from logging.handlers import SocketHandler, TimedRotatingFileHandler
# from dotenv import load_env
from shared.config_loader import load_environment

# load_dotenv()
load_environment()

def setup_logging():
    LOG_PATH = os.getenv("LOG_PATH", "logs/ml-logger.log")
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    # USE_FILEBEAT = os.getenv("USE_FILEBEAT", "True")
    FILEBEAT_URI = os.getenv("FILEBEAT_URI", "")
    print(FILEBEAT_URI)

    handlers = {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "standard",
            "level": LOG_LEVEL
        },
        "file": {
            "class": "logging.handlers.TimedRotatingFileHandler",
            "formatter": "detailed",
            "filename": LOG_PATH,
            "when": "midnight",
            "backupCount": 7,
            "level": LOG_LEVEL
        }
    },

    if FILEBEAT_URI != "": 
        handlers["socket"] = {
            "class": "logging.handlers.SocketHandler",
            "level": LOG_LEVEL,
            "args": (FILEBEAT_URI,5000)
        }

    logging_config = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters":{
            "standard": {
                "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            },
            "detailed": {
                "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s | %(data)s"
            }
        },
        "handlers": handlers,
        "root": {
            "level": LOG_LEVEL,
            "handlers": list(handlers.keys())
        },
        "loggers": {
            "ml-logger": {
                "level": LOG_LEVEL,
                "handlers": list(handlers.keys()),
                "propagate": False
            },
            "uvicorn.access": {"propagate": True},
            "uvicorn.error": {"propagate": True}
        }
    }

    logging.config.dictConfig(logging_config)
    return logging.getLogger("ml-logger")
