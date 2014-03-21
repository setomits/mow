# -*- coding: utf-8 -*-

from operator import itemgetter

from flask import g, Markup

from mow import app

@app.template_filter()
def ymdhms(s):
    return s.strftime('%Y/%b/%d %H:%M:%S')

@app.template_filter()
def rfc822(s):
    return s.strftime('%a, %d %b %Y %H:%M:%S +0000')

@app.template_filter()
def iso8601(s):
    return s.strftime('%Y-%m-%dT%H:%M:%SZ')

@app.template_filter()
def mdy(s):
    return s.strftime('%b %d, %Y')

@app.template_filter()
def my(s):
    return s.strftime('%b %Y')

@app.template_filter()
def hm(s):
    return s.strftime('%H:%M')

@app.template_filter()
def mb_truncate(s, length = 40, end = '...'):
    return s if len(s) < length else s[:length] + end

@app.template_filter()
def target_blank(s):
    if isinstance(s, str):
        s = Markup(s)

    return s.replace('a href=', Markup('a target="_blank" href='))

@app.template_filter()
def nl2br(s):
    if isinstance(s, str):
        s = Markup(s)

    return s.replace('\n', Markup('<br />\n'))

@app.template_filter()
def hot_tags(t):
    t.sort(key = itemgetter(1), reverse = True)
    hots = t[:g.items_for_side]
    hots.sort()

    return hots
