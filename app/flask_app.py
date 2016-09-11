from logging import config as logconfig, getLogger
import os
from flask import Flask
from flask_principal import identity_changed, identity_loaded, Principal, RoleNeed, UserNeed
from flask_login import LoginManager

from app.controller.admin import AdminBlueprint
from app.controller.index import IndexBlueprint
from app.controller.signin import SignInBlueprint
from app.init_db import init_db
from app.model.meta import SQLAS, controlled_nested_session
from app.model.user import User
from .config import Config


def make_app(configname='deploy'):
    cnf = dict()
    section = 'flask_%s' % configname
    for k in Config.core.options(section):
        typename, var = k.split('_', 1)
        val = getattr(Config.core, 'get%s' % typename)(section, k)
        cnf[var.upper()] = val

    logconfig.fileConfig(Config.ABSPATHS['core'])

    app = Flask('qualify_friend_inviter', root_path=os.path.dirname(os.path.abspath(__file__)))
    app.logger_name = 'root'

    app.config.update(**cnf)

    getLogger('sqlalchemy.engine.base.Engine').disabled = not app.config['DEBUG']
    getLogger('sqlalchemy.orm.mapper.Mapper').disabled = not app.config['DEBUG']
    getLogger('mail').disabled = app.config['TESTING']

    # app._logger = getLogger('root')

    # app.session_interface = WebSessionInterface()

    app.register_blueprint(IndexBlueprint)
    app.register_blueprint(AdminBlueprint)
    app.register_blueprint(SignInBlueprint)

    login_manager = LoginManager(app)
    login_manager.login_view = 'Auth.index'

    Principal(app)

    @login_manager.user_loader
    @controlled_nested_session(logger=app.logger)
    def get_user(user_id):
        return SQLAS.query(User).get(user_id)

    @identity_loaded.connect_via(app)
    @identity_changed.connect_via(app)
    def on_identity_event(sender, identity):
        """
        :type identity: flask_principal.Identity
        """
        identity.provides.clear()
        if identity.id:
            identity.user = SQLAS.query(User).get(identity.id)
            if not identity.user:
                return
            identity.provides.add(UserNeed(identity.id))
            if identity.user.type == User.Type.ADMIN:
                identity.provides.add(RoleNeed('admin'))

    @app.before_first_request
    def initialize_db():
        if Config.core.getboolean('sqlalchemy', 'init_db_on_run'):
            init_db()

    return app
