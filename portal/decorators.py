from flask import redirect, request, session, url_for
from functools import wraps
from connect_api import get_user_id

def authenticated(fn):
    """Mark a route as requiring authentication."""
    @wraps(fn)
    def decorated_function(*args, **kwargs):
        if not session.get('is_authenticated'):
            return redirect(url_for('login', next=request.url))

        if request.path == '/logout':
            return fn(*args, **kwargs)

        if (not session.get('name') or
                not session.get('email')) and request.path != '/profile':
            return redirect(url_for('create_profile', next=request.url))
        
        if (not session.get('user_id') and request.path != '/profile/new'):
            try:
                user_id = get_user_id(session)
                session['user_id'] = user_id
            except:
                return redirect(url_for('create_profile', next=request.url))

        return fn(*args, **kwargs)
    return decorated_function
