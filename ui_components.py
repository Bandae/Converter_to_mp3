import tkinter as tk
from tkinter import ttk
import re
from typing import Dict, Tuple

import utils


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
    def __init__(self, master, tags: Dict[str, str], **kwargs) -> None:
        super().__init__(master, **kwargs)
        self.tags = tags
        self.fields = {}
    
    def add_field(self, key: str, value: str) -> None:
        frame = tk.Frame(self)

        label = tk.Label(frame, text=key)
        entry = tk.Entry(frame)

        if value:
            entry.insert(0, value)

        label.pack(side=tk.TOP)
        entry.pack(side=tk.BOTTOM, padx=10)
        frame.pack(side=tk.LEFT)

        self.fields.update({key: entry})
    
    def add_fields(self) -> None:
        for tag in self.tags:
            self.add_field(tag, self.tags[tag])

    def get_fields_data(self) -> Dict[str, str]:
        tags = {}
        for field in self.fields:
            tags.update({field: self.fields[field].get()})
        
        return tags


class SongFrame(tk.Frame):
    def __init__(self, master, file_name: str, song_length: str, tags: Dict[str, str], **kwargs) -> None:
        super().__init__(master, **kwargs)
        # TODO: clean up, make init smaller
        self.label = tk.Label(self, text=file_name)
        
        self.start_time = TimeEntry(self, default='0:00.000', width=10)
        self.end_time = TimeEntry(self, default=song_length, width=10)

        self.tags_frame = TagsFrame(self, tags)
        self.tags_frame.add_fields()

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
