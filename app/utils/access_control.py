from functools import wraps
from flask import abort, flash, redirect, url_for
from flask_login import current_user

def role_required(*roles):
    """
    Decorator for views that checks whether a user has a particular role.
    If the user doesn't have any of the required roles, a 403 error is returned.
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                flash('Please log in to access this page.', 'warning')
                return redirect(url_for('auth.login'))
            
            has_role = False
            for role in roles:
                if current_user.has_role(role):
                    has_role = True
                    break
            
            if not has_role:
                abort(403)
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def super_admin_required(f):
    """Decorator for views that require super admin role."""
    return role_required('super_admin')(f)

def admin_required(f):
    """Decorator for views that require admin role."""
    return role_required('admin', 'super_admin')(f)

def teacher_required(f):
    """Decorator for views that require teacher role."""
    return role_required('teacher')(f)

def student_required(f):
    """Decorator for views that require student role."""
    return role_required('student')(f)

def parent_required(f):
    """Decorator for views that require parent role."""
    return role_required('parent')(f)

def school_access_required(school_id):
    """
    Checks if the current user has access to the specified school.
    Super admins have access to all schools.
    Other users must belong to the specified school.
    """
    if current_user.is_authenticated:
        if current_user.is_super_admin():
            return True
        return current_user.school_id == school_id
    return False