import os
import subprocess

from mutagen.mp3 import MP3
from mutagen.easyid3 import EasyID3
    
def write_ID3_tags(file_name, ID3tags: dict[str, str]) -> None:
    # decide whether to ask, overwrite or not if tags already in the file etc.
    song = MP3(file_name, ID3=EasyID3)

    for tag in ID3tags:
        if not tag in song:
            song[tag] = [ID3tags[tag]]

    song.save()


def convert_file(file_name: str, time: tuple[float, float], tags: dict[str, str]) -> None:
    '''
    takes the name of a file to be converted, with extension: "example.mp3",
    times for triming the file,
    and a dictionary of ID3 tags.

    Cuts file, converts to mp3, writes tags
    '''
    # if not os.path.exists('.\music'):
    #     os.makedirs('.\music')

    new_file_name = tags['title'] if tags.get('title') else os.path.splitext(file_name)[0]
    # -y automatycznie potwierdza nadpisanie pliku jak juz istnieje. -n daje nie. moge sprawdzic os.path costam czy jest juz taki plik najpierw, i wtedy sie zapytac w ui, i wybrac 
    options = ['ffmpeg', '-y', '-ss', time[0], '-i', file_name, '-to', time[1], '-vn', '-c:a', 'libmp3lame', '-copyts', f'{new_file_name}.mp3']
    uciete = subprocess.check_output(options)
    write_ID3_tags(f'{new_file_name}.mp3', tags)
