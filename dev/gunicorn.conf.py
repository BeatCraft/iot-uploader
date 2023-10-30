import multiprocessing
import os

bind = "0.0.0.0:8001"
workers =2
worker_class = "uvicorn.workers.UvicornWorker"
max_requests = 500
max_requests_jitter = 200

pidfile = "/opt/iotuploader/run/dev_iotuploader.pid"
accesslog = "/opt/iotuploader/log/dev_access.log"
errorlog = "/opt/iotuploader/log/dev_error.log"
loglevel = "debug"


