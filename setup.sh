#! /bin/bash

pip install curl
pip install werkzeug
pip install numpy
pip install flask_restful
pip install nltk
pip install argparse
pip install json
pip install requests
pip install timeit
pip install math
pip install re
pip install bs4
pip install flask
curl -sS https://dl.yarnpkg.com/debian/pubkey.gpg | sudo apt-key add -
echo "deb https://dl.yarnpkg.com/debian/ stable main" | sudo tee/etc/apt/sources.list.d/yarn.list

sudo apt update 
sudo apt install yarn
python3 api.py&yarn serve
