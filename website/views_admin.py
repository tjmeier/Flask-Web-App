from flask import Blueprint, render_template, request, flash, redirect, url_for, send_file, app
from flask_login import login_required, current_user
from datetime import datetime,  date, timedelta
from pytz import timezone


from .constants import MY_TIMEZONE
from .models import User, Client, Role, RoleHolders
from .dataprocessing import user_all_shifts_formatted, users_shifts_pd_dataframe
from . import db #imports database 'db' from the current directory defined in __init__.py

import os

DOWNLOAD_URL = "/admin/download/"
EXCEL_DOWNLOAD_PATH = "../Excel/" # ** in Python Anywhere, we need to go up two directories


def get_starting_ending_date_selection():
    now = datetime.strptime(((datetime.now()).astimezone(timezone(MY_TIMEZONE))).strftime("%Y-%m-%d"), "%Y-%m-%d")

    #gets time range for past pay period
    starting_date = now + timedelta(days= -(now.weekday()), weeks= -1) #2 mondays ago
    ending_date = now + timedelta(days= -(now.weekday()), weeks= 0) #1 monday ago
    
    #update time range from user submission
    if request.method == 'POST':

        #takes whatever is currently in the form
        if request.form['btn'] == 'update-time-range':
            starting_date = datetime.strptime(request.form.get('starting-date'),"%Y-%m-%d")
            ending_date = datetime.strptime(request.form.get('ending-date'),"%Y-%m-%d")

        #takes whatever is currently in the form, and adds or subtracts 7 days to shift weeks
        elif request.form['btn'] == 'past-week-time-range':
            starting_date = datetime.strptime(request.form.get('starting-date'),"%Y-%m-%d") - timedelta(days=7) 
            ending_date = datetime.strptime(request.form.get('ending-date'),"%Y-%m-%d") - timedelta(days=7) 
        elif request.form['btn'] == 'next-week-time-range':
            starting_date = datetime.strptime(request.form.get('starting-date'),"%Y-%m-%d") + timedelta(days=7) 
            ending_date = datetime.strptime(request.form.get('ending-date'),"%Y-%m-%d") + timedelta(days=7) 

        elif request.form['btn'] == 'past-pay-period-time-range':
            starting_date = now + timedelta(days= -(now.weekday()), weeks= -1) #2 mondays ago
            ending_date = now + timedelta(days= -(now.weekday()), weeks= 0) #1 monday ago
    


    #makes the time attributes of the starting and ending date be midnight
    starting_date.replace(hour=0, minute=0, second=0)
    ending_date.replace(hour=0, minute=0, second=0)


    return starting_date, ending_date




views_admin = Blueprint('views_admin', __name__, template_folder='templates/admin')

@views_admin.route('/', methods=['GET', 'POST'])
@login_required
def home():
    if (not current_user.is_admin):
        return redirect(url_for('views.home'))
    else:


        all_users = User.query.order_by(User.lastName)

        starting_date, ending_date = get_starting_ending_date_selection()


        
        Excel_File_Name = users_shifts_pd_dataframe(all_users, "All Users", starting_date, ending_date)


        return render_template("admin.html", user=current_user, previous_starting_date = starting_date.strftime("%Y-%m-%d"), previous_ending_date = ending_date.strftime("%Y-%m-%d"), \
                                Excel_File_Name=f"{DOWNLOAD_URL}{Excel_File_Name}", download_button_text = "All Users",)


######################### Clients ##############################
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
            
            return redirect(url_for('views_admin.clients'))



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



################################ Roles #############################################
@views_admin.route('/roles', methods=['GET', 'POST'])
@login_required
def roles():
    if (not current_user.is_admin):
        return redirect(url_for('views.home'))
    else:

        if request.method == 'POST':
            roleName = request.form.get('role-name')
            description = request.form.get('description')
            payrate = float(request.form.get('payrate'))


            
            role = Role.query.filter_by(role_name=roleName).first() #sees if there's role a client with that name

  
            if len(roleName) < 2:
                flash('Role name must be at least 2 characters.', category='error')
                
            elif payrate < 0:
                flash('Payrate must be positive value.', category='error')
                
            elif role:
                flash('A role with that name already exists.', category='error')
                
            else:
                

                new_role = Role(role_name = roleName, description=description, payrate = payrate)

                db.session.add(new_role)
                db.session.commit()

                flash('Role successfully added!', category='success')

        all_roles = Role.query.order_by(Role.role_name)

        return render_template("admin_roles.html", user=current_user, all_roles = all_roles)



@views_admin.route('/role/<int:see_role_id>', methods=['GET', 'POST'])
@login_required
def role(see_role_id):
    
    if (not current_user.is_admin):
        return redirect(url_for('views.home'))
    else:
        see_role = Role.query.filter_by(id=see_role_id).first()


        if request.method == 'POST':
            if request.form['btn'] == 'update-role':
                roleName = request.form.get('role-name')
                description = request.form.get('description')
                payrate = float(request.form.get('payrate'))


                
                role = Role.query.filter_by(role_name=roleName).first() #sees if there's role a client with that name


    
                if len(roleName) < 2:
                    flash('Role name must be at least 2 characters.', category='error')
                    
                elif payrate < 0:
                    flash('Payrate must be positive value.', category='error')
                    
                elif role and role.role_name != see_role.role_name:
                    flash('A role with that name already exists.', category='error')
                    
                else:
                    
                    see_role.role_name = roleName; see_role.description = description; see_role.payrate = payrate
                    db.session.commit()

                    flash('Role successfully updated!', category='success')


        #gets all the users who have this role
        if see_role.role_holders is not None: role_users = [User.query.get(role_holder.holder_user_id) for role_holder in see_role.role_holders]
        else: role_users = []

        return render_template("admin_see_role.html", see_role=see_role, user=current_user, all_users=role_users, user_table_name = f"{see_role.role_name} Users")


######################################## Users ################################################
@views_admin.route('/users')
@login_required
def users():
    if (not current_user.is_admin):
        return redirect(url_for('views.home'))
    else:    
        all_users = User.query.order_by(User.lastName)

        return render_template("admin_users.html", user=current_user, all_users=all_users, user_table_name = "Table of All Users")


def get_user_role_ids(user):
    if user.roles_held is not None: return [role_holder.held_role_id for role_holder in user.roles_held]
    else: return []


@views_admin.route('/user/<int:see_user_id>', methods=['GET', 'POST'])
@login_required
def user(see_user_id):
    
    if (not current_user.is_admin):
        return redirect(url_for('views.home'))
    else:
        
        see_user = User.query.get(see_user_id)


        all_roles = Role.query.order_by(Role.role_name)

        user_current_roles = get_user_role_ids(see_user)

        if request.method == 'POST':

            if request.form['btn'] == 'update-roles-assigned':


                checked_roles = [role.id for role in all_roles if request.form.get(f'roles-assigned{role.id}') == "Checked"] #sets the users roles to what checkboxes get checked

                #updating the held roles by this user based on the check boxes form
                added_roles = [role for role in checked_roles if role not in user_current_roles]
                
                for role in added_roles:
                    new_role_holder = RoleHolders(holder_user_id = see_user.id, held_role_id = role)
                    db.session.add(new_role_holder)

                
                revoked_roles = [role for role in user_current_roles if role not in checked_roles]
                
                for role in revoked_roles:
                    deleted_role_holder = RoleHolders.query.filter_by(holder_user_id = see_user.id, held_role_id = role).first()
                    db.session.delete(deleted_role_holder)

                db.session.commit()

                return redirect(url_for('views_admin.user', see_user_id=see_user_id))


        starting_date, ending_date = get_starting_ending_date_selection()

        

        


        # for testing generating excel: 
        Excel_File_Name = users_shifts_pd_dataframe([see_user], f"{see_user.firstName} {see_user.lastName}", \
                                                    starting_date, ending_date)


        return render_template("admin_see_user.html", previous_starting_date = starting_date.strftime("%Y-%m-%d"), previous_ending_date = ending_date.strftime("%Y-%m-%d"), \
                                user=current_user, see_user=see_user, Excel_File_Name=f"{DOWNLOAD_URL}{Excel_File_Name}", download_button_text = f"{see_user.firstName} {see_user.lastName}", \
                                all_shifts_display_data=user_all_shifts_formatted(user=see_user, use_case="admin html"), all_roles = all_roles, user_current_roles = user_current_roles)
    
@views_admin.route('/download/<path:excel_filename>', methods=['GET', 'POST'])
@login_required
def downloadFile(excel_filename):
    if (not current_user.is_admin):
        return redirect(url_for('views.home'))
    else:
        
        path = f"{EXCEL_DOWNLOAD_PATH}{excel_filename}"
        return send_file(path, as_attachment=True)
