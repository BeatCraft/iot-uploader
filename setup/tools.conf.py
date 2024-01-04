import multiprocessing
import os

bind = "127.0.0.1:8001"
workers = multiprocessing.cpu_count()
worker_class = "uvicorn.workers.UvicornWorker"
max_requests = 500
max_requests_jitter = 200
forwarded_allow_ips = "*"
timeout = 300

pidfile = "/opt/iotuploader/run/tools.pid"
accesslog = "/opt/iotuploader/log/tools-access.log"
errorlog = "/opt/iotuploader/log/tools-error.log"
loglevel = "info"

