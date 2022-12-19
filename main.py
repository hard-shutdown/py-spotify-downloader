import argparse
from multiprocessing.pool import ThreadPool
import os
import subprocess
import sys

from pytube import YouTube
import ytmusicapi
import spotipy

from filters import *
from txtutils import *

def download_audio(track_youtube: YouTube, outpath: str = os.getcwd(), filename: str = 'audio'):
    audio_streams = track_youtube.streams.filter(only_audio=True)
    best_audio_stream = get_best_audio_stream(audio_streams)
    if best_audio_stream is None:
        print('Could not find audio track')
        return
    best_audio_stream.download(output_path=outpath, filename=filename)

def convert_to_different_format(filepath: str, track: typing.Any, out_filename: str = 'audio.m4a'):
    os.makedirs(os.path.dirname(out_filename), exist_ok=True)
    #AudioSegment.from_file(filepath).export(mp3_filename, format='mp3')
    #os.system('ffmpeg -i ' + filepath + ' ' + out_filename)
    with open(os.devnull, 'w') as FNULL:
        subprocess.call(['ffmpeg', '-i', filepath] + create_metadata_args(track) + [out_filename, '-y'], stdout=FNULL, stderr=subprocess.STDOUT)
    os.remove(filepath)

def full_download_track(track: typing.Any, ytmusic_client: ytmusicapi.YTMusic, outpath: str = os.getcwd(), out_format: str = 'm4a'):
    if track is None:
        print('Could not find track')
        return

    print('Found Spotify Track: ' + create_search_query(track) + ' (' + str(round(track['duration_ms']/1000)) + ' seconds)')

    result = find_best(track, ytmusic_client.search(create_search_query(track), filter='songs', ignore_spelling=True))
    if result is None:
        print('Could not find corresponding YT track')
        return
    print('Found YouTube Music Track: ' + result['title'] + ' by ' + result['artists'][0]['name'] + ' (' + str(result['duration_seconds']) + ' seconds)')
    tmp_filename = 'audio_' + result['videoId']
    yt_obj = YouTube('https://www.youtube.com/watch?v=' + result['videoId'])
    yt_obj.bypass_age_gate()
    download_audio(yt_obj, '.', tmp_filename)
    convert_to_different_format(tmp_filename, track, pretty_print_path(track, outpath) + '.' + out_format)
    print('Converted ' + track['name'] + ' by ' + track['artists'][0]['name'] + ' to ' + out_format + ' format')

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Download Spotify tracks, albums, and playlists.')
    parser.add_argument('url', metavar='url', type=str, help='Spotify URL')
    parser.add_argument('-o', '--outpath', metavar='outpath', type=str, default=os.getcwd(), help='Output path, defaults to current directory')
    parser.add_argument('-f', '--format', metavar='format', type=str, default='m4a', help='Output format, defaults to m4a')
    parser.add_argument('--parallel', metavar='parallel', type=int, default=4, help='Number of parallel downloads, defaults to 4')
    args = parser.parse_args()

    if args.parallel < 1:
        print('Number of parallel downloads must be at least 1')
        sys.exit(1)
    
    ytmusic = ytmusicapi.YTMusic()
    sp = spotipy.Spotify(client_credentials_manager = spotipy.oauth2.SpotifyClientCredentials(client_id='3f50284096894e778263708c821ca4e7', client_secret='ef56831f6296405b8af3433740c4c169'))
    if args.url.__contains__('track'):
        track = sp.track(args.url)
        if track is None:
            print('Could not find track')
            sys.exit(1)
        full_download_track(track, ytmusic, args.outpath, args.format)
    elif args.url.__contains__('playlist'):
        playlist = sp.playlist(args.url)
        if playlist is None:
            print('Could not find playlist')
            sys.exit(1)
        run_arg_list = []
        for track in playlist['tracks']['items']:
            run_arg_list.append((track['track'], ytmusic, args.outpath, args.format))
        with ThreadPool(args.parallel) as p:
            p.starmap(full_download_track, run_arg_list)
    elif args.url.__contains__('album'):
        album = sp.album(args.url)
        if album is None:
            print('Could not find album')
            sys.exit(1)
        run_arg_list = []
        for track in album['tracks']['items']:
            run_arg_list.append((track, ytmusic, args.outpath, args.format))
        with ThreadPool(args.parallel) as p:
            p.starmap(full_download_track, run_arg_list)
    elif args.url.__contains__('artist'):
        artist = sp.artist(args.url)
        if artist is None:
            print('Could not find artist')
            sys.exit(1)
        run_arg_list = []
        print('Pulling albums and all tracks from artist...')
        for album in sp.artist_albums(artist['id'])['items']:
            album = sp.album(album['id'])
            for track in album['tracks']['items']:
                track = sp.track(track['id'])
                run_arg_list.append((track, ytmusic, args.outpath, args.format))
        with ThreadPool(args.parallel) as p:
            p.starmap(full_download_track, run_arg_list)