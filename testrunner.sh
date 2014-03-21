#!/bin/sh

cp config.py config.py.dev;
sed -e 's/Config(DevelopmentConfig)/Config(TestingConfig)/' config.py.dev > config.py
python -m unittest discover;
mv config.py.dev config.py;
