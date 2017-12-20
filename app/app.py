from flask import Flask, render_template

import io
import os

from google.cloud import speech
from google.cloud.speech import enums
from google.cloud.speech import types

application = Flask(__name__)

def get_text_from_google():
    client = speech.SpeechClient()
    file_name = os.path.join(
        os.path.dirname(__file__),
        'resources',
        'audio.raw')

    # Loads the audio into memory
    with io.open(file_name, 'rb') as audio_file:
        content = audio_file.read()
        audio = types.RecognitionAudio(content=content)

    config = types.RecognitionConfig(
        encoding=enums.RecognitionConfig.AudioEncoding.LINEAR16,
        sample_rate_hertz=16000,
        language_code='en-US')

    response = client.recognize(config, audio)

    for result in response.results:
        print('Transcript: {}'.format(result.alternatives[0].transcript))


@application.route("/speechtext", methods=['POST'])
def get_text_from_api():
    pass


@application.route("/")
def hello():
    return render_template('index.html')
