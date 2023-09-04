import tkinter as tk
import os
import subprocess
import threading

from song_editor import process_file
from ui_components import SongFrame, FileFrame
import utils

# TODO: handle the console returning "overwrite files? y/n" in the ui
# TODO: problems with > 1hour long videos, only mm:ss format used in .utils
# TODO: check tags_finder
# TODO: check times in ui_components, maybe make code shorter
# TODO: for choosing time, try different events, not resetting the field but returning to last correct value etc
# TODO: handle possible errors returned in console by ffrobe on song length
# TODO: allow option to overwrite tags, or show tags that already exist
# TODO: different ffmpeg call if no trimming.

class MainWindow(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.resizable(width=False, height=False)

        self.songframes: dict[str: SongFrame] = {}
        self.fileframes: dict[str: FileFrame] = {}

        # Creates a scrollable frame
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
        '''Shows an error message if FFMPEG is not installed.'''
        try:
            subprocess.check_output(['ffmpeg', '-version'])
            self.choose_mode_screen()
        # except FileNotFoundError:
        except subprocess.CalledProcessError:
            label = tk.Label(self.frame, text="FFMPEG is not installed, or not on PATH")
            label.pack(padx=40, pady=40)

    def choose_mode_screen(self) -> None:
        '''Creates a screen for choosing to either convert files to mp3 and process, or only process mp3 files in the directory'''
        self.mode_frame = tk.Frame(self.frame)
        sm_frame = tk.Frame(self.mode_frame)
        label = tk.Label(self.mode_frame, text='Choose to convert files to mp3 and process, or select mp3 files to process (cut, write tags)', wraplength=300)
        mp3_button = tk.Button(sm_frame, text='mp3', command=lambda: self.add_song_selection_screen(mp3s=True))
        video_button = tk.Button(sm_frame, text='other', command=self.add_song_selection_screen)

        self.mode_frame.pack(padx=40, pady=40)
        sm_frame.pack(side=tk.BOTTOM, pady=20)
        label.pack(side=tk.TOP)
        mp3_button.pack(side=tk.RIGHT, padx=10)
        video_button.pack(side=tk.LEFT, padx=10)

    def make_container_for_song(self, file_name: str, song_length: str) -> None:
        if file_name in self.songframes:
            return None
        
        frame = SongFrame(self.frame, file_name, song_length)
        frame.pack()
        self.songframes.update({file_name: frame})

    def click_accept_button1(self) -> None:
        '''Passes all the files marked by the user for processing to add_song_parameters_screen'''
        accepted_songs = [file_name for file_name, frame in self.fileframes.items() if frame.checked.get()]
        if not accepted_songs:
            return
        for frame in self.fileframes.values():
            frame.destroy()
        self.add_song_parameters_screen(accepted_songs)
        self.accept_button1.destroy()
        self.canvas.config(width=1000, height=600)

    def click_accept_button2(self) -> None:
        '''Collects passed data, processes all the audio files, with a progress bar added to the ui.'''
        self.accept_button2.destroy()
        progress_bar = tk.ttk.Progressbar(self.frame, orient=tk.HORIZONTAL, length=500, mode='determinate')
        progress_bar.pack()

        def inside_fn() -> None:
            for file_name, frame in self.songframes.items():
                frame.validate_times()
                process_file(file_name, frame.get_time_values(), frame.tags_frame.get_fields_data(), mp3s=self.mp3s)
                progress_bar['value'] += 100/len(self.songframes)
        threading.Thread(target=inside_fn).start()
        
    def add_song_selection_screen(self, mp3s: bool=False) -> None:
        '''
        Collects all files with the right extensions, displays them in the ui to allow the user to choose which files to process.
        Allowed extensions:
        if mp3s: .mp3
        else: .mp4, .webm
        '''
        self.mp3s = mp3s
        self.mode_frame.destroy()

        accepted_formats = ['.mp3'] if mp3s else ['.webm', '.mp4']
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
        '''Creates a screen for passing ID3 tags, and choosing times for trimming files.'''
        for f in file_names:
            self.make_container_for_song(f, utils.time_to_str(utils.get_song_length(f)))
        
        self.accept_button2 = tk.Button(self.frame, text='Accept', command=self.click_accept_button2)
        self.accept_button2.pack()

    def on_configure_canvas(self, event) -> None:
        self.canvas.configure(scrollregion=self.canvas.bbox('all'))


if __name__ == '__main__':
    window = MainWindow()
    window.mainloop()
