import os
import random

import pychedelic
import numpy

from utils import freesound
from utils import sound_files

freesound.credentials = {
    'client_id': 'YOUR ID',
    'api_key': 'YOUR KEY'
}

# 1 - scraping

# Get 15 results with "keyword" from freesound.org
results = freesound.search('factory', max=50)
print('found %s results' % len(results))

# Those are the directories where we will save the sound files.
# You can change them if you want to save the files somewhere else.
mp3_dir = '/tmp/soundscape/mp3'
wav_dir = '/tmp/soundscape/wav'

# For each result, we will get an mp3, which we need to convert
# to wav in order to import it with Python.
all_wav_paths = []
for result in results:
	# Because of the way we mix the sounds together, we want only sounds
	# that are longer than 30 seconds.
	if result['duration'] < 20:
		print('sound %s too short, moving on to next' % result['id'])
		continue
	
	print('downloading %s' % result['id'])

	# Paths for the mp3 and wav files for that result
	mp3_file_path = os.path.join(mp3_dir, '%s.mp3' % result['id'])
	wav_file_path = os.path.join(wav_dir, '%s.wav' % result['id'])

	# Download mp3 and convert to wav
	freesound.download_sound(result['id'], mp3_file_path)
	sound_files.convert(mp3_file_path, wav_file_path)

	all_wav_paths.append(wav_file_path)

	# 15 sounds is enough otherwise our soundscape might be too busy
	if len(all_wav_paths) == 15: break


# 2 - collage
all_tracks = []

for wav_file_path in all_wav_paths:
	# Load sound.
	# Think of the loaded samples as a matrix, rows are frames, columns channels
	samples = sound_files.read_stereo(wav_file_path)
	samples_frame_count = samples.shape[0]

	# Very simple rms normalization, to get roughly the same volume
	# for each sound
	rms = float(numpy.sqrt(numpy.mean(samples[:,0]**2)))
	samples = samples * (0.1 / rms)

	# In order to get an interesting soundscape, we will generate a randomized
	# volume change for each sound, and therefore get a random mix of all them.
	# For this, we generate a list of successive ramps, which we will then combine.
	ramps = []						# list of successive random ramps
	previous = 0					# previous target
	total_ramp_frame_count = 0		# total number of frames contained in `ramps`

	# We iterate until we have enough frames in the ramp to cover our sound
	while total_ramp_frame_count < samples_frame_count:
	
		# pick random characteristics for the next ramp
		if previous < 0.2 and previous > 0:
			target = 0
			ramp_frame_count = random.randint(2, 16) * 44100
		else:
			target = random.random()
			while abs(target - previous) < 0.5: target = random.random()
			ramp_frame_count = random.randint(2, 8) * 44100

		# add to the other ramps and prepare next iteration
		ramps.append(numpy.linspace(previous, target, ramp_frame_count))
		previous = target
		total_ramp_frame_count = total_ramp_frame_count + ramp_frame_count

	# we generate the final ramp by combining all the successive ramps
	# and trimming to the same length as our sound
	ramp = numpy.concatenate(ramps)
	ramp = ramp[:samples_frame_count]

	# apply volume ramp to each channel of the sound
	samples[:, 0] = samples[:, 0] * ramp
	samples[:, 1] = samples[:, 1] * ramp

	all_tracks.append(samples)

# All our sounds have different lengths. If we want to mix them,
# we need them to have all the same length. Therefore we will choose
# the length of the shortest sound.
all_tracks_trimmed = []
min_frame_count = min([t.shape[0] for t in all_tracks])
for track in all_tracks:
	all_tracks_trimmed.append(track[:min_frame_count,:])

# We mix and normalize the volume
mixed = numpy.sum(all_tracks_trimmed, axis=0)
mixed = mixed / 2.0

# And finally write the generated samples to a sound file
sound_files.write(mixed, 'soundscape.wav')

print('soundscape saved in "soundscape.wav"')
