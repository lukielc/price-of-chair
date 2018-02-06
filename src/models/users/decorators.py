from functools import wraps
from flask import session, url_for, redirect, request
from src.app import app


def requires_login(func):
    @wraps(func)
    def decorated_fuction(*args, **kwargs):
        if 'email' not in session.keys() or session['email'] is None:
            return redirect(url_for('users.login_user', next=request.path))
        return func(*args, **kwargs)
    return decorated_fuction

def requires_admin_permission(func):
    @wraps(func)
    def decorated_fuction(*args, **kwargs):
        if 'email' not in session.keys() or session['email'] is None:
            return redirect(url_for('users.login_user', next=request.path))
        if session['email'] not in app.config['ADMINS']:
            return redirect(url_for('users.login_user'))
        return func(*args, **kwargs)
    return decorated_fuction