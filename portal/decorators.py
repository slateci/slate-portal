from flask import redirect, request, session, url_for, flash
from functools import wraps
from portal.connect_api import get_user_id, get_instance_details, get_group_members
from portal import minislate_user

def authenticated(fn):
    """Mark a route as requiring authentication."""
    @wraps(fn)
    def decorated_function(*args, **kwargs):
        # if minislate_user:
        #     check_minislate_user()
            
        if not session.get('is_authenticated'):
            print("Authenticated decorator could not verify session")
            return redirect(url_for('login', next=request.url))

        if request.path == '/logout':
            return fn(*args, **kwargs)

        if (not session.get('name') or
                not session.get('email')) and request.path != '/profile':
            return redirect(url_for('create_profile', next=request.url))
        
        # if (not session.get('user_id') and request.path != '/profile/new'):
        #     try:
        #         user_id = get_user_id(session)
        #         session['user_id'] = user_id
        #     except:
        #         return redirect(url_for('create_profile', next=request.url))

        return fn(*args, **kwargs)
    return decorated_function


def instance_authenticated(fn):
    """Mark a route as requiring authentication."""
    @wraps(fn)
    def decorated_function(*args, **kwargs):
        instance_id = request.path.split('/')[-1]
        instance_details = get_instance_details(instance_id)

        if instance_details == 504:
            flash('The connection to {} has timed out. Please try again later.'.format(instance_id), 'warning')
            return redirect(url_for('list_instances'))

        if instance_details['kind'] == 'Error':
            message = instance_details['message']
            flash('{}'.format(message), 'warning')
            return redirect(url_for('list_instances'))

        group_name = instance_details['metadata']['group']
        group_members = get_group_members(group_name)
        group_members = group_members['items']
        group_user_ids = []

        for group_member in group_members:
            group_user_ids.append(group_member['metadata']['id'])
        
        if (not session.get('user_id') in group_user_ids):
            flash('You do not have permission to access this instance', 'warning')
            return redirect(url_for('list_instances'))

        return fn(*args, **kwargs)
    return decorated_function


def group_authenticated(fn):
    """Mark a route as requiring group authentication."""
    @wraps(fn)
    def decorated_function(*args, **kwargs):
        # if minislate_user:
        #     return fn(*args, **kwargs)
            
        group_name = request.path.split('/')[2]

        group_members = get_group_members(group_name)
        try:
            if group_members['kind'] == 'Error':
                message = group_members['message']
                flash('{}'.format(message), 'warning')
                return redirect(url_for('list_groups'))
        except:
            print("Finished querying group members")
        
        try:
            group_members = group_members['items']
        except:
            if group_members['message'] == 'Not authorized':
                flash('You do not have permission to access this group', 'warning')
                return redirect(url_for('list_groups'))
        
        group_user_ids = []

        for group_member in group_members:
            group_user_ids.append(group_member['metadata']['id'])

        if (not session.get('user_id') in group_user_ids):
            flash('You do not have permission to access this group', 'warning')
            return redirect(url_for('list_groups'))

        return fn(*args, **kwargs)
    return decorated_function


def check_minislate_user():
    try:
        # Check location of slate_portal_user file on minislate
        f = open("/slate_portal_user", "r")
        slate_portal_user = f.read().split()

        session['user_id'] = slate_portal_user[0]
        session['name'] = slate_portal_user[1]
        session['email'] = slate_portal_user[2]
        session['phone'] = slate_portal_user[3]
        session['institution'] = slate_portal_user[4]
        # session['slate_token'] = slate_portal_user[5]
        session['primary_identity'] = slate_portal_user[5]
        session['is_authenticated'] = True
        session['slate_portal_user'] = True

    except:
        session['slate_portal_user'] = False