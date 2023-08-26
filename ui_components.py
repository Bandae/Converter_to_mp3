import tkinter as tk
from tkinter import ttk
import re
from typing import Tuple

import utils
from song_tags_finder import find_song_data

SONG_TAGS = ['title', 'artist', 'album', 'date', 'genre']

class FileFrame(tk.Frame):
    def __init__(self, master, file_name: str, **kwargs) -> None:
        super().__init__(master, **kwargs)
        self.label = tk.Label(self, text=file_name)
        
        self.label.pack(side=tk.LEFT)
        self.checked = tk.IntVar()
        self.check = tk.Checkbutton(self, variable=self.checked)
        self.check.pack(side=tk.RIGHT)


class TimeEntry(tk.Entry):
    def __init__(self, master, default: str, **kwargs) -> None:
        super().__init__(master, **kwargs)
        self.default = default
        self.insert(0, default)
        self.bind("<FocusOut>", self.input_validation)

    @property
    def text(self) -> str:
        return self.get()

    @text.setter
    def text(self, value) -> None:
        self.delete(0, 'end')
        self.insert(0, value)
    
    def input_validation(self, event) -> None:
        # try different events, like key pressed to return to previous correct value,
        # instead of reseting the field to default
        time = self.text
        match = re.match(r'^(\d{1,2}):(\d{1,2}.\d{1,3}|\d{1,2})$', time)

        if not match:
            self.text = self.default
            return

        self.text = utils.time_to_str(utils.time_to_seconds(self.text))


class TagsFrame(tk.Frame):
    def __init__(self, master, file_name:str, **kwargs) -> None:
        super().__init__(master, **kwargs)
        self.fields = {}
        self.add_fields()
        self.add_button()
        self.file_name = file_name
    
    def add_fields(self) -> None:
        for tag in SONG_TAGS:
            frame = tk.Frame(self)
            label = tk.Label(frame, text=tag)
            entry = tk.Entry(frame)

            label.pack(side=tk.TOP)
            entry.pack(side=tk.BOTTOM, padx=10)
            frame.pack(side=tk.LEFT)

            self.fields.update({tag: entry})
    
    def update_fields(self, tags: dict[str, str]) -> None:
        for tag in tags:
            entry = self.fields.get(tag)
            entry.delete(0, 'end')
            entry.insert(0, tags[tag])

    def get_fields_data(self) -> dict[str, str]:
        tags = {}
        for field in self.fields:
            tags.update({field: self.fields[field].get()})
        return tags
    
    def add_button(self) -> None:
        search_button = tk.Button(self, text='Search', command=self.click_search_button)
        search_button.pack(side=tk.RIGHT)
    
    def click_search_button(self) -> None:
        tags = find_song_data(self.file_name)
        self.update_fields(tags)


class SongFrame(tk.Frame):
    def __init__(self, master, file_name: str, song_length: str, **kwargs) -> None:
        super().__init__(master, **kwargs)
        # TODO: clean up, make init smaller
        self.label = tk.Label(self, text=file_name)
        
        self.start_time = TimeEntry(self, default='0:00.000', width=10)
        self.end_time = TimeEntry(self, default=song_length, width=10)
        self.tags_frame = TagsFrame(self, file_name)

        separator_horizontal = ttk.Separator(master, orient='horizontal')

        self.bind("<FocusOut>", self.validate_times)

        self.label.pack(side=tk.LEFT)
        self.start_time.pack(side=tk.LEFT)
        self.end_time.pack(side=tk.LEFT)
        self.tags_frame.pack(side=tk.RIGHT, padx=20, pady=15)
        separator_horizontal.pack(fill='x')

    def get_time_values(self) -> Tuple[str, str]:
        return (self.start_time.text, self.end_time.text)
    
    def validate_times(self, event) -> None:
        self.start_time.input_validation(event)
        self.end_time.input_validation(event)

        start, end = utils.time_to_seconds(self.start_time.text), utils.time_to_seconds(self.end_time.text)
        length = utils.time_to_seconds(self.end_time.default)

        if start <= 0:
            start = 0
        
        if end >= length:
            end = length
        
        if start >= end:
            start = 0
            end = length
        
        start, end = utils.time_to_str(start), utils.time_to_str(end)
        self.start_time.text = start
        self.end_time.text = end
