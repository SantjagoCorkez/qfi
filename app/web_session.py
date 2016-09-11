import json
from datetime import timedelta
from uuid import uuid4

from flask import request
from sqlalchemy.sql.functions import now
from werkzeug.datastructures import CallbackDict
from flask.sessions import SessionInterface, SessionMixin

from app.model.meta import SQLAS
from app.model.session import DBSession


class WebSession(CallbackDict, SessionMixin):
    def __init__(self, initial=None, sid=None, new=False):
        def on_update(s):
            s.modified = True

        CallbackDict.__init__(self, initial, on_update)
        self.sid = sid
        self.new = new
        self.modified = False


class WebSessionInterface(SessionInterface):
    serializer = json
    session_class = WebSession

    @staticmethod
    def generate_sid():
        return str(uuid4())

    # noinspection PyMethodMayBeStatic
    def get_expiration_time(self, app, session):
        if session.permanent:
            return app.permanent_session_lifetime
        return timedelta(days=1)

    def open_session(self, app, req):
        """

        :type app: flask.Flask
        :type req: flask.Request
        :rtype: dict
        """
        sid = request.cookies.get(app.session_cookie_name)
        if not sid:
            sid = self.generate_sid()
            return self.session_class(sid=sid, new=True)
        val = SQLAS.query(DBSession).filter(DBSession.id == sid, DBSession.valid_until > now()).first()
        if val is not None:
            data = self.serializer.loads(val.data)
            if 'ip' in data and data['ip'] != req.remote_addr:
                return self.session_class(sid=self.generate_sid(), new=True)
            return self.session_class(data, sid=sid)
        return self.session_class(sid=sid, new=True)

    def save_session(self, app, session, response):
        if 'ip' not in session:
            session['ip'] = request.remote_addr
        if not session:
            return
        domain = self.get_cookie_domain(app)
        exp = self.get_expiration_time(app, session)
        cookie_exp = self.get_expiration_time(app, session)
        val = self.serializer.dumps(dict(session))
        self.redis.setex(self.prefix + session.sid, val,
                         int(redis_exp.total_seconds()))
        response.set_cookie(app.session_cookie_name, session.sid,
                            expires=cookie_exp, httponly=True,
                            domain=domain)
