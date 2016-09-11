from uuid import uuid4
from sqlalchemy import Column, Unicode, Integer
from app.model.meta import Base


class Invite(Base):
    __tablename__ = 'invites'

    id = Column(Unicode, primary_key=True, nullable=False)
    email = Column(Unicode, nullable=False, index=True)
    user_id = Column(Integer, nullable=True, index=False)

    def __init__(self):
        self.id = unicode(uuid4())
