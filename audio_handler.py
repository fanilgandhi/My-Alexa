from global_setup import *

import vlc

vlc_instance = vlc.Instance()

class AudioPlayer():
	
	def __init__(self):	
		self.vlc_player = vlc_instance.media_player_new()
		self.say_yes = vlc_instance.media_new(os.path.join(RESOURCES_DIR , "alexayes.mp3"))
		self.say_hello = vlc_instance.media_new(os.path.join(RESOURCES_DIR , "hello.mp3"))
		self.say_start = vlc_instance.media_new(os.path.join(RESOURCES_DIR , "start.mp3"))
		self.say_stop = vlc_instance.media_new(os.path.join(RESOURCES_DIR , "stop.mp3"))
		self.say_error = vlc_instance.media_new(os.path.join(RESOURCES_DIR , "error.mp3"))
		self.say_alarm = vlc_instance.media_new(os.path.join(RESOURCES_DIR , "alarm.mp3"))
		self.say_response = vlc_instance.media_new(response_file)

	def play(self , media = None):
		if media != None :
			RAM.set("audio_player_is_playing" , True) 
			self.vlc_player.set_media(media)
			self.vlc_player.play()
			RAM.set("audio_player_is_playing" , False) 
		else:
			pass

