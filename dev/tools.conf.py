import multiprocessing
import os

bind = "0.0.0.0:8101"
workers = 2
worker_class = "uvicorn.workers.UvicornWorker"
max_requests = 500
max_requests_jitter = 200

pidfile = "/opt/iotuploader/run/tools.pid"
accesslog = "/opt/iotuploader/log/tools-access.log"
errorlog = "/opt/iotuploader/log/tools-error.log"
loglevel = "debug"

