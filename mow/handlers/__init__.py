# -*- coding: utf-8 -*-

from functools import wraps

from flask import g, redirect, request, session, url_for, Response

from mow import app
from mow.models import remove_session
from mow.models import Comment, Entry, Tag, User

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if g.login_user is None:
            return redirect(url_for('login_page', next_url = request.url))
        return f(*args, **kwargs)
    return decorated_function

def returns_xml(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        r = f(*args, **kwargs)
        return Response(r, content_type = 'text/xml; charset=utf-8')
    return decorated_function

@app.before_request
def check_login_user():
    g.login_user = None

    if 'user_name' in session:
        login_user = User.get_by_name(session['user_name'])
        if login_user:
            g.login_user = login_user
        else:
            session.pop('username', None)

@app.before_request
def load_values_from_config():
    g.blog_title = app.config['BLOG_TITLE']
    g.entries_per_page = app.config['ENTRIES_PER_PAGE']
    g.items_for_side = app.config['ITEMS_FOR_SIDE']


@app.before_request
def load_values_for_side():
    g.recent_entries = Entry.fetch_recent_entries(
        max(g.items_for_side, g.entries_per_page))
    g.recent_comments = Comment.fetch_recent_comments(
        max(g.items_for_side, g.entries_per_page))
    g.tag_counts = Tag.fetch_tag_counts()
    g.archives = Entry.fetch_archives()



@app.teardown_appcontext
def shutdown_session(exception = None):
    remove_session()

from . import filters
from . import admin, day, entry, top, user, comment, tag
