import tkinter as tk
from tkinter.ttk import Progressbar
import os
import subprocess
import threading

from song_editor import convert_file
from ui_components import SongFrame, FileFrame
import utils

# TODO: handle the console returning "overwrite files? y/n" in the ui
# TODO: add scroll for too many songs
# TODO: chyba sa problemy z plikami ponad godzine moze to zobaczyc
# TODO: wrocic do zapisywania do folderu
# TODO: pozmieniac wyszukiwanie, zabezpieczyc to z genius szukanie

class Ui:
    def __init__(self) -> None:
        self.window = tk.Tk()
        self.window.geometry('800x600')
        v = tk.Scrollbar(self.window)
        v.pack(side=tk.RIGHT, fill=tk.Y)
        # self.main_frame = tk.Frame(self.window, width='1000', height='700')
        self.main_frame = tk.Canvas(self.window, yscrollcommand=v.set, width='800', height='4000')
        # self.main_frame = ScrolledCanvas(self.window)
        self.main_frame.pack(fill=tk.BOTH)
        v.config(command=self.main_frame.yview)
  
        self.songframes: dict[str: SongFrame] = {}
        self.fileframes: dict[str: FileFrame] = {}
    
    def no_files_screen(self) -> None:
        label = tk.Label(self.main_frame, text="No files found in the root directory")
        label.pack(padx=40, pady=40)

    def check_FFMPEG(self) -> None:
        try:
            subprocess.check_output(['ffmpeg', '-version'])
            self.add_song_selection_screen()
        # except FileNotFoundError:
        except subprocess.CalledProcessError:
            label = tk.Label(self.main_frame, text="FFMPEG is not installed, or not on PATH")
            label.pack(padx=40, pady=40)

    def make_container_for_song(self, file_name: str, song_length: str) -> None:
        if file_name in self.songframes:
            return None
        
        frame = SongFrame(self.main_frame, file_name, song_length)
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
        self.accept_button2.destroy()
        progress_bar = Progressbar(self.main_frame, orient=tk.HORIZONTAL, length=500, mode='determinate')
        progress_bar.pack()

        def inside_fn() -> None:
            for frame in self.songframes.values():
                convert_file(frame.label['text'], frame.get_time_values(), frame.tags_frame.get_fields_data())
                progress_bar['value'] += 100/len(self.songframes)
        threading.Thread(target=inside_fn).start()
        
    def add_song_selection_screen(self) -> None:
        # ffmpeg nie moze zmienic w miejscu pliku. Czyli nie moze byc a.mp3 -> a.mp3.
        # jesli chce tu dodac .mp3 to trzeba sie upewnic ze tytul bedzie inny
        accepted_formats = ['.mp3', '.webm', '.mp4']
        files_for_conversion = [f for f in os.listdir() if os.path.splitext(f)[1] in accepted_formats]

        if not files_for_conversion:
            self.no_files_screen()
            return

        for f in files_for_conversion:
            frame = FileFrame(self.main_frame, f, padx=40, pady=20)
            frame.pack()
            self.fileframes.update({f: frame})
        
        self.accept_button1 = tk.Button(self.main_frame, text='Accept', command=self.click_accept_button1)
        self.accept_button1.pack()

    def add_song_parameters_screen(self, file_names: list[str]) -> None:
        for f in file_names:
            self.make_container_for_song(f, utils.time_to_str(utils.get_song_length(f)))
        
        self.accept_button2 = tk.Button(self.main_frame, text='Accept', command=self.click_accept_button2)
        self.accept_button2.pack()


if __name__ == '__main__':
    window = Ui()
    window.check_FFMPEG()
    window.window.mainloop()
