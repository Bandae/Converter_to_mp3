from typing import Optional, Dict
import re

import requests
import musicbrainzngs
from dotenv import dotenv_values

SONG_TAGS = ['title', 'artist', 'album', 'date', 'genre']


class SongTagsFinder:
    # TODO: improve functions for getting data, maybe put each api into its own class so expanding is easier
    def __init__(self, search_q: str) -> None:
        self.search_q = self.process_search_q_str(search_q)
    
    def process_search_q_str(self, search_q: str) -> str:
        '''
        Processes the string for better results from api calls:
        -removes the possible file format suffix
        -removes all special characters excluding dashes
        -turns first letters of each word to uppercase, and the rest to lowercase
        '''
        str_no_suffix = re.sub(r'.[\d\w]{1,5}$', '', search_q)
        str_alpahnum = re.sub(r'[^\w\d-]', ' ', str_no_suffix)
        str_lowercase = re.sub(r'([\w])([\w]+)', lambda x: x[1].upper() + x[2].casefold(), str_alpahnum)
        
        return str_lowercase
    
    def get_song_data_genius(self) -> Optional[Dict[str, str]]:
        try:
            GENIUS_KEY = dotenv_values(".env")["GENIUS_KEY"]
        except KeyError:
            # log this
            return

        url = "http://api.genius.com/search"
        headers = {'Authorization': GENIUS_KEY}
        params = {'q': self.search_q}

        response = requests.get(url, params=params, headers=headers)
        if not response:
            return

        hits = response.json()['response']['hits']
        if not hits:
            return
        
        hit = hits[0]['result']

        title = hit.get('title')
        artist = hit.get('artist_names')
        date = str(hit.get('release_date_components').get('year')) if hit.get('release_date_components') else None
        
        return {'title': title, 'artist': artist, 'date': date}

    def get_song_data_musicbrainz(self) -> Optional[Dict[str, str]]:
        musicbrainzngs.set_useragent('song_scraping_app', '1.0')
        hit = musicbrainzngs.search_recordings(query=self.search_q, limit=1)

        if not hit:
            return
        else:
            hit = hit['recording-list'][0]
        
        title = hit.get('title')
        artist = hit.get('artist-credit')[0].get('name') if hit.get('artist-credit') else None
        album = hit.get('release-list')[0].get('title') if hit.get('release-list') else None
        date = str(hit.get('release-list')[0].get('date')) if hit.get('release-list') else None

        return {'title': title, 'artist': artist, 'album': album, 'date': date}

    def compare_song_data_containers(self, dict1: Dict[str, str], dict2: Dict[str, str]) -> Dict[str, str]:
        # fix, unreadable
        
        return_dict = {}

        if not dict1 and dict2:
            for key in dict2:
                return_dict.update({key: dict2[key]})
        
        elif not dict2 and dict1:
            for key in dict1:
                return_dict.update({key: dict1[key]})

        elif dict1 and dict2:
            for key in set(dict1.keys()) & set(dict2.keys()):
                # in_both = set(data1.songdata[key]).intersection(set(data2.songdata[key]))
                # in_both = in_both[0] if in_both else ''

                return_dict.update({key: dict1[key]})

            for key in set(dict1.keys()).symmetric_difference(set(dict2.keys())):
                if dict1.get(key):
                    return_dict.update({key: dict1[key]})
                else:
                    return_dict.update({key: dict2[key]})

        for key in SONG_TAGS:
            if key not in return_dict:
                return_dict.update({key: ''})
            
        return return_dict

def find_song_data(file_name: str) -> dict[str, str]:
    # add a dict as a parameter if the file is already mp3 and has tags
    finder = SongTagsFinder(file_name)
    genius_data = finder.get_song_data_genius()
    musicbrainz_data = finder.get_song_data_musicbrainz()
    
    final_data = finder.compare_song_data_containers(genius_data, musicbrainz_data)
    return final_data
