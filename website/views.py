from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user
from .models import Note, Client, Shift
from . import db #imports database 'db' from the current directory defined in __init__.py
import json


views = Blueprint('views', __name__)

@views.route('/', methods=['GET', 'POST'])
@login_required
def home():
    data = request.form
    
    if request.method == 'POST':

        if request.form['btn'] == 'clockin':
            
            shift_client_id = request.form.get('client-id')

            #create a new shift
            new_shift = Shift(user_id = current_user.id, client_id = shift_client_id)
            db.session.add(new_shift)
            db.session.commit()

            flash('You successfully clocked in!', category='success')

            #update user's active shift
            current_user.activeShift_id = new_shift.id
            db.session.commit()

            #reload home page
            return redirect(url_for('views.home'))

        elif request.form['btn'] == 'clockout':
            pass
        elif request.form['btn'] == 'current-shift-update':
            pass
        elif request.form['btn'] == 'notes':
            note = request.form.get('note')

            if len(note) < 1:
                flash('Note must contain at least one character.', category="error")
            else:
                new_note = Note(data=note, user_id=current_user.id)
                db.session.add(new_note)
                db.session.commit()
                flash('Note added!', category='success')




    all_clients = Client.query.order_by(Client.lastName)


    return render_template("home.html", user=current_user, all_clients=all_clients)

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



