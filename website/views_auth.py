from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_user, login_required, logout_user, current_user
from .models import User
from werkzeug.security import generate_password_hash, check_password_hash
from . import db #imports database 'db' from the current directory defined in __init__.py

ADMINS = {
    "tylerjmeier1@gmail.com",
    "teierjmyler1@gmail.com"
}


views_auth = Blueprint('views_auth', __name__)

@views_auth.route('/login', methods=['GET', 'POST']) #by default, it only accepts HTTP get requests
def login():
    data = request.form

    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user = User.query.filter_by(email=email).first()


        if user:
            #if the user exists, checks the password hash with the entered password
            if check_password_hash(user.password, password):
                flash('Welcome, '+user.firstName+'!', category='success')
                login_user(user, remember=True) #using flask_login, remembers the user is logged in for the session


                #checks list of admin emails for the entered email to give admin status
                if (email in ADMINS):
                    user.is_admin = True
                else:
                    user.is_admin = False

                return redirect(url_for('views.home'))
            else:
                flash('Incorrect credentials.', category='error')
        else:
            flash('Incorrect credentials.', category='error')
                

    return render_template("login.html", user=current_user)



@views_auth.route('/create-account', methods=['GET', 'POST'])
def create_account():

    data = request.form

    if request.method == 'POST':
        email = request.form.get('email')
        firstName = request.form.get('first')
        lastName = request.form.get('last')
        password = request.form.get('password')
        passwordConfirm = request.form.get('password-confirm')
        
        
        user = User.query.filter_by(email=email).first()
        


        if len(email) < 4:
            flash('Email must be at least 4 characters.', category='error')
            
        elif len(firstName) < 2:
            flash('First name must be at least 2 characters.', category='error')
            
        elif len(lastName) < 2:
            flash('Last name must be at least 2 characters.', category='error')
            
        elif len(password) < 7:
            flash('Password must be at least 7 characters.', category='error')
            
        elif password != passwordConfirm:
            flash('The confirmed password must match.', category='error')
            
        elif user:
            flash('An account with that email already exists.', category='error')
            
        else:
            
            #checks list of admin emails for the entered email to give admin status
            if (email in ADMINS):
                is_admin = True
            else:
                is_admin = False

            new_user = User(email=email, firstName=firstName, lastName=lastName, password=generate_password_hash(password), is_admin=is_admin)

            db.session.add(new_user)
            db.session.commit()

            flash('Account successfully created! Welcome, '+new_user.firstName+'!', category='success')

            login_user(new_user, remember=True) #using flask_login, when you create an account, logs you in automatically

            
            return redirect(url_for('views.home')) #safer than just typing in redirect("/") incase the url ever changes

            #if all these checks pass, we can add the user to the database

    return render_template("create_account.html", user=current_user)



@views_auth.route('/logout')
@login_required
def logout():
    logout_user() #flask_login function to log out the current user
    return redirect(url_for('views_auth.login'))