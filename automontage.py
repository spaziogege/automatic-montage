from math import sin
import os
from pprint import pprint
import subprocess
import ffmpeg
import opentimelineio as otio
from davinci_effects import dr_zoom
from math import floor

from readfolders import readFolder

def resolve_absolute_path(path):
    return os.path.abspath(os.path.expanduser(path))

def get_video_length_cmd_line(video_path):
    command = f'ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 {video_path}'
    process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE)
    output, _ = process.communicate()
    length = float(output)
    return length

def get_video_length(video_path):
    return ffmpeg.probe(resolve_absolute_path(video_path), cmd='ffprobe')['format']['duration']

def get_video_stream(streams):
    return [strm for strm in streams if strm['codec_type'] == 'video']

def get_video_fps(video_path):
    streams = ffmpeg.probe(resolve_absolute_path(video_path), cmd='ffprobe')['streams']
    video_stream = get_video_stream(streams)
    # DA QUI PER WORKSHOP / TUTORIAL 
    pprint(video_stream)
    command = f'ffprobe -v error -select_streams v:0 -show_entries stream=r_frame_rate -of default=noprint_wrappers=1:nokey=1 {video_path}'
    process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE)
    output, _ = process.communicate()
    fps = float(output.splitlines()[0].split(b'/')[0]) / float(output.splitlines()[0].split(b'/')[1])
    rfps = otio.opentime.RationalTime.nearest_valid_timecode_rate(fps)
    return rfps

def sec2hms(seconds):
    min, sec = divmod(float(seconds), 60)
    hor, min = divmod(min, 60)
    print("sec2hms: " + str(sec))
    rate = "%02d:%02d:" % (hor, min) + ('{:022.20f}'.format(sec))#[0:6]
    print("sec2hms rate: " + rate)
    return rate

def createchunks(video, vid_dur, chunk_dur, out_dir):
    chunks = list()
    for n in range(0, vid_dur / chunk_dur):
        out_file = resolve_absolute_path(out_dir + video[:-4] + '_chunk_' + str(n) + '.mp4')
        cmd = 'ffmpeg -y -v quiet'
        cmd += ' -i ' + video
        cmd += ' -vcodec copy'
        cmd += ' -ss ' + sec2hms(n*chunk_dur)
        cmd += ' -t ' + sec2hms(chunk_dur)
        cmd += ' ' + out_file
        print(cmd)
        os.system(cmd)
        chunks.append(out_file)
    return chunks

def is_some_time_left(source, chunk_size):
    return float(source['length']) - float(source['current_start']) >= chunk_size

def still_some_time_left(sources, chunk_size):
    is_left = True
    for source in sources:
        is_left = is_left or is_some_time_left(sources[source], chunk_size)
    return is_left

if __name__ == "__main__":
    
    base_path = './source-files/'
    sources = {}
    chunk_size = 0.6
    out_folder = './out'
    name = f'./sauce-{chunk_size}'
    output = f'./{name}.otio'

    limitc = 0
    limit_debug = 9999
    for file in readFolder(base_path):
        if limitc < limit_debug:
            sources[file] = {
                'length': get_video_length(base_path + file),
                'left_length': get_video_length(base_path + file),
                'current_start': 0,
                'path': base_path + file,
                'abs_path': resolve_absolute_path(base_path + file),
                'fps': get_video_fps(base_path + file),
            }
        limitc = limitc + 1

    # build the structure
    timeline = otio.schema.Timeline(name)

    track = otio.schema.Track(name)
    timeline.tracks.append(track)

    clip_id = 0
    debug_limit = 99999

    while still_some_time_left(sources, chunk_size) and clip_id < debug_limit:
        for source_name in sources:
            source = sources[source_name]
            fps = source['fps']
            current_start = source['current_start']
            next_start = current_start + chunk_size
            length = source['length']

            if is_some_time_left(source, chunk_size):
                time_string = sec2hms(0)
                print(fps)
                print(time_string)

                source_start_time = otio.opentime.from_time_string( time_string, fps )
                source_duration = otio.opentime.from_time_string( sec2hms(length), fps )
                available_range = otio.opentime.TimeRange( source_start_time, source_duration )

                source_media_reference = otio.schema.ExternalReference(
                    target_url=source['abs_path'],
                    # available range is the content available for editing
                    available_range=available_range
                )

                chunk_start_time = sec2hms(current_start)
                chunk_duration = sec2hms(chunk_size)
                chunk_source_range = otio.opentime.TimeRange(
                    start_time=otio.opentime.from_time_string(chunk_start_time, fps),
                    duration=otio.opentime.from_time_string(chunk_duration, fps)
                )

                # attach the reference to the clip
                clip = otio.schema.Clip(
                    name=f"Clip{clip_id + 1}",
                    media_reference=source_media_reference,

                    # the source range represents the range of the media that is being
                    # 'cut into' the clip.
                    source_range=chunk_source_range
                )

                # transform = otio.schema.Effect()
                # transform.from_json_string('{"OTIO_SCHEMA":"Effect.1","metadata":{"Resolve_OTIO":{"Effect Name":"Transform","Enabled":true,"Name":"Transform","Parameters":[{"Default Parameter Value":1.0,"Key Frames":{},"Parameter ID":"transformationZoomX","Parameter Value":1.2199997901916505,"Variant Type":"Double","maxValue":100.0,"minValue":0.0},{"Default Parameter Value":1.0,"Key Frames":{},"Parameter ID":"transformationZoomY","Parameter Value":1.2199997901916505,"Variant Type":"Double","maxValue":100.0,"minValue":0.0}],"Type":2}},"name":"","effect_name":"Resolve Effect"}')
                # cl.set_transform(transform)

                """ ef = otio.schema.Effect(
                    name="blur it",
                    effect_name="blur",
                    metadata={"foo": "bar"}
                ) """

                #cl.effects.append(dr_zoom(1.21, 1.21))

                # put the clip into the track
                track.append(clip)

                # remember where we got for the next cycle
                source['current_start'] = next_start
        
        clip_id = clip_id + 1

    # write the file to disk
    otio.adapters.write_to_file(timeline, output)

    """  # step 1. create 15 sec. chunks of first 60 sec. of content
    vid1_chunks = createchunks('vid1.mp4', 60, 15)
    vid2_chunks = createchunks('vid2.mp4', 60, 15)

    # step 2. create a list.txt file (alternating order)
    filenames = [None] * len(vid1_chunks)
    filenames[::2] = vid1_chunks[::2]
    filenames[1::2] = vid2_chunks[1::2]
    with open('list.txt', 'w') as listfile:
        for fname in filenames:
            listfile.write('file \'' + fname + '\'\n')

    # step 3. concatenate
    cmd = 'ffmpeg -y -v quiet -f concat -i list.txt -c copy final.mp4'
    os.system(cmd) """