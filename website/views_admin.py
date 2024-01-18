from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user
from .models import User

from . import db #imports database 'db' from the current directory defined in __init__.py
import json


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



        return render_template("admin.html", user=current_user, all_users=User)
