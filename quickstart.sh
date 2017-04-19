#!/bin/bash

pushd ../

git clone https://github.com/ampledata/kiss.git
git clone https://github.com/ampledata/aprs.git
popd

ln -sfr ../kiss/kiss
ln -sfr ../aprs/aprs

virtualenv -p python2 env
source env/bin/activate
pip install -r requirements.txt

git clone https://github.com/NERVEUML/multimon-ng
git clone https://github.com/wb2osz/direwolf
pushd direwolf
make
popd


