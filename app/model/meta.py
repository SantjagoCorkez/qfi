from functools import update_wrapper
import os

from sqlalchemy import create_engine, event, exc
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm.scoping import ScopedSession
from sqlalchemy.pool import StaticPool

from ..config import Config


cnf = Config.core

conn_string = cnf.get('sqlalchemy', 'conn_string')
DEBUG_RUN = cnf.getboolean('sqlalchemy', 'debug')

eng = create_engine(conn_string, convert_unicode=True, echo=DEBUG_RUN, poolclass=StaticPool)


@event.listens_for(eng, "connect")
def connect(dbapi_connection, connection_record):
    connection_record.info['pid'] = os.getpid()


@event.listens_for(eng, "checkout")
def checkout(dbapi_connection, connection_record, connection_proxy):
    pid = os.getpid()
    if connection_record.info['pid'] != pid:
        connection_record.connection = connection_proxy.connection = None
        raise exc.DisconnectionError(
            "Connection record belongs to pid %s, "
            "attempting to check out in pid %s" %
            (connection_record.info['pid'], pid)
        )


SQLAS = ScopedSession(sessionmaker(bind=eng))
""":type : sqlalchemy.orm.session.Session"""

Base = declarative_base(bind=eng)
Base.query = SQLAS.query_property()


def controlled_nested_session(action_on_inconsistency='rollback', logger=None):
    """
    Decorator that ensures that Session's nest level of a transaction state is the same on return as on enter

    :param action_on_inconsistency: either 'rollback' or 'commit' (strings) as an action to apply on session until
    the nest level reaches the outer one if they do not match
    :type action_on_inconsistency: str
    :param logger: a logging.Logger instance to log inconsistency alarms to, optional
    :type logger: logging.Logger
    """
    def decorated_view(f):
        def wrapped(*args, **kwargs):
            try:
                current_trans_parent = id(SQLAS.registry.registry.value.transaction._parent)
            except AttributeError:
                SQLAS.flush()
                current_trans_parent = id(SQLAS.registry.registry.value.transaction._parent)
            try:
                res = f(*args, **kwargs)
                return res
            except Exception:
                raise
            finally:
                nest_count = 0
                check_trans_parent = id(SQLAS.registry.registry.value.transaction._parent)
                while check_trans_parent != current_trans_parent:
                    getattr(SQLAS, action_on_inconsistency)()
                    if check_trans_parent == id(SQLAS.registry.registry.value.transaction._parent):
                        break
                    check_trans_parent = id(SQLAS.registry.registry.value.transaction._parent)
                    nest_count += 1
                if logger and nest_count:
                    logger.warning("Transaction nested state detected in outer scope: level %s", nest_count)

        return update_wrapper(wrapped, f)

    return decorated_view
