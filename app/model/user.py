import hashlib
from flask_login import UserMixin
from sqlalchemy import Column, Integer, Unicode

from app.model.meta import Base


class User(UserMixin, Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    name = Column(Unicode, nullable=False, index=True)
    password = Column(Unicode, nullable=False)
    email = Column(Unicode, nullable=False, index=True)
    type = Column(Integer, nullable=False, default=0)

    class Type(object):
        REGULAR = 0
        ADMIN = 1

    def is_authenticated(self):
        return self.id is not None and self.id > 0

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    @property
    def pwd(self):
        return self.password

    @pwd.setter
    def pwd(self, v):
        self.password = unicode(hashlib.sha256(v).hexdigest())
