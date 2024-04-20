from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user
from .models import Note, Client, Shift, Role, RoleHolders
from .dataprocessing import user_all_shifts_formatted
from . import db #imports database 'db' from the current directory defined in __init__.py
import json
from datetime import datetime, date
from pytz import timezone

views = Blueprint('views', __name__, template_folder='templates')

MY_TIMEZONE = 'US/Eastern' #currently this app only can run in one timezone


def get_user_roles(user):
    if user.roles_held is not None: return [Role.query.get(role_holder.held_role_id) for role_holder in user.roles_held]
    else: return []



@views.route('/', methods=['GET', 'POST'])
@login_required
def home():
    data = request.form
    
    all_clients = Client.query.order_by(Client.lastName)
    user_roles = get_user_roles(current_user)

    #generating page variables
    now = datetime.strptime(((datetime.now()).astimezone(timezone(MY_TIMEZONE))).strftime("%Y-%m-%d %H:%M:%S"), "%Y-%m-%d %H:%M:%S")
    current_weekday = now.strftime("%A")
    current_date = now.strftime("%m/%d/%Y")
    current_time12h = now.strftime("%I:%M %p")
    current_time24h = now.strftime("%H:%M")
    current_dateymd = now.strftime("%Y-%m-%d")


    current_shift = Shift.query.get(current_user.activeShift_id)
    if current_shift is not None:
        shift_timein24h = (current_shift.datetime_clockin).strftime("%H:%M")
        
        shift_timedelta = now - (current_shift.datetime_clockin)
        shift_totaltime = str(shift_timedelta) #truncate the fractions of seconds from shift_timedelta
        shift_client = Client.query.get(current_shift.client_id)

        shift_dateymd = (current_shift.datetime_clockin).strftime("%Y-%m-%d")
        shift_note = current_shift.note
        shift_role = Role.query.get(current_shift.role_id)
    
    else:
        shift_timein24h = ""
        shift_totaltime = ""
        shift_client = ""
        shift_dateymd = ""
        shift_note = ""
        shift_role = ""

    
    
    if request.method == 'POST':

        if request.form['btn'] == 'clockin':
            
            shift_client_id = request.form.get('client-id')
            shift_role_id = request.form.get('role-id')

            if shift_client_id is None:
                flash('Could not clock in! There was no client selected.', category='error')
            elif shift_role_id is None:
                flash('Could not clock in! There was no role selected.', category='error')
            else:
                shift_role = Role.query.get(shift_role_id)
                #create a new shift
                new_shift = Shift(user_id = current_user.id, client_id = shift_client_id, \
                                payrate_for_shift = shift_role.payrate, role_name_for_shift = shift_role.role_name, role_id = shift_role.id, \
                                datetime_clockin=datetime.strptime(((datetime.now()).astimezone(timezone(MY_TIMEZONE))).strftime("%Y-%m-%d %H:%M:%S"), "%Y-%m-%d %H:%M:%S"))
                db.session.add(new_shift)
                db.session.commit()

                flash('You successfully clocked in!', category='success')

                #update user's active shift
                current_user.activeShift_id = new_shift.id
                db.session.commit()
                        


            #reload home page
            return redirect(url_for('views.home'))

        elif request.form['btn'] == 'clockout':
            time_in = request.form.get('time-in')
            time_out = request.form.get('time-out')
            date_in = request.form.get('date-in')
            date_out = request.form.get('date-out')
            shift_client_id = request.form.get('client-id')
            shift_role = Role.query.get(request.form.get('role-id'))
            


            shift_note = request.form.get('shift-note')

            
            #filling in final shift data

            final_datetime_in = datetime.strptime(time_in + " " + date_in, "%H:%M %Y-%m-%d")
            final_datetime_out = datetime.strptime(time_out + " " + date_out, "%H:%M %Y-%m-%d")
            shift_totalhours = round((final_datetime_out - final_datetime_in).total_seconds()/3600, 10)

            #some data still gets saved regardless of if the clockout was valid
            current_shift.datetime_clockin = final_datetime_in
            current_shift.client_id = shift_client_id
            current_shift.note = shift_note
            current_shift.role_name_for_shift = shift_role.role_name
            current_shift.payrate_for_shift = shift_role.payrate
            current_shift.role_id = shift_role.id



            if ((final_datetime_out - final_datetime_in).total_seconds() < 0):
                flash('Your shift cannot be negative duration! Check your time in and time out.', category='error')
                db.session.commit()
                return redirect(url_for('views.home'))
            
            elif (shift_note == ""):
                flash('Please enter a shift note before clocking out!', category='error')
                
            else:
                current_user.activeShift_id = 0
                
                current_shift.datetime_clockout = final_datetime_out
                current_shift.total_hours = shift_totalhours
                current_shift.is_active = False

                flash('You successfully clocked out! Your shift lasted '+str(round(shift_totalhours, 2))+' hours!', category='success')
            
                db.session.commit()


        elif request.form['btn'] == "current-shift-update":
            

            #the only info you can update is the shift_note, time in (not time out), and the client
            time_in = request.form.get('time-in')
            date_in = request.form.get('date-in')
            shift_client_id = request.form.get('client-id')
            shift_note = request.form.get('shift-note')
            shift_role = Role.query.get(request.form.get('role-id'))

            
            final_datetime_in = datetime.strptime(time_in + " " + date_in, "%H:%M %Y-%m-%d")

           
            current_shift.client_id = shift_client_id
            current_shift.datetime_clockin = final_datetime_in
            current_shift.note = shift_note
            current_shift.role_name_for_shift = shift_role.role_name
            current_shift.payrate_for_shift = shift_role.payrate
            current_shift.role_id = shift_role.id

            db.session.commit()

            flash('Current shift details successfully updated!', category='success')

            #recalculate shift times to be displayed on the page (could be consolidated)
            shift_timein24h = (current_shift.datetime_clockin).strftime("%H:%M")
            shift_timedelta = now - (current_shift.datetime_clockin)
            shift_totaltime = (str(shift_timedelta)) #truncate the fractions of seconds from shift_timedelta
            shift_client = Client.query.get(current_shift.client_id)

            shift_dateymd = (current_shift.datetime_clockin).strftime("%Y-%m-%d")
            shift_note = current_shift.note
            




        elif request.form['btn'] == 'notes':
            note = request.form.get('note')

            if len(note) < 1:
                flash('Note must contain at least one character.', category="error")
            else:
                new_note = Note(data=note, user_id=current_user.id)
                db.session.add(new_note)
                db.session.commit()
                flash('Note added!', category='success')




   


    return render_template("home.html", 
        user=current_user, 
        all_clients=all_clients, 
        current_weekday=current_weekday, 
        current_date=current_date,
        current_dateymd=current_dateymd,
        shift_dateymd=shift_dateymd,
        current_time12h=current_time12h,
        current_time24h=current_time24h,
        shift_timein24h=shift_timein24h,
        shift_totaltime = shift_totaltime,
        shift_client = shift_client,
        shift_note = shift_note,
        user_roles = user_roles,
        shift_role = shift_role)




@views.route('/shifts')
@login_required
def shifts():

    return render_template("shifts.html", user=current_user, all_shifts_display_data=user_all_shifts_formatted(user=current_user, use_case="user html"))


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



