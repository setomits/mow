# -*- coding: utf-8 *-

from datetime import datetime
import unittest

from mow.models import db
from mow.models import Entry, Tag, Comment, User

class _TestCase(unittest.TestCase):
    def setUp(self):
        db.create_all()

    def tearDown(self):
        db.drop_all()


class TestUser(_TestCase):
    NAME = 'mits'

    def setUp(self):
        super(TestUser, self).setUp()
        self.user = User(TestUser.NAME).save()

    def test_user(self):
        self.assertEqual(self.user.name, TestUser.NAME)


class TestEntry(_TestCase):
    TITLE = 'test title'
    SUBTITLE = 'test subtitle'
    BODY = ('Lorem ipsum dolor sit amet, consectetur adipisicing elit, sed do '
            'eiusmod tempor incididunt ut labore et dolore magna aliqua. '
            'Ut enim ad minim veniam, quis nostrud exercitation ullamco ')
    EXTEND = ('laboris nisi ut aliquip ex ea commodo consequat. Duis aute '
              'irure dolor in reprehenderit in voluptate velit esse cillum '
              'dolore eu fugiat nulla pariatur. Excepteur sint occaecat ')

    def setUp(self):
        super(TestEntry, self).setUp()
        User(TestUser.NAME).save()

    def test_create_entry(self):
        _before = datetime.now()
        entry = Entry(1, TestEntry.TITLE, TestEntry.SUBTITLE,
                      TestEntry.BODY, TestEntry.EXTEND).save()
        _after = datetime.now()
        Tag(1, TestTag.LABEL1).save()
        Tag(1, TestTag.LABEL2).save()

        self.assertEqual(entry.title, TestEntry.TITLE)
        self.assertEqual(entry.subtitle, TestEntry.SUBTITLE)
        self.assertEqual(entry.body, TestEntry.BODY)
        self.assertEqual(entry.extend, TestEntry.EXTEND)
        self.assertTrue(_before < entry.posted_at < _after)

        self.assertEqual(entry.author.name, TestUser.NAME)

        self.assertEqual(len(entry.tags), 2)
        self.assertEqual(entry.tags[0].label, TestTag.LABEL1)
        self.assertEqual(entry.tags[1].label, TestTag.LABEL2)


class TestTag(_TestCase):
    LABEL1 = 'test tag 1'
    LABEL2 = 'test tag 2'

    def setUp(self):
        super(TestTag, self).setUp()
        User(TestUser.NAME).save()

        self.entry1 = Entry(1, TestEntry.TITLE, TestEntry.SUBTITLE,
                            TestEntry.BODY, TestEntry.EXTEND).save()
        self.entry2 = Entry(1, TestEntry.TITLE, TestEntry.SUBTITLE,
                            TestEntry.BODY, TestEntry.EXTEND).save()
                            
        self.tag1 = Tag(entry_id = 1, label = TestTag.LABEL1).save()
        self.tag2 = Tag(entry_id = 1, label = TestTag.LABEL2).save()
        self.tag3 = Tag(entry_id = 2, label = TestTag.LABEL1).save()

    def test_tagged_entry(self):
        entries = Tag.entries(label = TestTag.LABEL1, page = 1, limit = 100)
        self.assertEqual(len(entries), 2)
        self.assertEqual(entries[0], self.entry2)
        self.assertEqual(entries[1], self.entry1)

        entries = Tag.entries(label = TestTag.LABEL2, page = 1, limit = 100)
        self.assertEqual(len(entries), 1)
        self.assertEqual(entries[0], self.entry1)


class TestComment(_TestCase):
    TITLE = 'test comment title'
    BODY = ('cupidatat non proident, sunt in culpa qui officia deserunt '
            'mollit anim id est laborum.')
    COMMENTER_NAME = 'foo'

    def setUp(self):
        super(TestComment, self).setUp()
        User(TestUser.NAME).save()
        self.entry = Entry(1, TestEntry.TITLE, TestEntry.SUBTITLE, 
                           TestEntry.BODY, TestEntry.EXTEND).save()
        
    def test_create_comment(self):
        _before = datetime.now()
        comment = Comment(1, TestComment.COMMENTER_NAME,
                          TestComment.TITLE, TestComment.BODY).save()
        _after = datetime.now()

        self.assertEqual(comment.author_name, TestComment.COMMENTER_NAME)
        self.assertEqual(comment.title, TestComment.TITLE)
        self.assertEqual(comment.body, TestComment.BODY)
        self.assertTrue(_before < comment.posted_at < _after)
        self.assertEqual(comment.entry, self.entry)

if __name__ == '__main__':
    unittest.main()
