# -*- coding: utf-8 -*-

import os

class _Config:
    SECRET_KEY = 'YOUR_SECRET_KEY'
    ENTRIES_PER_PAGE = 5
    ITEMS_FOR_SIDE = 10
    BLOG_TITLE = 'blogSetomits'
    MC_SERVERS = ['localhost:11211',]

class DevelopmentConfig(_Config):
    DEBUG = True
    TESTING = False
    SQLALCHEMY_DATABASE_URI = 'sqlite:///%s/db/blog.db' % \
                              os.path.abspath(os.path.dirname(__file__))


class TestingConfig(_Config):
    DEBUG = False
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite://'


class Config(DevelopmentConfig):
    pass
