from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user
from .models import User, Client
from .dataprocessing import user_all_shifts_formatted, users_shifts_pd_dataframe
from . import db #imports database 'db' from the current directory defined in __init__.py

import os

from datetime import datetime



views_admin = Blueprint('views_admin', __name__)

@views_admin.route('/', methods=['GET', 'POST'])
@login_required
def home():
    if (not current_user.is_admin):
        return redirect(url_for('views.home'))
    else:
        data = request.form
        
        if request.method == 'POST':
            pass



        return render_template("admin.html", user=current_user)

@views_admin.route('/clients', methods=['GET', 'POST'])
@login_required
def clients():
    if (not current_user.is_admin):
        return redirect(url_for('views.home'))
    else:
        data = request.form

        if request.method == 'POST':
            firstName = request.form.get('first')
            lastName = request.form.get('last')
            email = request.form.get('email')
            phoneNumber = request.form.get('phone-number')
            company = request.form.get('company')

            
            client = Client.query.filter_by(email=email).first() #sees if there's already a client with that email
            


            if len(email) < 4:
                flash('Email must be at least 4 characters.', category='error')
                
            elif len(firstName) < 2:
                flash('First name must be at least 2 characters.', category='error')
                
            elif len(lastName) < 2:
                flash('Last name must be at least 2 characters.', category='error')
            
            elif len(company) < 2:
                flash('Company must be at least 2 characters.', category='error')
            
            elif len(phoneNumber) < 10:
                flash('Phone number must be at least 10 characters.', category='error')
                
            elif client:
                flash('An client with that email already exists.', category='error')
                
            else:
                

                new_client = Client(email=email, phoneNumber=phoneNumber, firstName=firstName, lastName=lastName, company=company)

                db.session.add(new_client)
                db.session.commit()

                flash('Client successfully added!', category='success')



        all_clients = Client.query.order_by(Client.lastName)

            
        return render_template("admin_clients.html", user=current_user, all_clients=all_clients)
    


@views_admin.route('/client/<int:see_client_id>')
@login_required
def client(see_client_id):
    
    if (not current_user.is_admin):
        return redirect(url_for('views.home'))
    else:
        see_client = Client.query.filter_by(id=see_client_id).first()
        return render_template("admin_see_client.html", user=current_user, see_client=see_client)

    
@views_admin.route('/users')
@login_required
def users():
    if (not current_user.is_admin):
        return redirect(url_for('views.home'))
    else:
        data = request.form
    
        all_users = User.query.order_by(User.lastName)

        return render_template("admin_users.html", user=current_user, all_users=all_users)

@views_admin.route('/user/<int:see_user_id>')
@login_required
def user(see_user_id):
    
    if (not current_user.is_admin):
        return redirect(url_for('views.home'))
    else:
        see_user = User.query.get(see_user_id)

        # for testing generating excel: users_shifts_pd_dataframe([see_user], datetime.strptime("2024-02-16 0:00:00", "%Y-%m-%d %H:%M:%S"), datetime.strptime("2024-02-19 0:00:00", "%Y-%m-%d %H:%M:%S"))

        return render_template("admin_see_user.html", user=current_user, see_user=see_user, all_shifts_display_data=user_all_shifts_formatted(user=see_user, use_case="admin html"))