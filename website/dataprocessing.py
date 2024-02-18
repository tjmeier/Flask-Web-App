from .models import Note, Client, Shift
from . import db #imports database 'db' from the current directory defined in __init__.py
import json
from datetime import datetime, date
from pytz import timezone

import pandas as pd #for later :)

def user_shifts_formatted(user):
    #query list of all inactive shifts for given user
    all_shifts = [Shift.query.get(shift.id) for shift in user.shiftsWorked]

    #sort by clock out time (most recent to least resent will display on page)
    #active shift is at the top, then the approved shifts, then the not approved shifts
    all_shifts.sort(reverse=True, key=lambda shift: ( shift.is_active, not shift.is_approved, str(shift.datetime_clockout) if shift.datetime_clockout is not None else " ") ) 

    #query list of all corresponding client first and last names
    all_shift_clients = [Client.query.get(shift.client_id).firstName+" "+\
                         Client.query.get(shift.client_id).lastName for shift in all_shifts]
    
    #query and format timein, timeout, total hours, and date
    all_shifts_timein = [shift.datetime_clockin.strftime("%I:%M %p") for shift in all_shifts]
    all_shifts_timeout = [shift.datetime_clockout.strftime("%I:%M %p") if not shift.is_active else "Still Active" for shift in all_shifts ] #active shift doesn't have a time out
    
    all_shifts_total_hours = [round(shift.total_hours, 2) for shift in all_shifts]
    all_shifts_date = []
    for shift in all_shifts:
        if (shift.is_active):
            all_shifts_date.append(shift.datetime_clockin.strftime("%m/%d/%Y"))
        elif (shift.datetime_clockin.strftime("%m/%d/%Y") == shift.datetime_clockout.strftime("%m/%d/%Y")):
            all_shifts_date.append(shift.datetime_clockin.strftime("%m/%d/%Y"))
        else:
            all_shifts_date.append(shift.datetime_clockin.strftime("%m/%d/%Y")+" to "+shift.datetime_clockout.strftime("%m/%d/%Y"))

    #zip all these lists together and send it to the html page
    return zip(all_shifts, all_shift_clients, all_shifts_timein, all_shifts_timeout,  all_shifts_total_hours, all_shifts_date)