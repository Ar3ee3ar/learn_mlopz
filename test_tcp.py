import logging
from logging.handlers import SocketHandler, TimedRotatingFileHandler

logger = logging.getLogger('abc-logger')
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s | %(data)s')
socket_handler = SocketHandler('localhost', 5000)
#file_handler = TimedRotatingFileHandler(LOG_PATH, when="midnight", backupCount=7) # delete old log when backupcount = 0 (1 count = 1 rotating('when' or 'interval')) (delete every 7 day)
# # handler = logging.FileHandler("logs/ml-logger.log", mode='a')
socket_handler.setFormatter(formatter)
# file_handler.setFormatter(formatter)
logger.addHandler(socket_handler)
#logger.addHandler(file_handler)
logger.setLevel(logging.INFO)

logger.info("test tcp", extra={"data":{"check_tcp":True, "name":"Mike Johnson"}})