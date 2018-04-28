from datetime import datetime, date, time, timedelta
import math

def calculate_time_worked(end, break_total, start, time_fmt):
    # Subtract break time from finish time
    end_less_break = datetime.strptime(str(end), time_fmt) - break_total

    # Convert time to timedelta type so we can subtract from finish time
    shiftstart = datetime.combine(date.min, start) - datetime.min

    # Subtract the start time from the recalculated finish time to get the overall time worked
    worked = end_less_break - shiftstart
    return worked

def calculate_break_time(start_break, end_break, time_fmt):
    break_total = datetime.strptime(str(end_break), time_fmt) - datetime.strptime(str(start_break), time_fmt)
    return break_total

def format_timedelta(td):
    seconds = td.total_seconds()
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    str = '{}:{}'.format(int(hours), int(minutes))
    return str

def subtract_daily_hrs(current, daily):
    hours, minutes = current.split(':')
    c_hours = int(hours) * 3600
    c_minutes = int(minutes) * 60
    # if hours is negative we need minutes to be negative too
    if '-' in str(hours):
        c_minutes *= -1

    current_seconds = c_hours + c_minutes
    hrs, mins = daily.split(':')
    d_hours = int(hrs) * 3600
    d_minutes = int(mins) * 60
    daily_seconds = d_hours + d_minutes
    negative = False

    seconds = float(current_seconds) - float(daily_seconds)
    # get time from total seconds
    the_time = timedelta(seconds=seconds)
    time = format_timedelta(the_time)
    if seconds < 0:
        negative = True
        # if time is minus we need to do some magic
        # turn the negative 'missing' time into postive
        minus_24 = timedelta(seconds=86400)
        neg_to_pos = the_time + minus_24

        # subract the 'missing' time from 24 hrs to get postive 'actual' time
        postime = minus_24 - neg_to_pos
        time = format_timedelta(postime)

    if negative:
        return "-" + time
    else:
        return time

def add_worked_hrs(current, worked):
    hours, minutes = current.split(':')
    c_hours = int(hours) * 3600
    c_minutes = int(minutes) * 60
    # if hours is negative we need minutes to be negative too
    if '-' in str(hours):
        c_minutes *= -1

    current_seconds = c_hours + c_minutes
    hours, minutes = worked.split(':')
    w_hours = int(hours) * 3600
    w_minutes = int(minutes) * 60
    worked_seconds = int(w_hours) + int(w_minutes)
    negative = False

    seconds = float(current_seconds) + float(worked_seconds)

    # get time from total seconds
    the_time = timedelta(seconds=seconds)
    time = format_timedelta(the_time)
    if seconds < 0:
        negative = True
        # if time is minus we need to do some magic
        # turn the negative 'missing' time into postive
        minus_24 = timedelta(seconds=86400)
        neg_to_pos = the_time + minus_24

        # subract the 'missing' time from 24 hrs to get postive 'actual' time
        postime = minus_24 - neg_to_pos
        time = format_timedelta(postime)

    if negative:
        return "-" + time
    else:
        return time


def delta_to_time(delta):
    return datetime.strptime(str(delta), '%H:%M:%S').time()
