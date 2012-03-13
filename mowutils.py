# -*- coding: utf-8 -*-

import calendar
from datetime import date, datetime, timedelta
import fcntl
import os
import os.path
import sqlite3
import time
import urllib
import xmlrpclib
import ConfigParser
import HTMLParser

def start_db(db_path):
    sqls = (
        '''CREATE TABLE entries
           (eid INTEGER PRIMARY KEY CHECK(eid > 0),
            year INTEGER CHECK(year > 1976),
            month INTEGER CHECK(month BETWEEN 1 AND 12),
            day INTEGER CHECK(day BETWEEN 1 AND 31),
            hour INTEGER CHECK(hour BETWEEN 0 AND 23),
            minute INTEGER CHECK(minute BETWEEN 0 AND 59),
            title TEXT, subtitle TEXT, body TEXT, extend TEXT,
            ymdhm INTEGER);''',
        '''CREATE TABLE tags
           (eid INTEGER CHECK(eid > 0), name TEXT, ymdhm INTEGER);''',
        '''CREATE TABLE comments
           (eid INTEGER CHECK(eid > 0), author TEXT, title TEXT, body TEXT,
            visible INTEGER,
            year INTEGER CHECK(year > 0),
            month INTEGER CHECK(month BETWEEN 1 AND 12),
            day INTEGER CHECK(day BETWEEN 1 AND 31),
            hour INTEGER CHECK(hour BETWEEN 0 AND 23),
            minute INTEGER CHECK(minute BETWEEN 0 AND 59),
            ymdhm INTEGER);''',
    )

    if not os.path.exists(db_path):
        db = sqlite3.connect(db_path)
        for sql in sqls:
            db.execute(sql)
        db.commit()
        db.close()

        os.chmod(db_path, 0666)
        os.chmod(os.path.dirname(db_path), 0777)


def update_entry(db_path, eid, column, val):
    if column in ('eid', 'year', 'month', 'day', 'hour', 'minute', 'ymdhm',
                  'title', 'subtitle', 'body', 'extend'):
        sql = 'UPDATE entries SET %s = ? WHERE eid = ?;' % column

        db = sqlite3.connect(db_path)
        db.execute(sql, (val, eid))
        db.commit()
        db.close()

def update_tagname(db_path, org_name, new_name):
    sql = 'UPDATE tags SET name = ? WHERE name = ?;'

    db = sqlite3.connect(db_path)
    db.execute(sql, (new_name, org_name))
    db.commit()
    db.close()

def update_tags(db_path, eid, tags, ymdhm):
    dsql = 'DELETE FROM tags WHERE eid = ?;'
    isql = 'INSERT INTO tags VALUES (?, ?, ?)'

    db = sqlite3.connect(db_path)
    db.execute(dsql, (eid,))
    for tag in tags:
        db.execute(isql, (eid, tag, ymdhm))
    db.commit()
    db.close()

def update_comment(db_path, cid, column, val):
    if column in ('year', 'month', 'day', 'hour', 'minute', 'ymdhm',
                  'author', 'title', 'body', 'visible'):
        sql = 'UPDATE comments SET %s = ? WHERE rowid = ?;' % column

        db = sqlite3.connect(db_path)
        db.execute(sql, (val, cid))
        db.commit()
        db.close()

def delete_entry(db_path, eid):
    sqls = ('DELETE FROM entries WHERE eid = ?;',
            'DELETE FROM comments WHERE eid = ?;',
            'DELETE FROM tags WHERE eid = ?;')

    db = sqlite3.connect(db_path)
    for sql in sqls:
        db.execute(sql, (eid,))
    db.commit()
    db.close()

def delete_comment(db_path, cid):
    sql = 'DELETE FROM comments WHERE rowid = ?;'

    db = sqlite3.connect(db_path)
    db.execute(sql, (cid,))
    db.commit()
    db.close()

def all_tags_option(conf):
    sql = 'SELECT name FROM tags GROUP BY name ORDER BY name;'
    OPTION = u'<option value="%s">%s</option>'

    db = sqlite3.connect(conf['db_path'])
    rows = db.execute(sql).fetchall()
    db.close()

    return u''.join([OPTION % (row[0], row[0]) for row in rows])

def _symdhm(year, month, day, hour, minute):
    return u'%04d%02d%02d%02d%02d' % (year, month, day, hour, minute)

def _iymdhm(year, month, day, hour, minute):
    return int(_symdhm(year, month, day, hour, minute))

def _datetime(year, month, day, hour, minute):
    return datetime(year, month, day, hour, minute) + \
        timedelta(seconds = time.timezone)

def entry_row(db_path, eid):
    sql = '''SELECT eid, year, month, day, hour, minute,
                    title, subtitle, body, extend, ymdhm
             FROM entries
             WHERE eid = ?;'''

    db = sqlite3.connect(db_path)
    row = db.execute(sql, (eid,)).fetchone()
    db.close()

    return row

def comment_row(db_path, cid):
    sql = '''SELECT eid, rowid, 0, author, title, body, visible,
                    year, month, day, hour, minute
             FROM comments WHERE rowid= ?;'''

    db = sqlite3.connect(db_path)
    row = db.execute(sql, (cid,)).fetchone()
    db.close()

    return row

def tags_list(db_path, eid):
    sql = 'SELECT name FROM tags WHERE eid = ?;'

    db = sqlite3.connect(db_path)
    rows = db.execute(sql, (eid,)).fetchall()
    db.close()

    tags = [Tag(row[0]) for row in rows]
    tags.sort()

    return tags

def get_entry(conf, eid, with_neighbors = False):
    row = entry_row(conf['db_path'], eid)

    if row:
        e = Entry(*row[:-1])
        e.tags = tags_list(conf['db_path'], eid)

        db = sqlite3.connect(conf['db_path'])
        e._set_comments(db)
        if with_neighbors:
            e._set_prev(db)
            e._set_next(db)
        db.close()
    else:
        e = None

    return e

def get_comment(conf, cid):
    row = comment_row(conf['db_path'], cid)

    if row:
        c = Comment(*row[:7])
        c.set_posted_at(*row[7:])
    else:
        c = None

    return c

def get_conf(req, local_root):
    o = {'local_root': local_root,
         'db_path': '%s/db/blog.db' % local_root, 
         'blog_root': req.application_url,
         'blog_path': req.application_url.replace(req.host_url, '')}

    cp = ConfigParser.ConfigParser()
    cp.read('%s/config' % local_root)

    o['blog_title'] = unicode(cp.get('general', 'blog_title'),
                              'utf-8', 'ignore')

    if cp.has_option('general', 'introduction'):
        o['introduction'] = unicode(cp.get('general', 'introduction'),
                                    'utf-8', 'ignore')
    else:
        o['introduction'] = u''

    if cp.has_option('general', 'main_len'):
        o['main_len'] = cp.getint('general', 'main_len')
    else:
        o['main_len'] = 5

    if cp.has_option('general', 'sub_len'):
        o['sub_len'] = cp.getint('general', 'sub_len')
    else:
        o['sub_len'] = 5

    if cp.has_option('general', 'author'):
        o['author'] = unicode(cp.get('general', 'author'), 'utf-8', 'ignore')
    else:
        o['author'] = unicode(req.application_url.split('/')[-1],
                              'utf-8', 'ignore')

    if cp.has_option('general', 'lang'):
        o['lang'] = unicode(cp.get('general', 'lang'), 'utf-8', 'ignore')
    else:
        o['lang'] = 'ja'

    if cp.has_option('general', 'ping_servers'):
        ups = unicode(cp.get('general', 'ping_servers'), 'utf-8', 'ignore')
        o['ping_servers'] = [up.strip() for up in ups.split() if up.strip()]
    else:
        o['ping_servers'] = []

    return o

def get_cache(conf, cache_path):
    db_path = conf['db_path']
    root = conf['local_root']
    cache_full_path = os.path.normpath('%(root)s/cache/%(cache_path)s' \
                                           % locals())

    if not os.path.exists(cache_full_path) \
            or os.path.getmtime(db_path) > os.path.getmtime(cache_full_path):
        return None
    else:
        f = open(cache_full_path)
        fcntl.lockf(f, fcntl.LOCK_SH)
        p = f.read()
        fcntl.lockf(f, fcntl.LOCK_UN)
        f.close()

        return p

def save_cache(conf, cache_path, content):
    root = conf['local_root']
    cache_full_path = os.path.normpath('%(root)s/cache/%(cache_path)s' \
                                           % locals())

    dname = os.path.dirname(cache_full_path)
    if not os.path.exists(dname):
        os.makedirs(dname)
        os.chmod(dname, 0777)

    f = open(cache_full_path, 'w')
    fcntl.lockf(f, fcntl.LOCK_EX)
    f.write(content)
    fcntl.lockf(f, fcntl.LOCK_UN)
    f.close()

def recent_eid_titles(db_path, counts):
    sql = 'SELECT eid, title FROM entries ORDER BY ymdhm DESC LIMIT ?;'

    if db_path:
        db = sqlite3.connect(db_path)
        rows = db.execute(sql, (counts,)).fetchall()
        db.close()
    else:
        rows = []

    return rows

def recent_comments(db_path, counts):
    sql = '''SELECT eid, rowid, 0, author, title, body,
                    year, month, day, hour, minute
             FROM comments WHERE visible = 1 ORDER BY ymdhm DESC LIMIT ?;'''

    o = []

    if db_path:
        db = sqlite3.connect(db_path)
        rows = db.execute(sql, (counts,)).fetchall()
        db.close()

        for row in rows:
            c = Comment(*row[:6])
            c.set_posted_at(*row[6:])
            o.append(c)

    return o

def ymd_entry_ids(db_path, year, month, day):
    SEL_YMD_ENTRY_IDS = '''SELECT eid FROM entries 
                           WHERE year = ? AND month = ? AND day = ?
                           ORDER BY ymdhm DESC;'''
    db = sqlite3.connect(db_path)
    rows = db.execute(SEL_YMD_ENTRY_IDS, (year, month, day)).fetchall()
    db.close()

    return [row[0] for row in rows]

def ym_entry_ids(db_path, year, month, limit, offset):
    SEL_YM_ENTRY_IDS = '''SELECT eid FROM entries
                          WHERE year = ? AND month = ? ORDER BY ymdhm DESC
                          LIMIT ? OFFSET ?;'''
    db = sqlite3.connect(db_path)
    rows = db.execute(SEL_YM_ENTRY_IDS, (year, month, limit, offset)).fetchall()
    db.close()

    return [row[0] for row in rows]

def tag_entry_ids(db_path, name, limit, offset):
    SEL_TAG_ENTRY_IDS = '''SELECT eid FROM tags
                           WHERE name = ? ORDER BY ymdhm DESC
                           LIMIT ? OFFSET ?;'''

    db = sqlite3.connect(db_path)
    rows = db.execute(SEL_TAG_ENTRY_IDS, (name, limit, offset)).fetchall()
    db.close()

    return [row[0] for row in rows]

def cal_table(conf, y = '', m = ''):
    cal = MyHTMLCalendar(conf)
    try:
        year, month = int(y), int(m)
    except:
        today = date.today()
        year, month = today.year, today.month

    return cal.formatmonth(year, month)

def valid_page_num(p):
    if p.isdigit():
        p = int(p)
        if p > 0:
            return p
    else:
        return 1

def get_paging(len_eids, limit, page):
    if len_eids > limit:
        older_num = page + 1
    else:
        older_num = None

    newer_num = page - 1

    return older_num, newer_num

def _format_day(day):
    _ext = {1: 'st', 2: 'nd', 3: 'rd', 21: 'st', 22: 'nd', 23: 'rd', 31: 'st'}
    if _ext.has_key(day):
        return u'%d%s' % (day, _ext[day])
    else:
        return u'%dth' % day

def hot_tags(conf):
    sql = '''SELECT name, cnt FROM (
              SELECT name, COUNT(*) as cnt FROM tags
              GROUP BY name ORDER BY COUNT(*) DESC LIMIT ?
             ) ORDER BY name;'''

    db = sqlite3.connect(conf['db_path'])
    rows = db.execute(sql, (conf['sub_len'],)).fetchall()
    db.close()

    return [Tag(tag_name, tag_count) for tag_name, tag_count in rows]

def fetch_all_tags(conf):
    sql = 'SELECT name, COUNT(*) FROM tags GROUP BY name ORDER BY name;'

    db = sqlite3.connect(conf['db_path'])
    rows = db.execute(sql).fetchall()
    db.close()

    return [Tag(tag_name, tag_count) for tag_name, tag_count in rows]

def fetch_archive(conf):
    sql = '''SELECT year, month, COUNT(*) FROM entries
                 GROUP BY year, month ORDER BY ymdhm;'''

    db = sqlite3.connect(conf['db_path'])
    rows = db.execute(sql).fetchall()
    db.close()

    d = {}
    for year, month, month_count in rows:
        if year in d:
            d[year].append({'month': month, 'month_count': month_count})
        else:
            d[year] = [{'month': month, 'month_count': month_count}]

    return d

class MyHTMLCalendar(calendar.HTMLCalendar):
    def __init__(self, conf):
        super(MyHTMLCalendar, self).__init__(calendar.SUNDAY)
        self.db_path = conf['db_path']
        self.blog_path = conf['blog_path']

    def formatday(self, year, month, day, weekday):
        if day == 0 or self.db_path == '':
            return super(MyHTMLCalendar, self).formatday(day, weekday)

        SEL_DAY_ENTRY = '''SELECT title FROM entries
                           WHERE year = ? AND month = ? AND day = ?
                           ORDER BY ymdhm DESC'''
        db = sqlite3.connect(self.db_path)
        rows = db.execute(SEL_DAY_ENTRY, (year, month, day)).fetchall()
        db.close()

        if rows:
            blog_path, css_class = self.blog_path, self.cssclasses[weekday]
            titles = u',\n'.join((r[0] for r in rows))
            td = u'''<td class="%(css_class)s">\
<a href="%(blog_path)s/day/%(year)d-%(month)d-%(day)d" title="%(titles)s">\
%(day)d</a></td>''' % locals()
            return td
        else:
            return super(MyHTMLCalendar, self).formatday(day, weekday)

    def formatweek(self, year, month, theweek):
        s = u''.join(self.formatday(year, month, d, wd) for (d, wd) in theweek)
        return u'<tr>%s</tr>\n' % s

    def formatmonthname(self, theyear, themonth):
        s = u'''<tr>\
<th><a href="javascript:MOW.calTable(%(theyear)d,%(themonth)d, 'prev');" title="Previous Month"><i class="icon-arrow-left"></i></a></th>\
<th colspan="5" class="month">\
<a href="%(blog_path)s/month/%(theyear)d-%(themonth)d/">%(smonth)s %(theyear)d</a>\
</th>\
<th><a href="javascript:MOW.calTable(%(theyear)d,%(themonth)d, 'next');" title="Next Month"><i class="icon-arrow-right"></i></a></th>\
</tr>\n'''
        smonth = calendar.month_abbr[themonth]
        blog_path = self.blog_path

        return s % locals()

    def formatmonth(self, theyear, themonth):
        v = []
        a = v.append
        a(u'<table class="month">\n')
        a(self.formatmonthname(theyear, themonth))
        a(self.formatweekheader())
        a(u'\n')
        for week in self.monthdays2calendar(theyear, themonth):
            a(self.formatweek(theyear, themonth, week))
        a(u'</table>\n')

        return u''.join(v)

class MyHTMLParser(HTMLParser.HTMLParser):
    ok_tags = [u'a', u'b', u'blockquote', u'em', u'font', u'i', u'img', u'li',
               u'ol', u'pre', u'span', u'strike', u'strong', u'u', u'ul']
    ok_entrefs = {u'quot': u'"', u'amp': u'&', u'nbsp': u' ',
                  u'lt': u'<', u'gt': u'>'}

    def __init__(self):
        HTMLParser.HTMLParser.__init__(self)
        self._html = []
        self._plain = []

    def reset(self):
        HTMLParser.HTMLParser.reset(self)
        self._html = []
        self._plain = []

    def html(self, html = u''):
        if html:
            self.reset()
            self.feed(html)

        h = u''.join(self._html)
        return h.replace(u'\n', u'<br />')

    def plain(self, html = u''):
        if html:
            self.reset()
            self.feed(html)
        return u''.join(self._plain)

    def handle_starttag(self, tag, attr):
        if tag in self.ok_tags:
            self._html.append(u'<%s' % tag)

            for a, v in attr:
                if not v or \
                        v[0:2].lower() == u'on' or \
                        v[0:10].lower() == u'javascript': 
                    continue
                else:
                    self._html.append(u' %s="%s"' % (a, v))
            if tag == u'img':
                self._html.append(u' />')
            else:
                self._html.append(u'>')

    def handle_endtag(self, tag):
        if tag in self.ok_tags and tag != u'img':
            self._html.append(u'</%s>' % tag)

    def handle_data(self, data):
        if data:
            self._html.append(data)
            self._plain.append(data)

    def handle_entityref(self, name):
        if name in self.ok_entrefs:
            self._html.append(u'&%s;' % name)
            self._plain.append(self.ok_entrefs[name])

class Entry(object):
    def __init__(self, eid = u'',
                 year = 0, month = 0, day = 0, hour = 0, minute = 0,
                 title = u'', subtitle = u'', body = u'', extend = u'', 
                 tags = []):
        self.eid = eid
        self.year = year
        self.month = month
        self.day = day
        self.hour = hour
        self.minute = minute
        self.title = title if title else u'No Title'
        self.subtitle = subtitle
        self.body = body
        self.extend = extend
        self.tags = tags
        self.iymdhm = _iymdhm(self.year, self.month, self.day,
                              self.hour, self.minute)
        self.published_at = _datetime(self.year, self.month, self.day,
                                      self.hour, self.minute)

    def _set_prev(self, db):
        sql = '''SELECT eid, title FROM entries
                 WHERE ymdhm < ? ORDER BY ymdhm DESC;'''

        row = db.execute(sql, (self.iymdhm,)).fetchone()
        if row:
            self.prev = {'eid': row[0], 'title': row[1] if row[1] else u'No Title'}
        else:
            self.prev = None

    def _set_next(self, db):
        sql = 'SELECT eid, title FROM entries WHERE ymdhm > ? ORDER BY ymdhm;'

        row = db.execute(sql, (self.iymdhm,)).fetchone()
        if row:
            self.next = {'eid': row[0], 'title': row[1] if row[1] else u'No Title'}
        else:
            self.next = None

    def _set_comments(self, db):
        sql = '''SELECT eid, rowid, 0, author, title, body,
                        year, month, day, hour, minute 
                 FROM comments WHERE eid = ? AND visible = 1 ORDER BY ymdhm;'''

        self.comments = []
        for row in db.execute(sql, (self.eid,)).fetchall():
            c = Comment(*row[:6])
            c.set_posted_at(*row[6:])
            self.comments.append(c)

    def pub_month_str(self):
        return calendar.month_abbr[self.month]

    def pub_day_str(self):
        return _format_day(self.day)

    def post(self, db_path):
        esql = 'INSERT INTO entries VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);'
        tsql = 'INSERT INTO tags VALUES (?, ?, ?);'

        _msg = ['[mow] : posting %s :' % self.eid]
        db = sqlite3.connect(db_path)
        try:
            db.execute(esql, (self.eid, self.year, self.month, self.day,
                              self.hour, self.minute,
                              self.title, self.subtitle, self.body, self.extend,
                              self.iymdhm))
            for tag in self.tags:
                db.execute(tsql, (self.eid, tag, self.iymdhm))
            db.commit()
        except sqlite3.IntegrityError, e:
            _msg.append(str(e))
        else:
            _msg.append('Succeeded.')
        db.close()
        print ' '.join(_msg)


    def ping(self, blog_title, blog_root, ping_servers):
        blog_url = '%s/' % blog_root
        rss_url = '%s/rss' % blog_root

        for ping_server in ping_servers:
            _msg = ['[mow] : ping to %s :' % ping_server]
            try:
                s = xmlrpclib.ServerProxy(ping_server)
                s.weblogUpdates.ping(blog_title, blog_url, rss_url)
            except Exception, e:
                _msg.append(str(e))
            else:
                _msg.append('Succeeded.')
            print ' '.join(_msg)


class Comment(object):
    def __init__(self, eid, cid = None, ptime = 0,
                 author = u'', title = u'', body = u'', visible = 1):
        self.eid = eid
        self.cid = cid
        self.ptime = ptime
        self.author = author
        self.title = title if title else u'No Title'
        self.body = body
        self.visible = visible
        self.year, self.month, self.day, self.hour, self.minute = 0, 0, 0, 0, 0
        
    def is_visible(self):
        AVAILABLE_HREFS = 10

        if self.body.count(u'href') > AVAILABLE_HREFS:
            return 0
        else:
            return 1

    def set_posted_at(self, year, month, day, hour, minute):
        self.year, self.month, self.day = year, month, day
        self.hour, self.minute = hour, minute

        self.iymdhm = _iymdhm(self.year, self.month, self.day,
                              self.hour, self.minute)
        self.posted_at = _datetime(year, month, day, hour, minute)

    def posted_month_str(self):
        return calendar.month_abbr[self.month]

    def posted_day_str(self):
        return _format_day(self.day)

    def post(self, db_path):
        csql = 'INSERT INTO comments VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);'

        self.year, self.month, self.day, self.hour, self.minute \
            = time.localtime(self.ptime)[:5]
        iymdhm = _iymdhm(self.year, self.month, self.day, self.hour, self.minute)

        db = sqlite3.connect(db_path)
        db.execute(csql, (self.eid, self.author, self.title, self.body,
                          self.is_visible(), self.year, self.month, self.day,
                          self.hour, self.minute, iymdhm))
        db.commit()
        db.close()

class Tag(object):
    def __init__(self, name, count = 0):
        self.name = name
        self.urlencoded = urllib.quote_plus(name.encode('utf-8'))
        self.count = count

def _main():
    import sys
    start_db(sys.argv[1])

if __name__ == '__main__':
    _main()
