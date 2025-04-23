from flask import Blueprint, render_template, redirect, url_for
from flask_login import current_user

main = Blueprint('main', __name__)

@main.route('/')
def index():
    if current_user.is_authenticated:
        if current_user.is_super_admin():
            return redirect(url_for('super_admin.dashboard'))
        elif current_user.is_admin():
            return redirect(url_for('admin.dashboard'))
        elif current_user.is_teacher():
            return redirect(url_for('teacher.dashboard'))
        elif current_user.is_student():
            return redirect(url_for('student.dashboard'))
        elif current_user.is_parent():
            return redirect(url_for('parent.dashboard'))
    
    return render_template('main/index.html')

@main.route('/about')
def about():
    return render_template('main/about.html')

@main.route('/contact')
def contact():
    return render_template('main/contact.html')