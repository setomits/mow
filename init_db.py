#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys

from config import Config
from mow.models import db

def _main():
    dev_db = Config.SQLALCHEMY_DATABASE_URI

    if os.path.exists(dev_db):
        sys.exit('"%s" already exists.' % dev_db)
    else:
        db.create_all()
        sys.exit('Database "%s" and all tables are created!.' % dev_db)

if __name__ == '__main__':
    _main()
