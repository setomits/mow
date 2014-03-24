# -*- coding: utf-8 -*-

from operator import itemgetter

from tzlocal import get_localzone
from flask import g, Markup

from mow import app

@app.template_filter()
def ymdhms(dt):
    return dt.strftime('%Y/%b/%d %H:%M:%S')

@app.template_filter()
def rfc822(dt):
    return get_localzone().localize(dt).strftime('%a, %d %b %Y %H:%M:%S %z')

@app.template_filter()
def iso8601(dt):
    return get_localzone().localize(dt).strftime('%Y-%m-%dT%H:%M:%S%z')

@app.template_filter()
def mdy(dt):
    return dt.strftime('%b %d, %Y')

@app.template_filter()
def my(dt):
    return dt.strftime('%b %Y')

@app.template_filter()
def hm(dt):
    return dt.strftime('%H:%M')

@app.template_filter()
def mb_truncate(s, length = 40, end = '...'):
    return s if len(s) < length else s[:length] + end

@app.template_filter()
def target_blank(s):
    if isinstance(s, str):
        s = Markup(s)

    return s.replace('a href=', Markup('a target="_blank" href='))

@app.template_filter()
def thousands_comma(x):
    return format(x, ',d')

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
