import os
import time

DEBUG = True

RESOURCES_DIR = os.path.join(os.path.abspath(os.curdir) , "resources" )
recording_file = os.path.join (RESOURCES_DIR , "recording.wav")
response_file = os.path.join(RESOURCES_DIR , "response.wav")

def log(x) : print x