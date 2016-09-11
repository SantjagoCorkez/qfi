import hashlib
from unittest import TestCase
from app.flask_app import make_app
from app.model.invite import Invite
from app.model.meta import SQLAS
from app.model.user import User


class AuthTestCase(TestCase):
    def setUp(self):
        self.app = make_app('testing')
        self.client = self.app.test_client()

    def test_01_unauth_page(self):
        rv = self.client.get('/')
        assert 'SignIn please' in rv.data

    def test_02_auth_page(self):
        rv = self.login('admin', 'derpasswort')
        assert '<button type="submit">SignOut</button>' in rv.data

    def test_03_logout_page(self):
        rv = self.logout()
        assert 'SignIn please' in rv.data

    def test_04_invite_page_restricted(self):
        rv = self.client.get('/admin', follow_redirects=True)
        assert 'This is highly restricted area' in rv.data

    def test_05_invite_page_permitted(self):
        self.login('admin', 'derpasswort')
        rv = self.client.get('/admin', follow_redirects=True)
        assert '<button type="submit">Send invite</button>' in rv.data

    def test_06_send_invite_empty_email(self):
        self.login('admin', 'derpasswort')
        rv = self.client.post('/admin/send_invite', data=dict(), follow_redirects=True)
        assert 'Email field cannot be empty' in rv.data

    def test_07_send_invite_valid(self):
        self.login('admin', 'derpasswort')
        rv = self.client.post('/admin/send_invite', data=dict(
            email='foo@bar.baz'
        ), follow_redirects=True)
        assert 'Invite successfully sent' in rv.data

        invite = SQLAS.query(Invite).filter(Invite.email == u'foo@bar.baz').first()
        assert invite
        assert invite.id
        assert invite.user_id is None

    def test_08_send_invite_existing(self):
        self.login('admin', 'derpasswort')
        rv = self.client.post('/admin/send_invite', data=dict(
            email='foo@bar.baz'
        ), follow_redirects=True)
        assert 'Invite already sent to this user' in rv.data

    def test_09_invite_url_page(self):
        self.login('admin', 'derpasswort')
        self.client.post('/admin/send_invite', data=dict(
            email='foo@bar.baz'
        ), follow_redirects=True)
        self.logout()

        invite = SQLAS.query(Invite).filter(Invite.email == u'foo@bar.baz').first()

        rv = self.client.get('/signin/{invite_id}'.format(invite_id=invite.id), follow_redirects=True)
        assert '<input type="hidden" name="invite_id" value="{invite_id}"/>'.format(invite_id=invite.id) in rv.data

    def test_10_invite_url_invalid(self):
        rv = self.client.get('/signin/{invite_id}'.format(invite_id='foo'), follow_redirects=True)
        assert '<p>The invite you provided does not exist</p>' in rv.data

    def test_11_invite_commit_bad(self):
        self.login('admin', 'derpasswort')
        self.client.post('/admin/send_invite', data=dict(
            email='foo@bar.baz'
        ), follow_redirects=True)
        self.logout()

        invite = SQLAS.query(Invite).filter(Invite.email == u'foo@bar.baz').first()

        rv = self.client.post('/signin/commit', data=dict(
            invite_id='foo'
        ), follow_redirects=True)
        assert '<p>The invite you provided does not exist</p>' in rv.data

        rv = self.client.post('/signin/commit', data=dict(
            invite_id=invite.id
        ), follow_redirects=True)
        assert 'You have missed some parameters' in rv.data

    def test_12_invite_commit_good(self):
        self.login('admin', 'derpasswort')
        self.client.post('/admin/send_invite', data=dict(
            email='foo@bar.baz'
        ), follow_redirects=True)
        self.logout()

        invite = SQLAS.query(Invite).filter(Invite.email == u'foo@bar.baz').first()

        rv = self.client.post('/signin/commit', data=dict(
            invite_id=invite.id,
            name='fooUser',
            password='fooPass'
        ), follow_redirects=True)
        assert '<button type="submit">SignOut</button>' in rv.data

        invite = SQLAS.query(Invite).filter(Invite.email == u'foo@bar.baz').first()
        assert invite.user_id is not None

        user = SQLAS.query(User).filter(User.name == u'fooUser').first()
        assert user
        assert user.id == invite.user_id
        assert user.password == unicode(hashlib.sha256('fooPass').hexdigest())

    def login(self, user, password):
        return self.client.post('/login', data=dict(
            login=user,
            password=password
        ), follow_redirects=True)

    def logout(self):
        return self.client.get('/logout', follow_redirects=True)
