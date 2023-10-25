#! /usr/bin/bash -eu

APP_HOME="/opt/iotuploader"
SETUP_DIR="${APP_HOME}/src/iot-uploader/setup"

echo "Install iot-uploader"

sudo mkdir -p ${APP_HOME}/data
sudo mkdir -p ${APP_HOME}/log
sudo chown -R iotuploader:iotuploader ${APP_HOME}

ENV_FILE="${APP_HOME}/.iotenv"
if [ ! -f ${ENV_FILE} ]; then
  echo "cp ${ENV_FILE}"
  sudo cp ${SETUP_DIR}/iotenv ${ENV_FILE}
  sudo chown iotuploader:iotuploader ${ENV_FILE}
  sudo chmod 600 ${ENV_FILE}
fi

SERVICE_FILE="/etc/systemd/system/iotuploader.service"
if [ ! -f ${SERVICE_FILE} ]; then
  echo "cp ${SERVICE_FILE}"
  sudo cp ${SRC_DIR}/setup/iotuploader.service ${SERVICE_FILE}
fi

echo "TODO:"
echo "  Configure ${ENV_FILE}"
echo "  sudo systemctl daemon-reload"
echo "  sudo systemctl start iopuploader.service"
echo "  sudo systemctl enable iopuploader.service"

