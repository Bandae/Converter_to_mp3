import re
import subprocess

def get_song_length(file_name: str) -> float:
    '''uses ffprobe to return the length (in seconds) of the file with the specified name, rounded to 3 decimal places'''
    duration = subprocess.check_output(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'default=noprint_wrappers=1:nokey=1', file_name])
    duration = re.search(r'(\d+.\d+)', str(duration))
    
    return round(float(duration[0]), 3)

def time_to_seconds(time: str) -> float:
    '''takes a str formated as mm:ss.sss and returns a float representing that time as seconds'''
    match = re.match(r'(\d{1,2}):(\d{1,2}.\d{1,3}|\d{1,2})', time)
    minutes, seconds = match[1], match[2]
    time = int(minutes) * 60 + float(seconds)
    return time

def time_to_str(time: float) -> str:
    '''takes a float representing time as amount of seconds and returns str formated as mm:ss.sss'''

    minutes = int(time / 60)
    seconds = round(time - minutes * 60, 3)
    
    time_as_str = str(minutes) + ':'

    if seconds < 10:
        time_as_str = time_as_str + '0'

    time_as_str = time_as_str + str(seconds)

    zeroes_to_add = 3 - len(str(seconds).split('.')[1]) if '.' in str(seconds) else 3

    if zeroes_to_add == 3:
        time_as_str += '.'

    time_as_str += '0' * zeroes_to_add

    return time_as_str

def shorten_name(name: str, max_len: int) -> str:
    '''Cuts strings short and adds "..." if the string exceeds some length.'''
    return name if len(name) <= max_len else name[0:max_len-3] + '...'
