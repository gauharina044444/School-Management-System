from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, current_user, login_required
from app.models.user import User
from app import db
from app.forms.auth_forms import LoginForm, PasswordChangeForm

auth = Blueprint('auth', __name__, url_prefix='/auth')

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        
        if user and user.check_password(form.password.data):
            if not user.is_active:
                flash('Your account is inactive. Please contact an administrator.', 'danger')
                return render_template('auth/login.html', form=form)
            
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            
            flash(f'Welcome back, {user.first_name}!', 'success')
            
            if next_page:
                return redirect(next_page)
            else:
                return redirect(url_for('main.index'))
        else:
            flash('Login unsuccessful. Please check email and password.', 'danger')
    
    return render_template('auth/login.html', form=form)

@auth.route('/logout')
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('main.index'))

@auth.route('/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    form = PasswordChangeForm()
    
    if form.validate_on_submit():
        if current_user.check_password(form.current_password.data):
            current_user.set_password(form.new_password.data)
            db.session.commit()
            flash('Your password has been updated!', 'success')
            return redirect(url_for('main.index'))
        else:
            flash('Current password is incorrect.', 'danger')
    
    return render_template('auth/change_password.html', form=form)