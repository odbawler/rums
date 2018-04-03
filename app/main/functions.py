from datetime import datetime, date, time


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
