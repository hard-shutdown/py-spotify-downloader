import argparse
import os
import sys

from pytube import YouTube
from pydub import AudioSegment
import ytmusicapi
import spotipy

from filters import *
from txtutils import *

def download_audio(track_youtube: YouTube, outpath: str = os.getcwd(), filename: str = 'audio'):
    audio_streams = track_youtube.streams.filter(only_audio=True)
    best_audio_stream = get_best_audio_stream(audio_streams)
    if best_audio_stream is None:
        print('Could not find audio track')
        sys.exit(1)
    print('Downloading audio track...')
    best_audio_stream.download(output_path=outpath, filename=filename)

def convert_to_mp3(filepath: str, mp3_filename: str = 'audio.mp3'):
    os.makedirs(os.path.dirname(mp3_filename), exist_ok=True)
    AudioSegment.from_file(filepath).export(mp3_filename, format='mp3')
    os.remove(filepath)

def full_download_track(track: typing.Any, ytmusic_client: ytmusicapi.YTMusic, outpath: str = os.getcwd()):
    if track is None:
        print('Could not find track')
        return

    print('Found Spotify Track: ' + create_search_query(track) + ' (' + str(round(track['duration_ms']/1000)) + ' seconds)')

    result = find_best(track, ytmusic_client.search(create_search_query(track), filter='songs', ignore_spelling=True))
    if result is None:
        print('Could not find track')
        sys.exit(1)
    print('Found YouTube Music Track: ' + result['title'] + ' by ' + result['artists'][0]['name'] + ' (' + str(result['duration_seconds']) + ' seconds)')
    tmp_filename = 'audio_' + result['videoId']
    download_audio(YouTube('?v=' + result['videoId']), '.', tmp_filename)
    print('Converting to mp3...')
    convert_to_mp3(tmp_filename, pretty_print_path(track, outpath) + '.mp3')



if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Download Spotify tracks, albums, and playlists.')
    parser.add_argument('url', metavar='url', type=str, help='Spotify URL')
    parser.add_argument('-o', '--outpath', metavar='outpath', type=str, default=os.getcwd(), help='Output path, defaults to current directory')
    args = parser.parse_args()
    
    ytmusic = ytmusicapi.YTMusic()
    sp = spotipy.Spotify(client_credentials_manager = spotipy.oauth2.SpotifyClientCredentials(client_id='3f50284096894e778263708c821ca4e7', client_secret='ef56831f6296405b8af3433740c4c169'))
    if args.url.__contains__('track'):
        track = sp.track(args.url)
        full_download_track(track, ytmusic, outpath=args.outpath)
    elif args.url.__contains__('playlist'):
        playlist = sp.playlist(args.url)
        if playlist is None:
            print('Could not find playlist')
            sys.exit(1)
        for track in playlist['tracks']['items']:
            full_download_track(track['track'], ytmusic, outpath=args.outpath)
    elif args.url.__contains__('album'):
        album = sp.album(args.url)
        if album is None:
            print('Could not find album')
            sys.exit(1)
        for track in album['tracks']['items']:
            full_download_track(track, ytmusic, outpath=args.outpath)