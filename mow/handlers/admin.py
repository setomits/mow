# -*- coding: utf-8 -*-

from datetime import datetime
from os.path import getmtime, getsize
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
    g.db_updated_at = datetime.fromtimestamp(
        getmtime(g.sqlalchemy_database_uri))
    g.db_mbytes = getsize(g.sqlalchemy_database_uri) / 1024 / 1024

    g.mc_stats = {}
    for server, stats in g.mc.get_stats():
        d = dict(
            cmd_get = int(stats[b'cmd_get']),
            get_hits = int(stats[b'get_hits']),
            total_items = int(stats[b'total_items'])
        )
        d['hit_ratio'] = '%5.2lf %%' % (d['get_hits'] / d['cmd_get'] * 100)
        g.mc_stats[server.decode('utf-8')] = d

    return render_template('admin/top.html')
