import hashlib
from flask import Blueprint, request, current_app, redirect, url_for, flash, render_template
from flask_login import login_user, logout_user, current_user
from flask_principal import identity_changed, Identity, AnonymousIdentity
from app.model.meta import SQLAS
from app.model.user import User

IndexBlueprint = Blueprint('Index', __name__, url_prefix='')


class Index(object):

    @staticmethod
    @IndexBlueprint.route('/')
    def index():
        if current_user.is_anonymous:
            return render_template('login_form.html')
        return render_template('index.html')

    @staticmethod
    @IndexBlueprint.route('/logout')
    def logout():
        logout_user()
        identity_changed.send(current_app._get_current_object(), identity=AnonymousIdentity())
        return redirect(url_for('.index'))

    @staticmethod
    @IndexBlueprint.route('/login', methods=('POST',))
    def login():
        login = request.form.get('login', None, type=unicode)
        password = request.form.get('password', None, type=unicode)

        if not login or not password:
            flash('Neither login nor password could be empty', 'error')
            return redirect(url_for('.index'))

        pwd = unicode(hashlib.sha256(password).hexdigest())
        user = SQLAS.query(User)\
            .filter(User.name == login, User.password == pwd)\
            .first()
        """:type: User"""
        if not user:
            flash('Login and/or password are incorrect', 'error')
            return redirect(url_for('.index'))

        login_user(user)
        identity_changed.send(current_app._get_current_object(), identity=Identity(user.id))

        return redirect(request.args.get('next') or url_for('.index'))
