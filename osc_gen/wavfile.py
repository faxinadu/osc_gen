#!/usr/bin/env python
""" Extend wavfile to read data as normalised float """

try:
    import soundfile as sf
    HAS_SOUNDFILE = True
except ImportError:
    HAS_SOUNDFILE = False

import wave
import struct
import numpy as np


def _float_to_ibytes(vals):
    """ Convert a sequence of vals to 16-bit bytes """

    num = len(vals)
    afloats = np.array(vals)
    afloats = (afloats * 32768).astype('int')
    np.clip(afloats, -32768, 32767, out=afloats)
    return struct.pack('<{0}h'.format(num), *(aval for aval in afloats))


def _ibytes_to_float(vals):

    num = len(vals)
    num = int(num / 4)
    afloats = struct.unpack('<{0}h'.format(num), vals)
    afloats = np.array(afloats).astype(float)
    afloats /= 32768.
    return afloats.astype(float)


def _read_using_wave(filename):

    wave_file = wave.open(filename, 'r')
    if wave_file.getnchannels() != 1:
        raise ValueError("only mono supported")
    if wave_file.getsampwidth() != 2:
        raise ValueError("only 16 bit supported")
    num_frames = wave_file.getnframes()
    return _ibytes_to_float(wave_file.readframes(num_frames))


def read(filename):
    """ Read wav file and convert to normalised float """

    if HAS_SOUNDFILE:
        data, _ = sf.read(filename)
        # take only the first channel of the audio
        if len(data.shape) > 1:
            data = np.swapaxes(data, 0, 1)[0]
    else:
        data = _read_using_wave(filename)

    # center on 0
    data = data.astype(float)
    data -= np.mean(data)

    # normalise to +/- 1.0
    data_max = max(abs(data))
    return data / data_max


def write(data, filename, samplerate=44100):
    """ Write wav file """

    wave_file = wave.open(filename, 'w')
    wave_file.setframerate(samplerate)
    wave_file.setnchannels(1)
    wave_file.setsampwidth(2)
    wave_file.writeframes(_float_to_ibytes(data))
    wave_file.close()


def write_wavetable(wavetable, filename, samplerate=44100):
    """ Write wavetable to file """

    wave_file = wave.open(filename, 'w')
    wave_file.setframerate(samplerate)
    wave_file.setnchannels(1)
    wave_file.setsampwidth(2)
    for wt_wave in wavetable.get_waves():
        wave_file.writeframes(_float_to_ibytes(wt_wave))
    wave_file.close()