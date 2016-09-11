from uuid import uuid4

from sqlalchemy import Column, Unicode, DateTime

from app.model.meta import Base


class DBSession(Base):
    __tablename__ = 'sessions'

    id = Column(Unicode, primary_key=True, nullable=False, default=lambda: unicode(uuid4()))
    data = Column(Unicode, nullable=False)
    valid_until = Column(DateTime, nullable=False, index=True)
