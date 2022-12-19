import pytube
import typing

def get_best_audio_stream(streams) -> pytube.Stream:
    best_bitrate = 0
    best_stream = streams[0]
    for stream in streams:
        if stream.abr is None:
            continue
        bitrate = int(stream.abr[:-4])
        if bitrate > best_bitrate:
            best_bitrate = bitrate
            best_stream = stream
    return best_stream

def find_best(track: typing.Any, results: typing.Any) -> typing.Any:
    duration_seconds_spotify = (track['duration_ms']/1000)%60
    best_res = results[0]
    for result in results:
        if result['title'] == track['name']:
            artlist = []
            for artist in result['artists']:
                artlist.append(artist['name'])
            if artlist.__contains__(track['artists'][0]['name']):
                duration_seconds_youtube = result['duration_seconds']
                if abs(duration_seconds_spotify - duration_seconds_youtube) < abs(duration_seconds_spotify - best_res['duration_seconds']):
                    best_res = result
                break

    return best_res
