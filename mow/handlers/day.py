# -*- coding: utf-8 -*-

from datetime import datetime

from flask import g, redirect, render_template, url_for

from mow import app
from mow.models import Entry

@app.route('/day/<int:year>-<int:month>-<int:day>/')
@app.route('/day/<int:year>-<int:month>-<int:day>/<int:page>')
def day_page(year, month, day, page = 1):
    if page < 1:
        return redirect(url_for('day_page',
                                year = year, month = month, day = day))

    try:
        posted_on = datetime(year, month, day)
    except ValueError:
        return abort(400)
    else:
        g.posted_on = posted_on
        g.page = page
        g.entries = Entry.fetch_day_entries(
            posted_on = posted_on,
            page = page,
            limit = g.entries_per_page)

        if g.entries_per_page * (page - 1) + len(g.entries) < \
           Entry.n_day_entries(posted_on):
            g.has_older = True
        else:
            g.has_older = False
        g.has_newer = True if page > 1 else False

        return render_template('day_page.html')

@app.route('/month/<int:year>-<int:month>/')
@app.route('/month/<int:year>-<int:month>/<int:page>')
def month_page(year, month, page = 1):
    if page < 1:
        return redirect(url_for('month_page', year = year, month = month))

    try:
        posted_in = datetime(year, month, 1)
    except ValueError:
        return abort(400)
    else:
        g.posted_in = posted_in
        g.page = page
        g.entries = Entry.fetch_month_entries(
            posted_in = posted_in,
            page = page,
            limit = g.entries_per_page)

        if g.entries_per_page * (page - 1) + len(g.entries) < \
           Entry.n_month_entries(posted_in):
            g.has_older = True
        else:
            g.has_older = False
        g.has_newer = True if page > 1 else False

        return render_template('month_page.html')
