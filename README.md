# .mp3 converting app

Running ui.py opens a tkinter window with frames for all .webm and .mp3 files in the root directory.

Each has two entry widgets with time formated as mm:ss.sss. The first one is initialized to 0, the second to the length of the file.

Each frame also has entry widgets for ID3 tags. These are initialized to values from musicbrainz and genius api, after a search made with the name of the file.

After clicking the "Run" button:
- each file will be converted to .mp3,

- If the time values are changed, the file will be cut, the first time being the beginning and the second - the end of the new file,

- The ID3 tags in the entry widgets will be written into the files,

- The name of each file will be set to its 'title' tag, or to the original name of the file, if there is no 'title' tag.

- The files will be placed in a *./music* directory (it will be created if there is none)

The app needs a .env file with a genius api key, if that api is to be used.
add
GENIUS_KEY=Bearer *your key here*
to the .env file

[Get a key](https://docs.genius.com/)
(make a genius account and connect it to the docs page)


*Uses:*
- [ffmpeg-python](https://github.com/kkroening/ffmpeg-python)
- [mutagen](https://mutagen.readthedocs.io/en/latest/)
- [the musicbrainz api](https://musicbrainz.org/doc/MusicBrainz_API)
- [the Genius api](https://docs.genius.com/) 