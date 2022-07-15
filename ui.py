import tkinter as tk
from typing import Dict
import os

from song_editor import convert_file_to_mp3_and_trim
from song_tags_finder import SongTagsFinder
from ui_components import SongFrame
import utils

# TODO: handle the console returning "overwrite files? y/n" in the ui
# TODO: add asynchronity for the ui, and a progress bar

class Ui:
    def __init__(self) -> None:
        self.window = tk.Tk()
        self.songframes: Dict['str': SongFrame] = {}
    
    def no_files_screen(self) -> None:
        label = tk.Label(self.window, text="No files found in the root directory")
        label.pack(padx=40, pady=40)

    def make_container_for_song(self, file_name: str, song_length: str, tags: Dict[str, str]) -> None:
        if file_name in self.songframes:
            return None
        
        frame = SongFrame(self.window, file_name, song_length, tags)
        frame.pack()
        self.songframes.update({file_name: frame})
    
    def add_accept_button(self) -> None:
        accept_button = tk.Button(self.window, text='Run', command=self.click_accept_button)
        accept_button.pack()

    def click_accept_button(self) -> None:
        for frame in self.songframes.values():
            convert_file_to_mp3_and_trim(frame.label['text'], frame.get_time_values(), frame.tags_frame.get_fields_data())
    
    def add_songs_from_directory(self) -> None:
        accepted_formats = ['.mp3', '.webm']
        files_for_conversion = [f for f in os.listdir() if os.path.splitext(f)[1] in accepted_formats]

        if not files_for_conversion:
            self.no_files_screen()
            return

        for f in files_for_conversion:
            song_tags = SongTagsFinder(f).get_data()
            
            self.make_container_for_song(f, utils.time_to_str(utils.get_song_length(f)), song_tags)
        
        self.add_accept_button()

if __name__ == '__main__':
    window = Ui()
    window.add_songs_from_directory()
    window.window.mainloop()
