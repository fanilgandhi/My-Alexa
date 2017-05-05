from global_setup import *
from alexa import Alexa
from audio_handler import *

import pyaudio
import wave
import snowboydetect
import requests

CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 16000
SECONDS = 8
max_frames = int(RATE/CHUNK * SECONDS)

model_path = os.path.join(RESOURCES_DIR , "alexa.umdl")
snowboy_resource = os.path.join(RESOURCES_DIR , "common.res")

detector = snowboydetect.SnowboyDetect(resource_filename = snowboy_resource , model_str = model_path.encode())
detector.SetAudioGain(1)
sensitivity_str = '0.5'
detector.SetSensitivity('0.5')

data_count = 0 
buffer = []

def record_callback(in_data , frame_count , time_info , status):
	global data_count
	global buffer
	if RAM.get("microphone_should_record") :
		buffer.append(in_data)
		data_count += 1
		if (data_count >= max_frames):
			RAM.set("microphone_should_record" , False)
			print "Ending Recording"
			
			media_player.play(media_player.say_stop)

			wf = wave.open(recording_file, 'wb')
			wf.setnchannels(CHANNELS)
			wf.setsampwidth(pyaudio_source.get_sample_size(FORMAT))
			wf.setframerate(RATE)
			wf.writeframes(b''.join(buffer))
			wf.close()

			RAM.set("microphone_recording_complete" , True)
			data_count = 0
			buffer = []
	else:
		ans = detector.RunDetection(in_data)
		if ans > 0 :
			log("HotWord Detected")
			time.sleep(0.05)
			media_player.play(media_player.say_start)
			RAM.set("microphone_should_record" , True )

	return (None , pyaudio.paContinue)

def internet_on():
	log("Checking Internet Connection...")
	try:
		requests.get('https://api.amazon.com/auth/o2/token')
		log("Connection OK")
		return True
	except:
		log("Connection Failed")
		return False
		

if __name__ == '__main__':
	pyaudio_source = pyaudio.PyAudio()
	microphone = pyaudio_source.open(format = FORMAT , channels = CHANNELS , rate = RATE , input = True , output = False , frames_per_buffer=CHUNK , stream_callback = record_callback)
	media_player = AudioPlayer()
	
	RAM.set("microphone_recording_complete" , False)
	while not  internet_on():
		media_player.play(media_player.say_alarm)
		time.sleep(3)

	alexa = Alexa(media_player)
	
	print "Starting Stream"
	microphone.start_stream()

	media_player.play(media_player.say_hello)
	while True:
		if RAM.get("microphone_recording_complete") :
			q = alexa.alexa_speech_recognizer()
			RAM.set("microphone_recording_complete" , False)
		else:
			time.sleep(0.3)
		
	log("Some Error Occured")
	microphone.stop_stream()

	microphone.close()
	pyaudio_source.terminate()

