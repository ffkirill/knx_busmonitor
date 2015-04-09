#!/usr/bin/env bash
cd ..
virtualenv env --no-site-packages
env/bin/pip install -r knx_busmonitor/requirements.txt
cd knx_busmonitor/eibd_stack
../../env/bin/python setup.py build
cd ..
cp eibd_stack/build/lib.linux-*/eibd_stack.so .
ln -sf ${PWD}/busmonitor.supervisor.conf /etc/supervisor/conf.d/busmonitor.conf
ln -sf ${PWD}/busmonitor.nginx.conf cat /etc/nginx/sites-enabled/busmonitor.conf