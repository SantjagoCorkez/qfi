import hashlib
from app.model.invite import Invite
from app.model.meta import Base, SQLAS
from app.model.user import User
from app.model.session import DBSession


def init_db():
    Base.metadata.create_all(tables=[User.__table__, DBSession.__table__, Invite.__table__])
    adm = User()
    adm.name = u'admin'
    adm.password = unicode(hashlib.sha256('derpasswort').hexdigest())
    adm.email = u'admin@qfi.test'
    adm.type = User.Type.ADMIN
    SQLAS.add(adm)
    SQLAS.flush()
    SQLAS.commit()
