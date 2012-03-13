import os
import sys
import time
import urllib

from jinja2 import Environment, FileSystemLoader
from webob import Request, Response

sys.path.append(os.path.dirname(__file__))
import mowutils

class Blog(object):
    def __call__(self, environ, start_response):
        self.req = Request(environ)
        self.resp = Response()
        self.start_response = start_response

        self.conf = mowutils.get_conf(self.req, os.path.dirname(__file__))

        return self._main()

    def _main(self):
        path_list = [p for p in self.req.path_info.split('/') if p]

        if not path_list:
            self._top_page()
        elif path_list[0].isdigit():
            self._entry_page(path_list[0])
        elif path_list[0] == 'tag':
            self._tag_page(path_list)
        elif path_list[0] == 'day':
            self._day_page(path_list)
        elif path_list[0] == 'month':
            self._month_page(path_list)
        elif path_list[0] == 'manage':
            self._manage_page(path_list)
        elif path_list[0] == 'rss':
            self._rss()
        elif path_list[0] == 'cal_table':
            self._calendar_table()
        elif path_list[0] == 'all_tags':
            self._all_tags_ul()
        elif path_list[0] == 'post_comment':
            self._post_comment()
        else:
            self._error_page('404', 'Not Found')

        self.start_response(self.resp.status, self.resp.headerlist)
        return self.resp.body

    def _render(self, fname, dat = {}, with_sub_contents = False):
        env = Environment(
            loader = FileSystemLoader(
                '%s/templates' % os.path.dirname(__file__)))
        template = env.get_template(fname)

        for k in self.conf:
            dat[k] = self.conf[k]

        if with_sub_contents:
            dat['cal_table'] = mowutils.cal_table(self.conf)
            dat['sub_recent_entries'] = \
                [{'eid': eid, 'title': title}
                 for eid, title in mowutils.recent_eid_titles(
                        self.conf['db_path'], self.conf['sub_len'])]
            dat['sub_recent_comments'] = mowutils.recent_comments(
                self.conf['db_path'], self.conf['sub_len'])
            dat['sub_tags'] = mowutils.hot_tags(self.conf)
            dat['sub_archive'] = mowutils.fetch_archive(self.conf)

        return template.render(dat).encode('utf-8')

    def _redirect_to_top(self):
        self.resp.status = 302
        self.resp.location = '%s/' % self.conf['blog_root']

    def _top_page(self):
        cache_path = 'index'
        html = mowutils.get_cache(self.conf, cache_path)
        if not html:
            eid_titles = mowutils.recent_eid_titles(self.conf['db_path'],
                                                 self.conf['main_len'])
            entries = []
            if eid_titles:
                for eid, etitle in eid_titles:
                    entries.append(mowutils.get_entry(self.conf, eid))


            html = self._render('top.html', {'entries': entries}, True)
            mowutils.save_cache(self.conf, cache_path, html)

        self.resp.body = html

    def _entry_page(self, eid):
        cache_path = 'entries/%s' % eid
        html = mowutils.get_cache(self.conf, cache_path)
        if html:
            self.resp.body = html
        else:
            entry = mowutils.get_entry(self.conf, eid, with_neighbors = True)
            if entry:
                html = self._render('entry.html', {'entry': entry}, True)
                mowutils.save_cache(self.conf, cache_path, html)
                self.resp.body = html
            else:
                self._redirect_to_top()

    def _tag_page(self, path_list):
        tag_name, page_num = self._name_page(path_list)

        if tag_name:
            limit = int(self.conf['main_len'])
            offset = limit * (page_num - 1)

            cache_path = 'tags/%s_%d' % (tag_name, page_num)
            html = mowutils.get_cache(self.conf, cache_path)
            if html:
                self.resp.body = html
            else:
                tag_eids = mowutils.tag_entry_ids(self.conf['db_path'],
                                                  tag_name, limit + 1, offset)
                if tag_eids:
                    entries = []
                    for eid in tag_eids[:limit]:
                        entries.append(mowutils.get_entry(self.conf, eid))

                        older_num, newer_num = \
                            mowutils.get_paging(len(tag_eids), limit, page_num)

                        html = self._render('tag.html',
                                            {'tag': mowutils.Tag(tag_name),
                                             'entries': entries,
                                             'page_num': page_num,
                                             'older_num': older_num,
                                             'newer_num': newer_num},
                                            True)
                        mowutils.save_cache(self.conf, cache_path, html)
                        self.resp.body = html
                else:
                    self._redirect_to_top()
        else:
            self._redirect_to_top()

    def _day_page(self, path_list):
        ymd, page_num = self._name_page(path_list)

        if ymd and len(ymd.split('-')) == 3:
            _ymd = ymd.split('-')
            for e in _ymd:
                if not e.isdigit():
                    self._redirect_to_top()
                    return
            year, month, day = (int(e) for e in _ymd)

            cache_path = 'days/%s' % ymd
            html = mowutils.get_cache(self.conf, cache_path)
            if html:
                self.resp.body = html
            else:
                ymd_eids = mowutils.ymd_entry_ids(self.conf['db_path'],
                                                  year, month, day)

                if ymd_eids:
                    entries = []
                    for eid in ymd_eids:
                        entries.append(mowutils.get_entry(self.conf, eid))

                    html = self._render('day.html',
                                        {'year': year,
                                         'month': month,
                                         'day': day,
                                         'entries': entries},
                                        True)
                    mowutils.save_cache(self.conf, cache_path, html)
                    self.resp.body = html
                else:
                    self._redirect_to_top()
        else:
            self._redirect_to_top()

    def _month_page(self, path_list):
        ym, page_num = self._name_page(path_list)

        if ym and len(ym.split('-')) == 2:
            _ym = ym.split('-')
            for e in _ym:
                if not e.isdigit():
                    self._redirect_to_top()
                    return

            year, month = (int(e) for e in _ym)

            limit = int(self.conf['main_len'])
            offset = limit * (page_num - 1)

            cache_path = 'months/%s_%d' % (ym, page_num)
            html = mowutils.get_cache(self.conf, cache_path)
            if html:
                self.resp.body = html
            else:
                ym_eids = mowutils.ym_entry_ids(self.conf['db_path'],
                                                year, month, limit + 1, offset)

                if ym_eids:
                    entries = []
                    for eid in ym_eids[:limit]:
                        entries.append(mowutils.get_entry(self.conf, eid))

                    older_num, newer_num = mowutils.get_paging(len(ym_eids),
                                                               limit, page_num)

                    html = self._render('month.html',
                                        {'year': year,
                                         'month': month,
                                         'entries': entries,
                                         'page_num': page_num,
                                         'older_num': older_num,
                                         'newer_num': newer_num},
                                        True)
                    mowutils.save_cache(self.conf, cache_path, html)
                    self.resp.body = html
                else:
                    self._redirect_to_top()
        else:
            self._redirect_to_top()

    def _manage_page(self, path_list):
        operation = 'index' if len(path_list) == 1 else path_list[1]

        if operation == 'index':
            db_path = self.conf['db_path']
            if os.path.exists(db_path):
                db_updated = time.asctime(time.localtime(os.path.getmtime(db_path)))
                db_size = os.path.getsize(db_path) / 1024.0 / 1024.0
            else:
                db_updated = None
                db_size = 0

            cache_dir = '/tmp/%s' % self.conf['blog_root']
            cache_size, cache_counts = 0, 0
            if os.path.exists(cache_dir):
                for root, dirs, files in os.walk(cache_dir):
                    cache_size += sum((os.path.getsize(os.path.join(root, fname))
                                       for fname in files))
                    cache_counts += len(files)

                cache_size = cache_size / 1024.0 / 1024.0

            html = self._render('manage/index.html',
                                {'db_updated': db_updated, 'db_size': db_size,
                                 'cache_dir': cache_dir,
                                 'cache_size': cache_size,
                                 'cache_counts': cache_counts},
                                True)

        elif operation == 'post':
            _eid_title = mowutils.recent_eid_titles(self.conf['db_path'], 1)
            new_eid = _eid_title[0][0] + 1 if len(_eid_title) else 1
            year, month, day, hour, minute = time.localtime()[:5]

            html = self._render('manage/post.html',
                                {'new_eid': new_eid,
                                 'year': year, 'month': month, 'day': day,
                                 'hour': hour, 'minute': minute},
                                True)

        elif operation == 'entry':
            eid = self.req.GET.get('eid', '')
            entry = mowutils.get_entry(self.conf, eid) if eid else None

            html = self._render('manage/entry.html', {'entry': entry}, True)

        elif operation == 'comment':
            cid = self.req.GET.get('cid', '')
            comment = mowutils.get_comment(self.conf, cid)

            html = self._render('manage/comment.html',
                                {'comment': comment},
                                True)

        elif operation == 'tag':
            org = self.req.POST.get('org', '').strip()
            dst = self.req.POST.get('dst', '').strip()

            if org and dst:
                mowutils.update_tagname(self.conf['db_path'], org, dst)

            tags = mowutils.fetch_all_tags(self.conf)
            html = self._render('manage/tag.html', {'tags': tags}, True)

        elif operation == 'post_entry':
            eid = self.req.POST.get('eid').strip()
            title = self.req.POST.get('title', '').strip()
            subtitle = self.req.POST.get('subtitle', '').strip()
            body = self.req.POST.get('body', '').strip()
            extend = self.req.POST.get('extend', '').strip()
            tags = [tag.strip()
                    for tag in self.req.POST.get('tags', '').strip().split(',')
                    if tag.strip()]
            
            year, month, day = \
                [int(i) for i in self.req.POST.get('ymd').strip().split('-')]
            hour, minute = [int(i)
                            for i in self.req.POST.get('hm').strip().split(':')]

            e = mowutils.Entry(eid, year, month, day, hour, minute,
                               title, subtitle, body, extend)
            e.tags = tags

            e.post(self.conf['db_path'])
            e.ping(self.conf['blog_title'], self.conf['blog_root'],
                   self.conf['ping_servers'])

            self.resp.status = 303
            self.resp.location = '%s/manage/entry?eid=%s' % \
                (self.conf['blog_root'], eid)

            return

        elif operation == 'update_entry':
            eid = self.req.POST.get('eid').strip()
            col = self.req.POST.get('col').strip()
            val = self.req.POST.get('val').strip()

            if col == 'ymd':
                for c, v in zip(['year', 'month', 'day'],
                                [int(i) for i in ymd.split('-')]):
                    mowutils.update_entry(self.conf['db_path'], eid, c, v)
            elif col == 'hm':
                for c, v in zip(['hour', 'minute'],
                                [int(i) for i in ymd.split(':')]):
                    mowutils.update_entry(self.conf['db_path'], eid, c, v)
            elif col == 'ymdhm':
                mowutils.update_entry(self.conf['db_path'], eid, col, int(val))
            else:
                mowutils.update_entry(self.conf['db_path'], eid, col, val)

            html = self._render('plain.txt', {'value': 'ok'})

        elif operation == 'delete_entry':
            eid = self.req.POST.get('eid').strip()
            mowutils.delete_entry(self.conf['db_path'], eid)

            self.resp.status = 303
            self.resp.location = '%s/manage/index' % self.conf['blog_root']
            
            return

        elif operation == 'update_tags':
            eid = self.req.POST.get('eid').strip()
            ymdhm = self.req.POST.get('ymdhm').strip()
            tags = [tag.strip()
                    for tag in self.req.POST.get('tags').strip().split(',')
                    if tag.strip()]

            mowutils.update_tags(self.conf['db_path'], eid, tags, ymdhm)
            html = self._render('plain.txt', {'value': 'ok'})

        elif operation == 'update_comment':
            cid = self.req.POST.get('cid')
            col = self.req.POST.get('col')
            val = self.req.POST.get('val')

            if col == 'ymd':
                for c, v in zip(['year', 'month', 'day'],
                                [int(i) for i in ymd.split('-')]):
                    mowutils.update_comment(self.conf['db_path'], cid, c, v)
            elif col == 'hm':
                for c, v in zip(['hour', 'minute'],
                                [int(i) for i in ymd.split(':')]):
                    mowutils.update_comment(self.conf['db_path'], cid, c, v)
            elif col in ('ymdhm', 'visible'):
                mowutils.update_comment(self.conf['db_path'],
                                        cid, col, int(val))
            else:
                mowutils.update_comment(self.conf['db_path'], cid, col, val)

            html = self._render('plain.txt', {'value': 'ok'})

        elif operation == 'delete_comment':
            cid = self.req.POST.get('cid').strip()
            mowutils.delete_comment(self.conf['db_path'], cid)

            self.resp.status = 303
            self.resp.location = '%s/manage/index' % self.conf['blog_root']
            
            return

        self.resp.body = html

    def _rss(self):
        with_comments = not self.req.GET.get('without_comments', False)
        if with_comments:
            cache_path = 'data/rss_with_comments'
        else:
            cache_path = 'data/rss_without_comments'

        rss = mowutils.get_cache(self.conf, cache_path)
        if not rss:
            eid_titles = mowutils.recent_eid_titles(self.conf['db_path'],
                                                 self.conf['main_len'])
            entries = []
            for eid, etitle in eid_titles:
                entries.append(mowutils.get_entry(self.conf, eid))

            if with_comments:
                comments = mowutils.recent_comments(self.conf['db_path'],
                                                    self.conf['main_len'])
            else:
                comments = []

            rss = self._render('rss.xml',
                               {'entries': entries, 'comments': comments})

            mowutils.save_cache(self.conf, cache_path, rss)

        self.resp.body = rss
        self.resp.content_type = 'text/xml; charset=UTF-8'

    def _calendar_table(self):
        year = self.req.GET.get('year', '')
        month = self.req.GET.get('month', '')

        if year.isdigit() and month.isdigit():
            cache_path = 'data/cal_%(year)s_%(month)s' % locals()
            cal = mowutils.get_cache(self.conf, cache_path)
            if not cal:
                cal = mowutils.cal_table(self.conf, year, month)
                mowutils.save_cache(self.conf, cache_path,
                                    cal.encode('utf-8', 'ignore'))
        else:
            cal = mowutils.cal_table(self.conf)

        self.resp.body = cal.encode('utf-8', 'ignore')
        self.resp.content_type = 'text/plain; charset=UTF-8'
        
    def _all_tags_ul(self):
        tags = mowutils.fetch_all_tags(self.conf)
        html = self._render('all_tags_ul.html', {'tags': tags})

        self.resp.body = html
        self.resp.content_type = 'text/plain; charset=UTF-8'


    def _post_comment(self):
        comm_author = self.req.POST.get('comm_author', u'')
        comm_title = self.req.POST.get('comm_title', u'')
        comm_body = self.req.POST.get('comm_body', u'')
        eid = self.req.POST.get('eid', u'')
        comm_time = self.req.POST.get('comm_time', u'')
        pbody = self.req.POST.get('pbody', u'')

        # Hidden input validation
        eid, comm_time, pbody = (e.strip() for e in (eid, comm_time, pbody))
        if eid.isdigit and mowutils.get_entry(self.conf, eid) and comm_time and pbody:
            pass
        else:
            self._redirect_to_top()
            return

        try:
            comm_time = float(comm_time)
        except:
            self._redirect_to_top()
            return

        # Expiration
        if time.time() - int(comm_time) > 60 * 60 * 3:
            msg = 'Oops! Period to comment has expired! Write again, please.'
            self._error_page('403', msg)
            return 

        # User input validation
        author, title, body = (e.strip()
                               for e in (comm_author, comm_title, comm_body))

        if not author or not body:
            msg = ('Oops! You might miss "Name" or "Comment". '
                   'Go back and check them, please.')
            self._error_page('400', msg)
            return

        hp = mowutils.MyHTMLParser()

        c = mowutils.Comment(eid)
        c.ptime = comm_time
        c.author = hp.plain(author)
        c.title = hp.plain(title)
        c.body = hp.html(body)

        c.post(self.conf['db_path'])

        self.resp.status = 303
        self.resp.location = '%s/%s#comments' % (self.conf['blog_path'], eid)


    def _error_page(self, status = '400', msg = ''):
        try:
            self.resp.status = status
        except KeyError:
            self.resp.status = '400'

        self.resp.body = self._render('error.html',
                                      {'status': self.resp.status,
                                       'message': msg},
                                      True)

    def _name_page(self, l):
        if len(l) == 1:
            return None, 0
        elif len(l) == 2:
            return l[1], 1
        else:
            _name = l[1]
            _num = l[2]
            
            if _num.isdigit() and int(_num) > 0:
                return _name, int(_num)
            else:
                return _name, 1

application = Blog()
