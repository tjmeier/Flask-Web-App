from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_user, login_required, logout_user, current_user
from .models import User
from . import db #imports database 'db' from the current directory defined in __init__.py




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
            pass



        return render_template("clients.html", user=current_user)
    
@views_admin.route('/users', methods=['GET', 'POST'])
@login_required
def users():
    if (not current_user.is_admin):
        return redirect(url_for('views.home'))
    else:
        data = request.form
        
        if request.method == 'POST':
            pass

        all_users = User.query.order_by(User.lastName)

        return render_template("admin_users.html", user=current_user, all_users=all_users)

@views_admin.route('/user/<int:see_user_id>', methods=['GET', 'POST'])
@login_required
def user(see_user_id):
    
    if (not current_user.is_admin):
        return redirect(url_for('views.home'))
    else:
        see_user = User.query.filter_by(id=see_user_id).first()

        if request.method == 'POST':
            pass

        return render_template("admin_see_user.html", user=current_user, see_user=see_user)