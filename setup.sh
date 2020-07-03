#! /bin/bash

sudo apt install curl
pip install bs4
pip install flask
pip install werkzeug
pip install numpy
pip install flask_restful
pip install nltk
pip install argparse
curl -sS https://dl.yarnpkg.com/debian/pubkey.gpg | sudo apt-key add -
echo "deb https://dl.yarnpkg.com/debian/ stable main" | sudo tee/etc/apt/sources.list.d/yarn.list

sudo apt update
sudo apt install yarn
yarn install
python3 api.py&yarn serve 
