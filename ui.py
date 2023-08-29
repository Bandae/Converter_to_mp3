import tkinter as tk
from tkinter.ttk import Progressbar
import os
import subprocess
import threading

from song_editor import convert_file
from ui_components import SongFrame, FileFrame
import utils

# TODO: handle the console returning "overwrite files? y/n" in the ui
# TODO: might have some problems with >1hour videos
# TODO: save to folder instead of root folder
# TODO: check tags_finder
# TODO: only print part of titles to save space
# TODO: check times in ui_components, maybe make code shorter


class MainWindow(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.resizable(width=False, height=False)

        self.songframes: dict[str: SongFrame] = {}
        self.fileframes: dict[str: FileFrame] = {}

        self.canvas = tk.Canvas(self)
        scroll = tk.Scrollbar(self, command=self.canvas.yview)
        scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.canvas.pack(fill=tk.BOTH)
        self.canvas.configure(yscrollcommand=scroll.set)

        self.frame = tk.Frame(self.canvas)
        self.canvas.create_window(0, 0, window=self.frame, anchor='nw')

        self.frame.update_idletasks()
        self.canvas.configure(scrollregion=self.canvas.bbox('all'))
        self.canvas.bind('<Configure>', self.on_configure_canvas)

        self.check_FFMPEG()

    def check_FFMPEG(self) -> None:
        try:
            subprocess.check_output(['ffmpeg', '-version'])
            self.add_song_selection_screen()
        # except FileNotFoundError:
        except subprocess.CalledProcessError:
            label = tk.Label(self.frame, text="FFMPEG is not installed, or not on PATH")
            label.pack(padx=40, pady=40)

    def make_container_for_song(self, file_name: str, song_length: str) -> None:
        if file_name in self.songframes:
            return None
        
        frame = SongFrame(self.frame, file_name, song_length)
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
        self.canvas.config(width=1000, height=600)

    def click_accept_button2(self) -> None:
        self.accept_button2.destroy()
        progress_bar = Progressbar(self.frame, orient=tk.HORIZONTAL, length=500, mode='determinate')
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
            label = tk.Label(self.frame, text="No files found in the root directory")
            label.pack(padx=40, pady=40)
            return

        for f in files_for_conversion:
            frame = FileFrame(self.frame, f, width=400, height=50)
            frame.pack()
            # frames automatically fit size to the child widgets, this line prevents it, so that all checkboxes can line up
            # needs setting width and height to actually appear
            frame.pack_propagate(0)
            self.fileframes.update({f: frame})
        
        self.accept_button1 = tk.Button(self.frame, text='Accept', command=self.click_accept_button1)
        self.accept_button1.pack()
        # <configure> event not fired when changing widgets in frame, needs this line
        self.canvas.config(width=400)

    def add_song_parameters_screen(self, file_names: list[str]) -> None:
        for f in file_names:
            self.make_container_for_song(f, utils.time_to_str(utils.get_song_length(f)))
        
        self.accept_button2 = tk.Button(self.frame, text='Accept', command=self.click_accept_button2)
        self.accept_button2.pack()

    def on_configure_canvas(self, event) -> None:
        # w, _ = event.width, event.height
        # natural = self.frame.winfo_reqwidth()
        # self.canvas.itemconfigure('inner', width=w if w > natural else natural)
        self.canvas.configure(scrollregion=self.canvas.bbox('all'))


if __name__ == '__main__':
    window = MainWindow()
    window.mainloop()
