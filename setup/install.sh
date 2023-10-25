#! /usr/bin/bash -eu

APP_HOME="/opt/iotuploader"
SETUP_DIR="${APP_HOME}/src/iot-uploader/setup"

echo "Install iot-uploader"

sudo yum install -y gcc

sudo chown -R iotuploader:iotuploader ${APP_HOME}
sudo -u iotuploader mkdir -p ${APP_HOME}/data
sudo -u iotuploader mkdir -p ${APP_HOME}/log
sudo -u iotuploader mkdir -p ${APP_HOME}/run

cd ${APP_HOME}/
sudo -u iotuploader python3 -m venv .
sudo -u iotuploader ${APP_HOME}/bin/pip3 install -r ${SETUP_DIR}/requirements.txt

ENV_FILE="${APP_HOME}/.iotenv"
if [ ! -f ${ENV_FILE} ]; then
  echo "cp ${ENV_FILE}"
  sudo -u iotuploader cp ${SETUP_DIR}/iotenv ${ENV_FILE}
  sudo -u iotuploader chmod 600 ${ENV_FILE}
fi

SERVICE_FILE="/etc/systemd/system/iotuploader.service"
if [ ! -f ${SERVICE_FILE} ]; then
  echo "cp ${SERVICE_FILE}"
  sudo cp ${SETUP_DIR}/iotuploader.service ${SERVICE_FILE}
fi

ROTATE_FILE="/etc/logrotate.d/iotuploader"
if [ ! -f ${ROTATE_FILE} ]; then
  echo "cp ${ROTATE_FILE}"
  sudo cp ${SETUP_DIR}/logrotate.iotuploader ${ROTATE_FILE}
fi

echo "TODO:"
echo "  Configure ${ENV_FILE}"
echo "  sudo systemctl daemon-reload"
echo "  sudo systemctl start iopuploader.service"
echo "  sudo systemctl enable iopuploader.service"

