#!/usr/bin/env python
# -*- coding: utf-8 -*-

from datetime import datetime
import sqlite3
import sys

def _migrate_entries(ver1, ver2):
    _select = (
        'SELECT eid, title, subtitle, body, extend, '
        '       year, month, day, hour, minute '
        'FROM entries ORDER BY eid;')
    _insert = 'INSERT INTO entries VALUES(?, ?, ?, ?, ?, ?, ?);'
    _counter = 0

    con1 = sqlite3.connect(ver1)
    con2 = sqlite3.connect(ver2)
    cur1 = con1.cursor()
    cur2 = con2.cursor()

    for eid, title, subtitle, body, extend, \
        year, month, day, hour, minute in cur1.execute(_select):

        _counter += 1
        posted_at = datetime(year, month, day, hour, minute)
        t = (eid, 1, title, subtitle, body, extend, posted_at)
        cur2.execute(_insert, t)
        con2.commit()
        print('.', end = '', flush = True)

    con1.close()
    con2.close()

    print('\n migrated %d entries' % _counter)


def _migrate_comments(ver1, ver2):
    _select = (
        'SELECT ROWID, eid, author, title, body, '
        '       year, month, day, hour, minute '
        'FROM comments ORDER BY ROWID;')
    _insert = 'INSERT INTO comments VALUES(?, ?, ?, ?, ?, ?);'
    _counter = 0

    con1 = sqlite3.connect(ver1)
    con2 = sqlite3.connect(ver2)
    cur1 = con1.cursor()
    cur2 = con2.cursor()

    for comment_id, entry_id, author_name, title, body, \
        year, month, day, hour, minute in cur1.execute(_select):

        _counter += 1
        posted_at = datetime(year, month, day, hour, minute)
        t = (comment_id, entry_id, author_name, title, body, posted_at)
        cur2.execute(_insert, t)
        con2.commit()
        print('.', end = '', flush = True)

    con1.close()
    con2.close()

    print('\n migrated %d comments' % _counter)


def _migrate_tags(ver1, ver2):
    _select = 'SELECT eid, name FROM tags;'
    _insert = 'INSERT INTO tags VALUES(?, ?, ?);'
    _counter = 0

    con1 = sqlite3.connect(ver1)
    con2 = sqlite3.connect(ver2)
    cur1 = con1.cursor()
    cur2 = con2.cursor()

    for entry_id, label in cur1.execute(_select):

        _counter += 1
        cur2.execute(_insert, (_counter, entry_id, label))
        con2.commit()
        print('.', end = '', flush = True)

    con1.close()
    con2.close()

    print('\n migrated %d tags' % _counter)


def _main(ver1, ver2):
    _migrate_entries(ver1, ver2)
    _migrate_comments(ver1, ver2)
    _migrate_tags(ver1, ver2)


if __name__ == '__main__':
    if len(sys.argv) == 3:
        _main(sys.argv[1], sys.argv[2])
    else:
        sys.exit('Usage: %s db_ver1 db_ver2')
