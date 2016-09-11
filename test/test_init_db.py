import hashlib
import unittest
from app.flask_app import make_app
from app.model.invite import Invite
from app.model.meta import SQLAS
from app.model.user import User


class InitDBTestCase(unittest.TestCase):
    def setUp(self):
        self.app = make_app('testing').test_client()
        self.app.get('/')

    def test_models_created(self):
        SQLAS.query(User).first()
        SQLAS.query(Invite).first()

    def test_default_admin_created(self):
        u = SQLAS.query(User).filter(User.name == u'admin').first()

        self.assertIsNotNone(u)
        self.assertIsNotNone(u.id)
        self.assertEqual(u.password, hashlib.sha256('derpasswort').hexdigest())
