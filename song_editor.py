import os
from typing import Dict, Tuple

import ffmpeg
from mutagen.mp3 import MP3
from mutagen.easyid3 import EasyID3

BITRATE = 180000

class SongEditor:
    def __init__(self, file_name: str) -> None:
        self.stream = ffmpeg.input(file_name)
        self.file_name = file_name

    def filter_stream(self, **filters) -> None:
        if 'atrim' in filters and any(filters['atrim']):
            start, end = filters['atrim']

            if start and end:
                self.stream = ffmpeg.filter(self.stream, 'atrim', start=start, end=end)
            elif start:
                self.stream = ffmpeg.filter(self.stream, 'atrim', start=start)
            elif end:
                self.stream = ffmpeg.filter(self.stream, 'atrim', end=end)
    
    def output_stream(self, new_file_name: str, bitrate: int) -> None:
        if not os.path.exists('.\music'):
            os.makedirs('.\music')
        
        new_file_name = os.path.splitext(new_file_name)[0]
        self.stream = ffmpeg.output(self.stream, f'.\music\{new_file_name}.mp3', **{'b:a': bitrate})
        ffmpeg.run(self.stream)
        self.file_name = f'.\music\{new_file_name}.mp3'
    
    def write_ID3_tags(self, ID3tags: Dict[str, str]) -> None:
        # decide whether to ask, overwrite or not if tags already in the file etc.
        song = MP3(self.file_name, ID3=EasyID3)

        for tag in ID3tags:
            if not tag in song:
                song[tag] = [ID3tags[tag]]
    
        song.save()


def convert_file_to_mp3_and_trim(file_name: str, time: Tuple[float, float], tags: Dict[str, str]) -> None:
    '''
    takes the name of a file to be converted, with extension "example.mp3",
    times for triming the file,
    and a dictionary of ID3 tags.

    Cuts file, converts to mp3, writes tags
    '''
    file_name_no_extension = os.path.splitext(file_name)[0]

    editor = SongEditor(file_name)
    editor.filter_stream(atrim=time)

    if tags.get('title'):
        editor.output_stream(tags['title'], BITRATE)
    else:
        editor.output_stream(file_name_no_extension, BITRATE)
    
    editor.write_ID3_tags(tags)
