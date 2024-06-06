from datetime import datetime, timedelta
import pandas as pd


def convert_time_float_to_string(flt_timestamp):
    ### skip the conversion if the input is None
    ### this is needed because if the word is a number (e.g., 15), whisperx will return None
    if flt_timestamp == None:
        t_formatted = None
    else:
        t = timedelta(seconds = flt_timestamp)  #step 1
        t = (datetime.min + t).time()           #step 2

        format = "%H:%M:%S.%f"
        t_formatted = t.strftime(format)[:-3]   #step 3 *[:-3] means until the third decimals

    return t_formatted


### Function to convert string time to float
def convert_string_to_float(str_timestamp):
    if str_timestamp == None:
        t_formatted = None
    else:
        t = datetime.strptime(str_timestamp, "%H:%M:%S.%f")
        t_formatted = timedelta(hours=t.hour, minutes=t.minute, seconds=t.second, microseconds=t.microsecond).total_seconds()

    return t_formatted