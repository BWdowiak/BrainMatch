import os
import secrets
from flask import render_template, url_for, flash, redirect, request, Blueprint, current_app
from app import db
from app.forms import RegistrationForm, LoginForm, UpdateAccountForm
from app.models import User
from flask_login import login_user, current_user, logout_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash

auth = Blueprint('auth', __name__)


def save_picture(form_picture, folder):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(current_app.root_path, 'static/' + folder, picture_fn)
    form_picture.save(picture_path)
    return picture_fn

@auth.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = generate_password_hash(form.password.data)
        user = User(username=form.username.data, email=form.email.data, 
                    password_hash=hashed_password, role=form.role.data)
        db.session.add(user)
        db.session.commit()
        flash('Konto zostało utworzone!', 'success')
        return redirect(url_for('auth.login'))
    return render_template('register.html', title='Rejestracja', form=form)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.username_or_email.data).first()
        if not user:
            user = User.query.filter_by(username=form.username_or_email.data).first()
        if user and check_password_hash(user.password_hash, form.password.data):
            login_user(user, remember=True)
            return redirect(url_for('main.home'))
        else:
            flash('Błąd logowania. Sprawdź dane.', 'danger')
    return render_template('login.html', title='Logowanie', form=form)

@auth.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    form = UpdateAccountForm()
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.email = form.email.data
        current_user.role = form.role.data
        db.session.commit()
        flash('Twoje konto zostało zaktualizowane!', 'success')
        return redirect(url_for('auth.settings'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
        form.role.data = current_user.role
    return render_template('settings.html', title='Ustawienia konta', form=form)

@auth.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('main.home'))

@auth.route('/account', methods=['GET', 'POST'])
@login_required
def account():
    form = UpdateAccountForm()
    
    if form.validate_on_submit():
        if form.profile_pic.data:
            pic_file = save_picture(form.profile_pic.data, 'profile_pics')
            current_user.profile_pic = pic_file
        if form.cover_pic.data:
            cover_file = save_picture(form.cover_pic.data, 'cover_pics')
            current_user.cover_pic = cover_file

        current_user.username = form.username.data
        current_user.email = form.email.data
        current_user.first_name = form.first_name.data  
        current_user.last_name = form.last_name.data    
        current_user.bio = form.bio.data
        current_user.education = form.education.data

        db.session.commit() 
        flash('Twój profil został zaktualizowany!', 'success')
        return redirect(url_for('auth.account'))
    
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
        form.first_name.data = current_user.first_name
        form.last_name.data = current_user.last_name
        form.bio.data = current_user.bio
        form.education.data = current_user.education
    
    profile_pic = url_for('static', filename='profile_pics/' + current_user.profile_pic)
    cover_pic = url_for('static', filename='cover_pics/' + current_user.cover_pic)
    
    return render_template('account.html', title='Konto', 
                           profile_pic=profile_pic, cover_pic=cover_pic, form=form)