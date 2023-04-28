import tkinter as tk
from typing import Dict
import os
import subprocess

from song_editor import convert_file_to_mp3_and_trim
from song_tags_finder import SongTagsFinder
from ui_components import SongFrame, FileFrame
import utils

# TODO: handle the console returning "overwrite files? y/n" in the ui
# TODO: add asynchronity for the ui, and a progress bar

class Ui:
    def __init__(self) -> None:
        self.window = tk.Tk()
        self.songframes: Dict[str: SongFrame] = {}
        self.fileframes: Dict[str: FileFrame] = {}
    
    def no_files_screen(self) -> None:
        label = tk.Label(self.window, text="No files found in the root directory")
        label.pack(padx=40, pady=40)

    def check_FFMPEG(self) -> None:
        try:
            version = subprocess.check_output(['ffmpeg', '-version'])
            self.add_song_selection_screen()
        except FileNotFoundError:
            label = tk.Label(self.window, text="FFMPEG is not installed, or not on PATH")
            label.pack(padx=40, pady=40)

    def make_container_for_song(self, file_name: str, song_length: str, tags: Dict[str, str]) -> None:
        if file_name in self.songframes:
            return None
        
        frame = SongFrame(self.window, file_name, song_length, tags)
        frame.pack()
        self.songframes.update({file_name: frame})

    def click_accept_button1(self) -> None:
        accepted_songs = [file_name for file_name, frame in self.fileframes.items() if frame.checked.get()]
        if not accepted_songs:
            return
        for frame in self.fileframes.values():
            frame.destroy()
        self.add_song_parameters_screen(accepted_songs)
        self.accept_button1.destroy()

    def click_accept_button2(self) -> None:
        for frame in self.songframes.values():
            convert_file_to_mp3_and_trim(frame.label['text'], frame.get_time_values(), frame.tags_frame.get_fields_data())
    
    def add_song_selection_screen(self) -> None:
        accepted_formats = ['.mp3', '.webm']
        files_for_conversion = [f for f in os.listdir() if os.path.splitext(f)[1] in accepted_formats]

        if not files_for_conversion:
            self.no_files_screen()
            return

        for f in files_for_conversion:
            frame = FileFrame(self.window, f, padx=40, pady=20)
            frame.pack()
            self.fileframes.update({f: frame})
        
        self.accept_button1 = tk.Button(self.window, text='Accept', command=self.click_accept_button1)
        self.accept_button1.pack()

    def add_song_parameters_screen(self, file_names: list[str]) -> None:
        for f in file_names:
            song_tags = SongTagsFinder(f).get_data()
            self.make_container_for_song(f, utils.time_to_str(utils.get_song_length(f)), song_tags)
        
        accept_button = tk.Button(self.window, text='Accept', command=self.click_accept_button2)
        accept_button.pack()

if __name__ == '__main__':
    window = Ui()
    window.check_FFMPEG()
    window.window.mainloop()
