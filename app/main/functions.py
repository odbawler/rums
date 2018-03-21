from datetime import datetime, date, time


def calculate_time_worked(end, break_total, start, time_fmt):
    # Subtract break time from finish time
    endlessbreak = datetime.strptime(str(end), time_fmt) - datetime.strptime(str(break_total), time_fmt)
    # Convert time to timedelta type so we can subtract from finish time
    shiftstart = datetime.combine(date.min, start) - datetime.min
    # Subtract the start time from the recalculated finish time to get the overall time worked
    worked = endlessbreak - shiftstart
    return worked
