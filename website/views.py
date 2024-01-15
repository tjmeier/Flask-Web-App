from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user
from .models import Note
from . import db #imports database 'db' from the current directory defined in __init__.py
import json


views = Blueprint('views', __name__)

@views.route('/', methods=['GET', 'POST'])
@login_required
def home():
    data = request.form
    
    if request.method == 'POST':
        note = request.form.get('note')

        if len(note) < 1:
            flash('Note must contain at least one character.', category="error")
        else:
            new_note = Note(data=note, user_id=current_user.id)
            db.session.add(new_note)
            db.session.commit()
            flash('Note added!', category='success')

    return render_template("home.html", user=current_user)

@views.route('/delete-note', methods=['POST'])
def delete_note():
    note = json.loads(request.data)
    noteId = note['noteId']
    note = Note.query.get(noteId)
    if note:
        if note.user_id == current_user.id: #security check
            db.session.delete(note) #deletes the note from the database
            db.session.commit()
    return ""; #we need to return something



@views.route('/admin', methods=['GET', 'POST'])
@login_required
def admin():
    if (current_user.is_admin):
        data = request.form
        
        if request.method == 'POST':
            pass

        return render_template("admin.html", user=current_user)

    else:
        return redirect(url_for('views.home'))
