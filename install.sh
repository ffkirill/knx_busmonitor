#!/usr/bin/env bash
cd ..
sudo -u busmonitor virtualenv env --no-site-packages
sudo -u busmonitor env/bin/pip install -r knx_busmonitor/requirements.txt
cd knx_busmonitor/eibd_stack
sudo -u busmonitor ../../env/bin/python setup.py build
cd ..
sudo -u busmonitor cp eibd_stack/build/lib.linux-*/eibd_stack.so .
ln -sf ${PWD}/busmonitor.supervisor.conf /etc/supervisor/conf.d/busmonitor.conf
ln -sf ${PWD}/busmonitor.nginx.conf /etc/nginx/sites-enabled/busmonitor.conf