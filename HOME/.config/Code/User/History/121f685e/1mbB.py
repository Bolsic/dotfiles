import os
import time
import threading
import queue
import azure.cognitiveservices.speech as speechsdk
from azure.core.credentials import AzureKeyCredential
from azure.ai.translation.text import TextTranslationClient

speech_key = os.environ.get('SPEECH_KEY')
service_region = os.environ.get('SPEECH_REGION')

print("Speech key: " + speech_key)
print("Service region: " + service_region)
