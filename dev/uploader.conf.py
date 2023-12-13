import multiprocessing
import os

bind = "127.0.0.1:8100"
workers = 2
worker_class = "uvicorn.workers.UvicornWorker"
max_requests = 500
max_requests_jitter = 200
timeout = 1200
forwarded_allow_ips = "*"

pidfile = "/opt/iotuploader/run/uploader.pid"
accesslog = "/opt/iotuploader/log/access.log"
errorlog = "/opt/iotuploader/log/error.log"
loglevel = "debug"

