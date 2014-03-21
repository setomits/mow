#!/usr/bin/env python

from os import environ
from os.path import abspath, dirname

def _main():
    _root = abspath(dirname(__file__))
    environ['YOURAPPLICATION_SETTINGS'] = '%s/config.py' % _root
    
    from mow import app
    app.run(debug = True, host = '0.0.0.0')


if __name__ == '__main__':
    _main()

