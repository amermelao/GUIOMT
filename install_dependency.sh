#!/bin/bash

# never forget to change the current path in the main.py
# appending to sys.path

sudo add-apt-repository ppa:kivy-team/kivy
sudo apt-get update
sudo apt-get --yes install python-setuptools
sudo apt-get --yes install python-dev
sudo pip install katcp
sudo apt-get --yes install python-kivy
