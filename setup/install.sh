#! /usr/bin/bash -eu

APP_HOME="/opt/iotuploader"
SETUP_DIR="${APP_HOME}/src/iot-uploader/setup"

echo "Install iot-uploader"

sudo yum install -y gcc
sudo amazon-linux-extras install -y nginx1 python3.8

sudo chown -R iotuploader:iotuploader ${APP_HOME}
sudo -u iotuploader mkdir -p ${APP_HOME}/data/images
sudo -u iotuploader mkdir -p ${APP_HOME}/data/overlay-images
sudo -u iotuploader mkdir -p ${APP_HOME}/data/raw-data
sudo -u iotuploader mkdir -p ${APP_HOME}/log
sudo -u iotuploader mkdir -p ${APP_HOME}/run
sudo -u iotuploader mkdir -p ${APP_HOME}/conf

cd ${APP_HOME}/
sudo -u iotuploader python3.8 -m venv .
sudo -u iotuploader ${APP_HOME}/bin/pip3 install -r ${SETUP_DIR}/requirements.txt

ENV_FILE="${APP_HOME}/.iotenv"
if [ ! -f ${ENV_FILE} ]; then
  echo "cp ${ENV_FILE}"
  sudo -u iotuploader cp ${SETUP_DIR}/iotenv ${ENV_FILE}
  sudo -u iotuploader chmod 600 ${ENV_FILE}
fi

CONF_FILE1="${APP_HOME}/conf/uploader.conf.py"
if [ ! -f ${CONF_FILE1} ]; then
  echo "cp ${CONF_FILE1}"
  sudo -u iotuploader cp ${SETUP_DIR}/uploader.conf.py ${CONF_FILE1}
fi

CONF_FILE2="${APP_HOME}/conf/tools.conf.py"
if [ ! -f ${CONF_FILE2} ]; then
  echo "cp ${CONF_FILE2}"
  sudo -u iotuploader cp ${SETUP_DIR}/tools.conf.py ${CONF_FILE2}
fi

SERVICE_FILE1="/etc/systemd/system/iot-uploader.service"
if [ ! -f ${SERVICE_FILE1} ]; then
  echo "cp ${SERVICE_FILE1}"
  sudo cp ${SETUP_DIR}/iot-uploader.service ${SERVICE_FILE1}
fi

SERVICE_FILE2="/etc/systemd/system/iot-uploader-tools.service"
if [ ! -f ${SERVICE_FILE2} ]; then
  echo "cp ${SERVICE_FILE2}"
  sudo cp ${SETUP_DIR}/iot-uploader-tools.service ${SERVICE_FILE2}
fi

NGINX_FILE="/etc/nginx/conf.d/iotuploader.conf"
if [ ! -f ${NGINX_FILE} ]; then
  echo "cp ${NGINX_FILE}"
  sudo cp ${SETUP_DIR}/nginx.iotuploader.conf ${NGINX_FILE}
fi

ROTATE_FILE="/etc/logrotate.d/iotuploader"
if [ ! -f ${ROTATE_FILE} ]; then
  echo "cp ${ROTATE_FILE}"
  sudo cp ${SETUP_DIR}/logrotate.iotuploader ${ROTATE_FILE}
fi

sudo systemctl start nginx
sudo systemctl enable nginx

echo "TODO:"
echo "  Configure ${ENV_FILE}"
echo "  sudo systemctl daemon-reload"
echo "  sudo systemctl start iot-uploader.service"
echo "  sudo systemctl enable iot-uploader.service"
echo "  sudo systemctl start iot-uploader-tools.service"
echo "  sudo systemctl enable iot-uploader-tools.service"

