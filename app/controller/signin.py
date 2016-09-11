from flask import Blueprint, request, render_template, flash, redirect, url_for, current_app
from flask_login import login_user
from flask_principal import identity_changed, Identity
from sqlalchemy import or_
from app.model.invite import Invite
from app.model.meta import SQLAS
from app.model.user import User

SignInBlueprint = Blueprint('SignIn', __name__, url_prefix='/signin')


class SignIn(object):

    @staticmethod
    @SignInBlueprint.route('/<invite_id>')
    def index(invite_id):
        invite = SQLAS.query(Invite).filter(Invite.id == invite_id, Invite.user_id.is_(None)).first()
        if not invite:
            return render_template('signin/not_found.html')

        return render_template('signin/index.html')

    @staticmethod
    @SignInBlueprint.route('/commit', methods=('POST',))
    def commit():
        name = request.form.get('name', type=unicode)
        password = request.form.get('password', type=unicode)

        invite_id = request.form.get('invite_id', type=unicode)

        if not invite_id:
            return render_template('signin/not_found.html')

        if not all((name, password)):
            flash('You have missed some parameters')
            return redirect(url_for('.index', invite_id=invite_id))

        invite = SQLAS.query(Invite).filter(Invite.id == invite_id, Invite.user_id.is_(None)).first()
        if not invite:
            return render_template('signin/not_found.html')

        existing = SQLAS.query(User).filter(or_(User.name == name, User.email == invite.email)).first()
        if existing:
            flash('User with the same name/or email already exists')
            return redirect(url_for('.index'))

        user = User()
        user.name = name
        user.email = invite.email
        user.pwd = password
        user.type = User.Type.REGULAR

        SQLAS.add(user)
        SQLAS.flush()
        invite.user_id = user.id
        SQLAS.flush()
        SQLAS.commit()

        login_user(user)
        identity_changed.send(current_app._get_current_object(), identity=Identity(user.id))
        return redirect(url_for('Index.index'))
