# -*- coding: utf-8 -*-

import unittest

from mow.models import db, Entry, User

class TestMowServer(unittest.TestCase):
    def setUp(self):
        db.create_all()
        self.client = db.get_app().test_client()

    def tearDown(self):
        db.drop_all()

    def login(self, user_name, password):
        return self.client.post('/login', data = dict(
            user_name = user_name,
            password = password
        ), follow_redirects = True)

    def logout(self):
        return self.client.get('/logout', follow_redirects=True)


class TestUser(TestMowServer):
    USER_NAME = 'xxx'
    PASSWORD = 'password'

    def setUp(self):
        super(TestUser, self).setUp()
        User(TestUser.USER_NAME, TestUser.PASSWORD).save()

    def test_login(self):
        with self.client.session_transaction() as session:
            self.assertNotIn('user_name', session)

        self.login(TestUser.USER_NAME, TestUser.PASSWORD)
        with self.client.session_transaction() as session:
            self.assertEqual(session['user_name'], TestUser.USER_NAME)

    def test_login_required(self):
        resp = self.client.get('/admin')
        self.assertIn('/login', resp.location)


class TestEntry(TestMowServer):
    TITLE = 'テストエントリータイトル'
    SUBTITLE = 'テストエントリーサブタイトル'
    BODY = 'エントリー本文' * 20
    EXTEND = 'エントリー続き' * 20

    def setUp(self):
        super(TestEntry, self).setUp()
        User(TestUser.USER_NAME, TestUser.PASSWORD).save()
        Entry(author_id = 1, 
              title = TestEntry.TITLE,
              subtitle = TestEntry.SUBTITLE,
              body = TestEntry.BODY,
              extend = TestEntry.EXTEND).save()

    def test_entry(self):
        resp = self.client.get('/1')
        self.assertEqual(resp.status_code, 200)

        resp = self.client.get('/2')
        self.assertEqual(resp.status_code, 404)

    def test_post_entry(self):
        self.login(TestUser.USER_NAME, TestUser.PASSWORD)
        resp = self.client.post('/admin/entry/post', data = dict(
            user_name = TestUser.USER_NAME,
            title = TestEntry.TITLE,
            subtitle = TestEntry.SUBTITLE,
            body = TestEntry.BODY,
            extend = TestEntry.EXTEND
        ))
        self.assertIn('entry_id=2', resp.location)
                        
        resp = self.client.get('/2')
        self.assertEqual(resp.status_code, 200)

    def test_fail_to_post_entry(self):
        self.login(TestUser.USER_NAME, TestUser.PASSWORD)
        resp = self.client.post('/admin/entry/post', data = dict(
            user_name = TestUser.USER_NAME,
            title = TestEntry.TITLE,
            subtitle = TestEntry.SUBTITLE,
            body = '',
            extend = TestEntry.EXTEND
        ))
        self.assertEqual(resp.status_code, 400)

    def test_edit_entry(self):
        self.login(TestUser.USER_NAME, TestUser.PASSWORD)
        resp = self.client.post('/admin/entry/edit', data = dict(
            user_name = TestUser.USER_NAME,
            entry_id = 1,
            title = TestEntry.TITLE + ' mod',
            subtitle = TestEntry.SUBTITLE + ' mod',
            body = TestEntry.BODY + ' mod',
            extend = TestEntry.EXTEND + ' mod'
        ))
        self.assertEqual(resp.status_code, 200)

        resp = self.client.post('/admin/entry/edit', data = dict(
            user_name = TestUser.USER_NAME,
            entry_id = 2,
            title = TestEntry.TITLE + ' mod',
            subtitle = TestEntry.SUBTITLE + ' mod',
            body = TestEntry.BODY + ' mod',
            extend = TestEntry.EXTEND + ' mod'
        ))
        self.assertEqual(resp.status_code, 400)


class TestComment(TestMowServer):
    AUTHOR_NAME = '通りすがり'
    TITLE = 'テストコメントタイトル'
    BODY = 'コメント本文' * 20

    def setUp(self):
        super(TestComment, self).setUp()
        User(TestUser.USER_NAME, TestUser.PASSWORD).save()
        Entry(author_id = 1, 
              title = TestEntry.TITLE,
              subtitle = TestEntry.SUBTITLE,
              body = TestEntry.BODY,
              extend = TestEntry.EXTEND).save()

    def test_post_comment(self):
        resp = self.client.post('/comment/post', data = dict(
            entry_id = 1,
            author_name = TestComment.AUTHOR_NAME,
            comment_title = TestComment.TITLE,
            comment_body = TestComment.BODY
        ))
        self.assertIn('/1', resp.location)

    def test_fail_to_post_comment(self):
        resp = self.client.post('/comment/post', data = dict(
            author_name = TestComment.AUTHOR_NAME,
            comment_title = TestComment.TITLE,
            comment_body = TestComment.BODY
        ))
        self.assertEqual(resp.status_code, 400)

        resp = self.client.post('/comment/post', data = dict(
            entry_id = 2,
            author_name = TestComment.AUTHOR_NAME,
            comment_title = TestComment.TITLE,
            comment_body = TestComment.BODY
        ))
        self.assertEqual(resp.status_code, 400)

        resp = self.client.post('/comment/post', data = dict(
            entry_id = 'abc',
            author_name = TestComment.AUTHOR_NAME,
            comment_title = TestComment.TITLE,
            comment_body = TestComment.BODY
        ))
        self.assertEqual(resp.status_code, 400)

        resp = self.client.post('/comment/post', data = dict(
            entry_id = 1,
            comment_title = TestComment.TITLE,
            comment_body = TestComment.BODY
        ))
        self.assertEqual(resp.status_code, 400)

        resp = self.client.post('/comment/post', data = dict(
            entry_id = 1,
            author_name = TestComment.AUTHOR_NAME,
            comment_body = TestComment.BODY
        ))
        self.assertEqual(resp.status_code, 400)

        resp = self.client.post('/comment/post', data = dict(
            entry_id = 1,
            author_name = TestComment.AUTHOR_NAME,
            comment_title = TestComment.TITLE,
        ))
        self.assertEqual(resp.status_code, 400)

    def test_edit_comment(self):
        resp = self.client.post('/comment/post', data = dict(
            entry_id = 1,
            author_name = TestComment.AUTHOR_NAME,
            comment_title = TestComment.TITLE,
            comment_body = TestComment.BODY
        ))

        self.login(TestUser.USER_NAME, TestUser.PASSWORD)
        resp = self.client.post('/admin/comment/edit', data = dict(
            comment_id = 1,
            author_name = TestComment.AUTHOR_NAME + ' mod',
            title = TestComment.TITLE + ' mod',
            body = TestComment.BODY + ' mod'
        ))
        self.assertEqual(resp.status_code, 200)

    def test_fail_to_edit_comment(self):
        resp = self.client.post('/comment/post', data = dict(
            entry_id = 1,
            author_name = TestComment.AUTHOR_NAME,
            comment_title = TestComment.TITLE,
            comment_body = TestComment.BODY
        ))

        self.login(TestUser.USER_NAME, TestUser.PASSWORD)
        resp = self.client.post('/admin/comment/edit', data = dict(
            author_name = TestComment.AUTHOR_NAME + ' mod',
            title = TestComment.TITLE + ' mod',
            body = TestComment.BODY + ' mod'
        ))
        self.assertEqual(resp.status_code, 400)

        self.login(TestUser.USER_NAME, TestUser.PASSWORD)
        resp = self.client.post('/admin/comment/edit', data = dict(
            comment_id = 2,
            author_name = TestComment.AUTHOR_NAME + ' mod',
            title = TestComment.TITLE + ' mod',
            body = TestComment.BODY + ' mod'
        ))
        self.assertEqual(resp.status_code, 400)

        self.login(TestUser.USER_NAME, TestUser.PASSWORD)
        resp = self.client.post('/admin/comment/edit', data = dict(
            comment_id = 'abc',
            author_name = TestComment.AUTHOR_NAME + ' mod',
            title = TestComment.TITLE + ' mod',
            body = TestComment.BODY + ' mod'
        ))
        self.assertEqual(resp.status_code, 400)


if __name__ == '__main__':
    unittest.main()
