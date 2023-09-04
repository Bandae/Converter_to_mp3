# .mp3 converting app
#### Convert files to .mp3, trim them, input ID3 tags (title, artist, etc.)


```sh
python -m pip install -r requirements.txt
```

Run `python -m ui`
- Choose mode. "other" to convert files to mp3, write ID3 tag, trim; "mp3" to select mp3 files and skip the conversion.
- All files with the appropriate extensions in the root directory are displayed. Select which ones to process.
- Each file has two entry widgets with time formated as mm:ss.sss. The first one is initialized to 0, the second to the length of the file. To trim the file, change the values, first entry for new start, second for new end. Ignore for no trimming.
- Each frame also has entry widgets for ID3 tags. Click "search" to find tags from musicbrainz and genius api, searching with the name of the file.
- Click run. New files will be saved in a newly created *./music* directory. The file names will be set to its "title" tag, or to the original name of the file, if there is no "title" tag.


The app needs a .env file with a genius api key, if that api is to be used.
add
GENIUS_KEY=Bearer *your key here*
to the .env file

[Get a key](https://docs.genius.com/)
(make a genius account and connect it to the docs page)


*Uses:*
- [ffmpeg](https://ffmpeg.org/)
- [mutagen](https://mutagen.readthedocs.io/en/latest/)
- [the musicbrainz api](https://musicbrainz.org/doc/MusicBrainz_API)
- [the Genius api](https://docs.genius.com/) 