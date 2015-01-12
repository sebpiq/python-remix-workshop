import subprocess
import pychedelic


def convert(source, dest):
    """
    Converts sound file `source` to `dest`, normalizing at the same time to 44100Hz frame rate,
    16 bits depths. 
    """
    ffmpeg_args = ['ffmpeg', '-y', '-i', source, '-ar', '44100', '-sample_fmt', 's16', dest]
    ffmpeg = subprocess.Popen(ffmpeg_args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = ffmpeg.communicate() # !!! stderr contains non-error output !?
    return err


def read_mono(path):
    """
    Read sound file `path`, returns samples as mono, removing the second channel if there is one.
    """
    samples, infos = pychedelic.chunk.read_wav(path)
    return pychedelic.chunk.fix_channel_count(samples, 1)


def read_stereo(path):
    """
    Read sound file `path`, returns samples as stereo, duplicating the first channel if necessary.
    """
    samples, infos = pychedelic.chunk.read_wav(path)
    return pychedelic.chunk.fix_channel_count(samples, 2)


def write(samples, path):
    """
    Write `samples` to the file `path` in wav format
    """
    pychedelic.stream.to_wav_file(pychedelic.stream.iter(samples), path)