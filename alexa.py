
from global_setup import *
import requests , json , email

amazon_token_url = "https://api.amazon.com/auth/o2/token"
amazon_recog_url = "https://access-alexa-na.amazon.com/v1/avs/speechrecognizer/recognize"

CLIENT_ID = "amzn1.application-oa2-client.0f36c8f3f5b64b22aaefda8c6a519cf7"
CLIENT_SECRET = "684ee3ac2e6d0506f491fae4ac3e8066d3818e0d3c3af7ca00e404c8d09ec6e7"
REFRESH_TOKEN = "Atzr|IwEBIP4rixH0yfTKsD2mUefzHKS9d163VCMmsjflzpmcW-FklhvCWbxwF02Pj9H-OLoxQGJr2M6V1qxoZxvakCfhm3pNTF-ROAs_qVwja2uZ0XvEeJbsmcpBqFIEDKlPCz6JjtQ3zAVMC7OLpE6p_MMcBQB7NtTRc3p0uvLl8NhSyG6zFAo5dDRb-nsx9tv772dWGNPndGv0A4lRl080SSiJ9TnCYHg5FX3yWcStjlWLLUXcBf12wgi6IiypF0XDouwdRZPyYCdHu7dcIgITErnxJ6zNVAktBS0jkJ_ImuQJz1EEaZnBbKF9xzx-4YgXhtz6m2eiPnIh2GLa7BCyJvDq3XJjb0G468-PIslim7TCI9efuuCmCi2s02-wwA37GFInmuM02c74XOYCIbwPywqUuL7gRNiO1A9gvSopuILV042wBGNLMW7aMbiWHn177EznWO-Vm1v-Kf0OGQ6mkWLbsoOFCPp3taVIuMxra-i3-BY-kSN86Bg4d8OyP8LHdUPYTwGP1gE_KkpRGS_bX3EnaXQiQzTxFJ6jslTv2ayjqBEWxA"

class Alexa():
	def __init__(self , media_player):
		self.access_token = None
		self.refresh_token = REFRESH_TOKEN
		self.session = requests.Session()
		self.media_player = media_player

		if (self.refresh_token != None) :
			if (self.get_token() == None):
				log("No access_token could be obtained !!!")
				return 0+"" 
		else:
			log("No Refresh Token found")
			return 0+""


	def get_token(self):
		if self.access_token == None:
			data = {
				"client_id" : CLIENT_ID , 
				"client_secret" : CLIENT_SECRET , 
				"refresh_token" : REFRESH_TOKEN ,
				"grant_type" : "refresh_token",
			}
			start_time = time.time()
			response = self.session.post(amazon_token_url , data = data)
			if response.status_code != 200 :
				log("Could not get token")
				return None
			credentials = response.json()
			self.access_token = str(credentials["access_token"])
		return self.access_token

	def alexa_speech_recognizer(self):
		log(" Sending Speech Request . . . ")

		response = None
		token = self.get_token()
		if token == None : return None
		headers = { 'Authorization' : 'Bearer %s' % token}
		data = {
			"messageHeader" : {
				"deviceContext" : [{
					"name" : "playbackState",
					"namespace" : "AudioPlayer" ,
					"payload" : {
						"streamId" : "" ,
						"offsetInMilliseconds" : "0" , 
						"playerActivity" : "IDLE"
					}
				}]
			},
			"messageBody" : {
				"profile" : "alexa-close-talk",
				"locale" : "en-US",
				"format" : "audio/L16; rate=16000; channels=1"
			}
		}

		with open(recording_file) as recording :
			files = [
				('file' , ('request' , json.dumps(data), 'application/json; charset=UTF-8' )),
				('file' , ('audio' ,  recording , 'audio/L16; rate=16000; channels=1' )),
			]
			response = self.session.post( amazon_recog_url , headers = headers , files = files)

		if (response != None) : return self.process_response( response )
		else : 
			log("No response obtained from speech request")
			self.media_player.play(self.media_player.say_error)


	def process_response(self, response):
		log (" Processing Speech Response . . .  ")
		
		if (response.status_code == 200):
			data = "Content-Type:" + response.headers['content-type'] + "\r\n\r\n" + response.content
			msg = email.message_from_string(data)
			for payload in msg.get_payload():
				if payload.get_content_type() == "application/json":
					string = json.loads(payload.get_payload())
					log("JSON String returned {}".format( json.dumps(string) ))
				
				elif payload.get_content_type() == "audio/mpeg" : 
					with open(response_file , 'wb') as fp:
						fp.write(payload.get_payload())
				else:
					log("Wow , new content-type available : " + payload.get_content_type() )
					self.media_player.play(self.media_player.say_error)

			if 'directives' in string['messageBody']:
				if len( string['messageBody']['directives'])  == 0:
					log("0 directives received")
					self.media_player.play(self.media_player.say_error)
					return None

				for directive in string['messageBody']['directives']:
					####################################################################################################
					#		implement speech directives here
					####################################################################################################
					allowed_pairs = [("SpeechSynthesizer" , "speak") , ("AudioPlayer" , "play") ]
					if (directive['namespace'] , directive['name']) in allowed_pairs:
						print "speaking response"
						self.media_player.play(self.media_player.say_response)
					else:
						pass

		elif ( response.status_code == 204 ) : 
			log("Response is NULL (The universe prefers silence)")
			self.media_player.play(self.media_player.say_stop)
		else:
			log("Some Work is still left . Error Code : {} " .format(response.status_code))
			self.media_player.play(self.media_player.say_error)
