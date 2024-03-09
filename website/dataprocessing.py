from .models import Note, Client, Shift
from . import db #imports database 'db' from the current directory defined in __init__.py
from datetime import datetime, date

import pandas as pd
import numpy as np

import os

DATE_MDY_FORMAT = "%m/%d/%Y"
DATE_MDY_DASHES_FORMAT = "%m-%d-%Y"
TIME_12H_FORMAT = "%I:%M %p"

#date_range_as tuple (start date, end date);

def user_all_shifts_formatted(user, use_case = "user html", datetime_range = "all dates"):
    #query list of all inactive shifts for given user
    if datetime_range == "all dates":
        all_shifts = [Shift.query.get(shift.id) for shift in user.shiftsWorked]
    else:
        all_shifts = []
        for shift in user.shiftsWorked:
            if shift.datetime_clockout is not None: #incompleted shifts will never be included if a date range exists

                if shift.datetime_clockout > datetime_range[0] and  shift.datetime_clockout < datetime_range[1]:
                    all_shifts.append(Shift.query.get(shift.id))


    #sort by clock out time (most recent to least resent will display on page)
    #active shift is at the top, then the approved shifts, then the not approved shifts
    all_shifts.sort(reverse=True, key=lambda shift: ( shift.is_active, not shift.is_approved, str(shift.datetime_clockout) if shift.datetime_clockout is not None else " ") ) 

    #query list of all corresponding client first and last names
    all_shift_clients = [Client.query.get(shift.client_id).firstName+" "+\
                         Client.query.get(shift.client_id).lastName for shift in all_shifts]
    
    #query and format timein, timeout, total hours, and date
    all_shifts_timein = [shift.datetime_clockin.strftime(TIME_12H_FORMAT) for shift in all_shifts]
    all_shifts_timeout = [shift.datetime_clockout.strftime(TIME_12H_FORMAT) if not shift.is_active else "Still Active" for shift in all_shifts ] #active shift doesn't have a time out

    all_shifts_id = [int(shift.id) for shift in all_shifts]
    
    all_shifts_total_hours = [float(round(shift.total_hours, 2)) for shift in all_shifts]
    all_shifts_date = []
    for shift in all_shifts:
        if (shift.is_active):
            all_shifts_date.append(shift.datetime_clockin.strftime(DATE_MDY_FORMAT))
        elif (shift.datetime_clockin.strftime(DATE_MDY_FORMAT) == shift.datetime_clockout.strftime(DATE_MDY_FORMAT)):
            all_shifts_date.append(shift.datetime_clockin.strftime(DATE_MDY_FORMAT))
        else:
            all_shifts_date.append(shift.datetime_clockin.strftime(DATE_MDY_FORMAT)+" to "+shift.datetime_clockout.strftime(DATE_MDY_FORMAT))

    #zip all these lists together and send it to the html page
    

    #
    if use_case == "admin html" or use_case == "user html":
        return zip(all_shifts, all_shift_clients, all_shifts_timein, all_shifts_timeout,  all_shifts_total_hours, all_shifts_date)

    elif use_case == "admin pandas":

        all_shifts_datein = [shift.datetime_clockin.strftime(DATE_MDY_FORMAT) for shift in all_shifts]
        all_shifts_dateout = [shift.datetime_clockout.strftime(DATE_MDY_FORMAT) if not shift.is_active else "Not Completed" for shift in all_shifts ] #active shift doesn't have a time out

        return np.array([all_shifts_id, all_shift_clients, all_shifts_total_hours, all_shifts_timein, all_shifts_datein, all_shifts_timeout, all_shifts_dateout]).T
    






#returns path to excel file to be downloaded
def users_shifts_pd_dataframe(users, download_name, starting_datetime, ending_datetime):

    EXCEL_DIRECTORY_NAME = "Excel"
    EXCEL_FILE_NAME = f'{download_name} Shifts {starting_datetime.strftime(DATE_MDY_DASHES_FORMAT)} to {ending_datetime.strftime(DATE_MDY_DASHES_FORMAT)}.xlsx'

    #creates excel folder
    if (not os.path.exists(EXCEL_DIRECTORY_NAME)):
        os.makedirs(EXCEL_DIRECTORY_NAME)

    
    #create a 3D list of all shift data for each user in the list
    #first dimension = user, second dimension = shift attribute, third dimension = shift number

    users_shifts_data = [user_all_shifts_formatted(user=user, use_case="admin pandas", datetime_range=(starting_datetime, ending_datetime)) for user in users]

    SHIFTS_DATA_COL_NAMES = ("Shift ID", "Client", "Shift Hours", "Time In", "Date In", "Time Out", "Date Out")


    dfs = []

    for i, user in enumerate(users):
        
        user_info_df = pd.DataFrame( [f"{user.firstName} {user.lastName}", f"{user.email}"], columns=["User"])

        dfs.append(user_info_df)

        
        df = pd.DataFrame(users_shifts_data[i], columns=SHIFTS_DATA_COL_NAMES)
        df["Shift ID"] = df["Shift ID"].astype('int')
        df["Shift Hours"] = df["Shift Hours"].astype('float')

        df.loc[len(df.index)] = (df[["Shift Hours"]]).sum().rename("Total Hours") #add a total hours row to the end of the dataframe

        dfs.append(df)



    main_df = pd.concat([df for df in dfs]) #concatenate all these datafro

    main_df.to_excel(EXCEL_DIRECTORY_NAME+"/"+EXCEL_FILE_NAME, index=False, float_format="%.2f")
    
    return EXCEL_FILE_NAME
