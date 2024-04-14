import os
import main
import unittest
import tempfile


class CommunityTestCase(unittest.TestCase):

    def setUp(self):
        self.db_fd, main.app.config['DATABASE'] = tempfile.mkstemp()
        main.app.config['TESTING'] = True
        self.app = main.app.test_client()
        main.init_db()

    def tearDown(self):
        os.close(self.db_fd)
        os.unlink(main.app.config['DATABASE'])

    def test_empty_db(self):
        rv = self.app.get('/')
        assert 'No entries here so far' in rv.data.decode('utf-8')

    def login(self, username, password):
        return self.app.post('/login', data=dict(
            username=username,
            password=password
        ), follow_redirects=True)

    def logout(self):
        return self.app.get('/logout', follow_redirects=True)

    def test_login_logout(self):
        rv = self.login('admin', 'dummy')
        assert 'You were logged in' in rv.data.decode('utf-8')
        rv = self.logout()
        assert 'You were logged out' in rv.data.decode('utf-8')
        rv = self.login('adminx', 'default')
        assert 'Invalid username' in rv.data.decode('utf-8')
        rv = self.login('admin', 'defaultx')
        assert 'Invalid username or password' in rv.data.decode('utf-8')

    def test_messages(self):
        self.login('admin', 'dummy')
        rv = self.app.post('/add', data=dict(
            title='<Hello>',
            text='<strong>HTML</strong> allowed here'
        ), follow_redirects=True)
        assert 'No entries here so far' not in rv.data.decode('utf-8')
        assert '&lt;Hello&gt;' in rv.data.decode('utf-8')
        assert '<strong>HTML</strong> allowed here' in rv.data.decode('utf-8')


if __name__ == '__main__':
    unittest.main()
