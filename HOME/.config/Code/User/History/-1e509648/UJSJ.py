import os
import time
import threading
import queue
import azure.cognitiveservices.speech as speechsdk
from azure.core.credentials import AzureKeyCredential
from azure.ai.translation.text import TextTranslationClient

import wave
import io
import simpleaudio as sa


def voice_synth(text_queue, speech_key, speech_region, voice_name=None, done_event=None):
    # Create a speech config with specified subscription key and service region.
    speech_config = speechsdk.SpeechConfig(subscription=speech_key, region=speech_region)
    if voice_name:
        speech_config.speech_synthesis_voice_name = voice_name

    # Create a synthesizer that returns audio data in memory.
    synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config, audio_config=None)
    
    while True:
        if done_event.is_set() and text_queue.empty():
            break
        
        try:
            # Wait for a text segment from the queue (with timeout to allow stop_event check).
            text = text_queue.get(timeout=0.5)
        except queue.Empty:
            continue

        print(f"[Synthesizing text]: {text}")
        result = synthesizer.speak_text_async(text).get()
        if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
            print("[Synthesis completed, playing audio]...")
            audio_bytes = result.audio_data
            try:
                # Play the synthesized audio (expected to be in WAV format) using simpleaudio.
                with wave.open(io.BytesIO(audio_bytes), 'rb') as wav_file:
                    wave_obj = sa.WaveObject.from_wave_read(wav_file)
                    play_obj = wave_obj.play()
                    play_obj.wait_done()  # Wait until playback finishes.
            except Exception as e:
                print("[Error during audio playback]:", e)
        else:
            print(f"[Synthesis failed] for '{text}'. Reason: {result.reason}")
        text_queue.task_done()
