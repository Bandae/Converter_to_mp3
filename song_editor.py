import os
import subprocess

from mutagen.mp3 import MP3
from mutagen.easyid3 import EasyID3

def write_ID3_tags(file_name, ID3tags: dict[str, str]) -> None:
    '''Writes ID3 tags into an mp3 file, if they are not already there.'''
    mp3_file = MP3(file_name, ID3=EasyID3)

    for tag in ID3tags:
        if not tag in mp3_file:
            mp3_file[tag] = [ID3tags[tag]]

    mp3_file.save()


def process_file(file_name: str, time: tuple[float, float], tags: dict[str, str], mp3s: bool=False) -> None:
    '''
    takes the name of a file to be converted, with extension: "example.mp3",
    times for triming the file,
    and a dictionary of ID3 tags.

    Cuts file, converts to mp3, writes tags
    If mp3s: No conversion
    '''
    if not os.path.exists('.\music'):
        os.makedirs('.\music')
    
    new_file_name = tags['title'] if tags.get('title') else os.path.splitext(file_name)[0]
    # -y automatically overwrites existing files. -n aborts.
    # can check os.path for if there is a file existing, and prompt user in ui before running ffmpeg

    # -ss -to selects start and end time, -copyts allows accurate time selection (then -to still refers to the time from the beginning of uncut file)
    # -vn = no video
    # -c:a copy = copy audio, -c:a libmp3lame = selects encoder
    # -q:a = selects audio quality - 2 = 170-210kbits/s, avarage 190 kbits/s, variable bit rate
    options = ['ffmpeg', '-y', '-ss', time[0], '-i', file_name, '-to', time[1], '-vn']
    if mp3s:
        new_file_name += 'NEW'
        options += ['-c:a', 'copy','-copyts', f'.\music\{new_file_name}.mp3']
    else:
        options += ['-c:a', 'libmp3lame', '-q:a', '2', '-copyts', f'.\music\{new_file_name}.mp3']
    
    subprocess.run(options)
    write_ID3_tags(f'.\music\{new_file_name}.mp3', tags)
