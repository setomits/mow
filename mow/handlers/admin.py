# -*- coding: utf-8 -*-

from flask import g, render_template

from mow import app
from mow.models import Comment, Entry, Tag, User
from mow.handlers import login_required

@app.route('/admin')
@login_required
def admin_top_page():
    g.sqlalchemy_database_uri \
        = app.config['SQLALCHEMY_DATABASE_URI'].replace('sqlite:///', '')
    g.n_total_comments = Comment.n_total_count()
    g.n_total_entries = Entry.n_total_count()
    g.n_total_tags = Tag.n_total_count()
    g.n_total_users = User.n_total_count()

    return render_template('admin/top.html')
