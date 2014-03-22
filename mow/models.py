#!/usr/bin/env python

from datetime import datetime, timedelta
from hashlib import sha1

from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.sql import func
from flask import g
from flask.ext.sqlalchemy import SQLAlchemy

from mow import app

db = SQLAlchemy(app)

def rollback():
    db.session.rollback()

def remove_session():
    db.session.remove()

class MyMixin:
    id = db.Column(db.Integer, primary_key = True)

    def __eq__(self, other):
        return True if self.id == other.id else False

    def __ne__(self, other):
        return not self.__eq__(other)

    def clear_memcache(self):
        g.mc.delete('%s_%d' % (self.__class__.__name__, self.id))

    def delete(self):
        self.clear_memcache()
        db.session.delete(self)
        db.session.commit()

    def save(self, clear_cache = True):
        if clear_cache:
            self.clear_memcache()

        db.session.add(self)
        db.session.commit()
        return self

    @classmethod
    def get_by_id(cls, id):
        return cls.query.filter(cls.id == id).first()


class Entry(db.Model, MyMixin):
    __tablename__ = 'entries'

    author_id = db.Column(db.Integer)
    title = db.Column(db.String)
    subtitle = db.Column(db.String)
    body = db.Column(db.Text)
    extend = db.Column(db.Text)
    posted_at = db.Column(db.DateTime)

    def __init__(self, author_id, title = '', subtitle = '',
                 body = '', extend = ''):
        self.author_id = author_id
        self.title = title
        self.subtitle = subtitle
        self.body = body
        self.extend = extend
        self.posted_at = datetime.now()

    def save(self, clear_cache = True):
        super(Entry, self).save(clear_cache = clear_cache)
        if clear_cache:
            g.mc.delete('Entry_archives')

    @property
    def author(self):
        return User.get_by_id(self.author_id)

    def _query_for_comments(self):
        q = Comment.query.filter(Comment.entry_id == self.id)
        return q

    @property
    def comments(self):
        return self._query_for_comments().order_by(Comment.posted_at).all()

    @property
    def n_comments(self):
        return self._query_for_comments().count()

    def _query_for_tags(self):
        q = Tag.query.filter(Tag.entry_id == self.id)
        q = q.order_by(Tag.label)

        return q

    @property
    def previous_entry(self):
        q = Entry.query.filter(Entry.posted_at < self.posted_at)
        q = q.filter(Entry.id != self.id)
        q = q.order_by(Entry.posted_at.desc())

        return q.first()

    @property
    def next_entry(self):
        q = Entry.query.filter(Entry.posted_at > self.posted_at)
        q = q.filter(Entry.id != self.id)
        q = q.order_by(Entry.posted_at)

        return q.first()

    @property
    def tags(self):
        return self._query_for_tags().all()

    @property
    def n_tags(self):
        return self._query_for_tags().count()

    @property
    def tag_labels(self):
        return ', '.join([tag.label for tag in self.tags])

    @staticmethod
    def _fetch_archives():
        archives = {}

        oldest = Entry.query.order_by(Entry.posted_at).first()
        if oldest:
            newest = Entry.query.order_by(Entry.posted_at.desc()).first()
            year = oldest.posted_at.year
            month = oldest.posted_at.month
        else:
            return archives
        
        while (year, month) <= (newest.posted_at.year, newest.posted_at.month):
            n_entries = Entry.n_month_entries(datetime(year, month, 1))

            if year not in archives:
                archives[year] = []

            archives[year].append((month, n_entries))

            if month == 12:
                year, month = year + 1, 1
            else:
                month = month + 1

        return archives

    @staticmethod
    def fetch_archives():
        mc_key = 'Entry_archives'
        value = g.mc.get(mc_key)
        if value is None:
            value = Entry._fetch_archives()
            if value:
                g.mc.set(mc_key, value)

        return value

    @staticmethod
    def fetch_recent_entries(entries_per_page = 5):
        q = Entry.query.order_by(Entry.posted_at.desc()).limit(entries_per_page)

        return q.all()

    @staticmethod
    def _query_for_day(posted_on):
        _end = posted_on + timedelta(days = 1)

        q = Entry.query.filter(Entry.posted_at >= posted_on)
        q = q.filter(Entry.posted_at < _end)

        return q

    @staticmethod
    def fetch_day_entries(posted_on, page, limit):
        q = Entry._query_for_day(posted_on)
        q = q.order_by(Entry.posted_at.desc())
        q = q.limit(limit).offset(limit * (page - 1))

        return [entry for entry in q]

    @staticmethod
    def n_day_entries(posted_on):
        return Entry._query_for_day(posted_on).count()

    @staticmethod
    def _query_for_month(posted_in):
        if posted_in.month == 12:
            _end = posted_in.replace(year = posted_in.year + 1, month = 1)
        else:
            _end = posted_in.replace(month = posted_in.month + 1)

        q = Entry.query.filter(Entry.posted_at >= posted_in)
        q = q.filter(Entry.posted_at < _end)

        return q

    @staticmethod
    def fetch_month_entries(posted_in, page, limit):
        q = Entry._query_for_month(posted_in)
        q = q.order_by(Entry.posted_at.desc())
        q = q.limit(limit).offset(limit * (page - 1))

        return [entry for entry in q]

    @staticmethod
    def n_month_entries(posted_in):
        return Entry._query_for_month(posted_in).count()

    @staticmethod
    def fetch_tagged_entries(label, page, limit):
        return Tag.entries(label, page, limit)

    def delete(self):
        for tag in self.tags:
            tag.delete()

        for comment in self.comments:
            comment.delete()

        super(Entry, self).delete()


class Tag(db.Model, MyMixin):
    __tablename__ = 'tags'

    entry_id = db.Column(db.Integer)
    label = db.Column(db.String)

    def __init__(self, entry_id, label):
        self.entry_id = entry_id
        self.label = label

    def save(self):
        super(Tag, self).save()
        g.mc.delete('Tag_counts')

    @staticmethod
    def _query_for_label(label):
        return Tag.query.filter(Tag.label == label)

    @staticmethod
    def entries(label, page, limit):
        q = Tag._query_for_label(label)
        q = q.order_by(Tag.entry_id.desc())
        q = q.limit(limit).offset(limit * (page - 1))

        return [Entry.get_by_id(tag.entry_id) for tag in q]

    @staticmethod
    def n_entries(label):
        return Tag._query_for_label(label).count()

    @staticmethod
    def _fetch_tag_counts():
        q = db.session.query(Tag.label, func.count(Tag.entry_id))
        q = q.group_by(Tag.label).order_by(Tag.label)

        return [(label, count) for label, count in q]

    @staticmethod
    def fetch_tag_counts():
        mc_key = 'Tag_counts'
        value = g.mc.get(mc_key)
        if value is None:
            value = Tag._fetch_tag_counts()
            if value:
                g.mc.set(mc_key, value)

        return value


class Comment(db.Model, MyMixin):
    __tablename__ = 'comments'

    entry_id = db.Column(db.Integer)
    author_name = db.Column(db.String)
    title = db.Column(db.String)
    body = db.Column(db.Text)
    posted_at = db.Column(db.DateTime)

    def __init__(self, entry_id, author_name, title, body):
        self.entry_id = entry_id
        self.author_name = author_name
        self.title = title
        self.body = body
        self.posted_at = datetime.now()

    def delete(self):
        self.entry.clear_memcache()
        super(Comment, self).delete()

    def save(self, clear_cache = True):
        self.entry.clear_memcache()
        if clear_cache:
            self.clear_memcache()
        super(Comment, self).save(clear_cache = clear_cache)

    @property
    def entry(self):
        return Entry.get_by_id(self.entry_id)

    @staticmethod
    def fetch_recent_comments(entries_per_page = 5):
        q = Comment.query.order_by(Comment.posted_at.desc())
        q = q.limit(entries_per_page)

        return q.all()


class User(db.Model, MyMixin):
    __tablename__ = 'users'

    name = db.Column(db.String)
    password_hash = db.Column(db.String)
    registered_at = db.Column(db.DateTime)

    def __init__(self, name, password = ''):
        self.name = name
        self.registered_at = datetime.now()
        self.password_hash = User.make_hash(password) if password else ''

    @staticmethod
    def make_hash(p):
        from hashlib import sha1
        return sha1(app.config['SECRET_KEY'].encode('utf-8') + \
                    p.encode('utf-8')).hexdigest()

    @staticmethod
    def get_by_name(n):
        return User.query.filter(User.name == n).first()

    def set_password_hash(p):
        self.password_hash = User.make_hash(p)
