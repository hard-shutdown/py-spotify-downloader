import os
import typing
from urllib3.util import parse_url

def create_search_query(track: typing.Any) -> str:
    end = track['name'] + ' by'
    for artist in track['artists']:
        end += ' ' + artist['name'] + ','
    return end[:-1]

def combine_artists(artists_list: list) -> str:
    combined_artists = ''
    for artist in artists_list:
        combined_artists += artist['name'] + ', '
    return combined_artists[:-2]

def pretty_print_path(track: typing.Any, outpath: str) -> str:
    return os.path.join(outpath, track['album']['name'], combine_artists(track['artists']), track['name'])