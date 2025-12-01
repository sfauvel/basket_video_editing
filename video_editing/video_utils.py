# Some utility functions to manipulate data.

import glob
import re

def time_to_seconds(time):
    split = time.split(":")
    if len(split) < 2  or 3 < len(split):
        raise Exception(f"Invalid time: '{time}'")
    for number in split:
        if not re.match(r'^(\d)+$', number):
            raise Exception(f"Invalid time: '{time}'")
    
    seconds = 0
    
    if len(split) >= 1:
        seconds += int(split[-1])
    
    if len(split) >= 2:
        seconds += 60*int(split[-2])
    
    if len(split) >= 3:
        seconds += 60*60*int(split[-3])
        
    return int(seconds)
    
def seconds_to_time(time_in_seconds):
    hour = int(time_in_seconds / 3600)
    time_in_seconds -= hour * 3600
    minutes = int(time_in_seconds / 60)
    time_in_seconds -= minutes * 60
    seconds = time_in_seconds
    return f"{hour:01d}:{minutes:02d}:{seconds:02d}"

def files_sorted(pattern):
    files = glob.glob(pattern)
    files.sort()
    return files 

def files_before(pattern, first_file_exclude):
    files = glob.glob(pattern)
    files.sort()
    return [file for file in files if file < first_file_exclude] 
