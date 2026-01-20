# app/auth/decorators.py
from flask_login import current_user
from flask import abort
from functools import wraps

def role_required(*roles):
    def wrapper(fn):
        @wraps(fn)
        def decorated(*args, **kwargs):
            if not current_user.is_authenticated:
                abort(401)
            if not any(current_user.has_role(r) for r in roles):
                abort(403)
            return fn(*args, **kwargs)
        return decorated
    return wrapper
