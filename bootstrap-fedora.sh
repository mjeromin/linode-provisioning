#!/usr/bin/env bash

# install ansible (note: ansible 2.5+ supports python 3.5+)
yum install -y libselinux-python
pip3 install --upgrade pip
/usr/local/bin/pip3 install ansible==2.5.10  # full pip3 path needed after upgrade
