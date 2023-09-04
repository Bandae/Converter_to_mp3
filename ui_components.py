import tkinter as tk
from tkinter import ttk
import re

import utils
from song_tags_finder import find_song_data

SONG_TAGS = ['title', 'artist', 'album', 'date', 'genre']

class FileFrame(tk.Frame):
    '''tkinter Frame with the name of a file and a checkbox to mark if the file is to be processed.'''
    def __init__(self, master, file_name: str, **kwargs) -> None:
        super().__init__(master, **kwargs)
        label = tk.Label(self, text=utils.shorten_name(file_name, 40))
        
        label.pack(side=tk.LEFT)
        self.checked = tk.IntVar()
        check = tk.Checkbutton(self, variable=self.checked)
        check.pack(side=tk.RIGHT)


class TimeEntry(tk.Entry):
    '''A single tkinter Entry for entering a time value, with validation and a default format.'''
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
    
    def input_validation(self, event: tk.Event | None = None) -> None:
        '''
        Matches the passed text with a number of different ways of passing time values.
        If no match, sets the text back to default value.
        If matched, turns the time to standard format.
        '''
        time = self.text
        match = re.match(r'^(\d{1,2}):(\d{1,2}.\d{1,3}|\d{1,2})$', time)

        if not match:
            self.text = self.default
            return

        self.text = utils.time_to_str(utils.time_to_seconds(self.text))


class TagsFrame(tk.Frame):
    '''
    tkinter Frame containing fields for entering ID3 tags for a file,
    and a search button for using the Song Finder
    '''
    def __init__(self, master, file_name:str, **kwargs) -> None:
        super().__init__(master, **kwargs)
        self.file_name = file_name
        self.fields = {}
        for tag in SONG_TAGS:
            frame = tk.Frame(self)
            label = tk.Label(frame, text=tag)
            entry = tk.Entry(frame, width=15)

            label.pack(side=tk.TOP)
            entry.pack(side=tk.BOTTOM, padx=10)
            frame.pack(side=tk.LEFT)

            self.fields.update({tag: entry})
        
        search_button = tk.Button(self, text='Search', command=self.click_search_button)
        search_button.pack(side=tk.RIGHT)

    def get_fields_data(self) -> dict[str, str]:
        '''Returns a dictionary with the tags from entry widgets.'''
        return {name: tag.get() for name, tag in self.fields}
    
    def click_search_button(self) -> None:
        '''Uses the tag finder, and updates entries with tags found in musicbrainz/genius'''
        tags = find_song_data(self.file_name)
        for tag in tags:
            entry = self.fields.get(tag)
            entry.delete(0, 'end')
            entry.insert(0, tags[tag])


class SongFrame(tk.Frame):
    '''
    tkinter Frame for collecting data for each file from the user.
    Contains entry boxes for trim times, and a TagsFrame for inputing ID3 tags.
    '''
    def __init__(self, master, file_name: str, file_length: str, **kwargs) -> None:
        super().__init__(master, **kwargs)
        label = tk.Label(self, text=utils.shorten_name(file_name, 25))
        
        self.start_time = TimeEntry(self, default='0:00.000', width=10)
        self.end_time = TimeEntry(self, default=file_length, width=10)
        self.tags_frame = TagsFrame(self, file_name)

        separator_horizontal = ttk.Separator(master, orient='horizontal')

        self.bind("<FocusOut>", self.validate_times)

        label.pack(side=tk.LEFT)
        self.start_time.pack(side=tk.LEFT)
        self.end_time.pack(side=tk.LEFT)
        self.tags_frame.pack(side=tk.RIGHT, padx=20, pady=15)
        separator_horizontal.pack(fill='x')

    def get_time_values(self) -> tuple[str, str]:
        return (self.start_time.text, self.end_time.text)
    
    def validate_times(self, event: tk.Event | None = None) -> None:
        '''
        Validates trim times: is start time >= 0, end time <= file length, start >= end.
        If times fail these checks, resets them to default.
        Otherwise, fits the times entered to standard format.
        '''
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
