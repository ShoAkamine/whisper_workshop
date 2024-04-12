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
def convert_string_to_float(str_series):
    dt_series = pd.to_timedelta(str_series).dt.total_seconds()
    return dt_series

# str_series = pd.Series(["01:23:45.678", "02:34:56.789"])
# output:
# 0    5025.678
# 1    9276.789