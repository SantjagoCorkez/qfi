from functools import wraps
from flask import Blueprint, render_template, request, flash, redirect, url_for, current_app
from flask_login import current_user
from sqlalchemy.exc import SQLAlchemyError
from app.mail import MailSender
from app.model.invite import Invite
from app.model.meta import SQLAS
from app.model.user import User

AdminBlueprint = Blueprint('Admin', __name__, url_prefix='/admin')


def access_restrictor(f):
    @wraps(f)
    def check_and_call(*args, **kwargs):
        if current_user.is_anonymous or current_user.type != User.Type.ADMIN:
            return render_template('admin/no_access.html')
        return f(*args, **kwargs)

    return check_and_call


class Admin(object):

    @staticmethod
    @AdminBlueprint.route('/')
    @access_restrictor
    def index():
        return render_template('admin/index.html')

    @staticmethod
    @AdminBlueprint.route('/send_invite', methods=('POST',))
    @access_restrictor
    def send_invite():
        email = request.form.get('email', None, type=unicode)

        if not email:
            flash('Email field cannot be empty', 'error')
            return redirect(url_for('.index'))

        if SQLAS.query(Invite.id).filter(Invite.email == email).first():
            flash('Invite already sent to this user', 'error')
            return redirect(url_for('.index'))

        existing = SQLAS.query(User).filter(User.email == email).first()
        if existing:
            flash('User with the same email already exists')
            return redirect(url_for('.index'))

        invite = Invite()
        invite.email = email

        try:
            SQLAS.add(invite)
            SQLAS.flush()
            SQLAS.commit()

            MailSender.send_invite(email, unicode(invite.id))
            flash('Invite successfully sent', 'success')
        except SQLAlchemyError as se:
            current_app.logger.exception(se)
            flash('Error occurred while sending an invite', 'error')

        return redirect(url_for('.index'))
