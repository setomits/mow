# -*- coding: utf-8 -*-

from flask import g, render_template, request

from mow import app
from mow.handlers import returns_xml

@app.route('/')
def top_page():
    return render_template('top_page.html')

@app.route('/rss')
@returns_xml
def rss_xml():
    if request.args.get('without_comments', ''):
        with_comments = False
    else:
        with_comments = True

    return render_template('rss.xml', with_comments = with_comments)
