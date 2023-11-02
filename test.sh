#! /usr/bin/bash -eu

source /opt/iotuploader/.iotenv
export DB_URL

/opt/iotuploader/bin/pytest -s $@ tests/

