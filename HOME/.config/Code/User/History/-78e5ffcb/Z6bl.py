import os
import asyncio
import azure.cognitiveservices.speech as speechsdk
from azure.ai.translation.text import TextTranslationClient
from azure.core.credentials import AzureKeyCredential

# Set your Azure subscription keys and region
speech_key = "7fJr88MVZklBSl3vDoF7xkKxYtD9vrDYnXALYsoVbT6IG7b4F1NTJQQJ99BAAC5RqLJXJ3w3AAAYACOG0pi9"
service_region = "westeurope"
translator_key = "3iJ3P9yL1KJHkJKHFfQoq7zw2fr3PoH8LLYqd6y78bHSiNW4koxFJQQJ99BAAC5RqLJXJ3w3AAAbACOG807F"
translator_region = "westeurope"

def make_output_path(input_path):
    """
    Generates the output file path by appending '-Translated' to the input file name.
    """
    input_dir = os.path.dirname(input_path)
    input_file_name = os.path.basename(input_path)
    output_dir = input_dir.replace("Original-Audio", "Translated-Audio")
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, input_file_name.replace(".wav", "-Translated.wav"))
    return output_path

async def transcribe_audio(file_path):
    """
    Asynchronously transcribes audio from the given file path.
    Yields transcribed text and detected language as they become available.
    """
    if not speech_key or not service_region:
        raise ValueError("Azure Speech service key and region must be set.")

    auto_detect_source_language_config = speechsdk.languageconfig.AutoDetectSourceLanguageConfig(
        languages=["en-US", "sr-RS", "fr-FR", "it-IT"]
    )

    audio_config = speechsdk.audio.AudioConfig(filename=file_path)
    speech_config = speechsdk.SpeechConfig(subscription=speech_key, region=service_region)

    speech_recognizer = speechsdk.SpeechRecognizer(
        speech_config=speech_config,
        auto_detect_source_language_config=auto_detect_source_language_config,
        audio_config=audio_config
    )

    loop = asyncio.get_event_loop()
    transcriptions = asyncio.Queue()

    def recognized_callback(evt):
        if evt.result.reason == speechsdk.ResultReason.RecognizedSpeech:
            detected_language = evt.result.properties[
                speechsdk.PropertyId.SpeechServiceConnection_AutoDetectSourceLanguageResult
            ]
            loop.call_soon_threadsafe(transcriptions.put_nowait, (evt.result.text, detected_language))

    speech_recognizer.recognized.connect(recognized_callback)
    speech_recognizer.start_continuous_recognition()

    while True:
        transcription = await transcriptions.get()
        if transcription is None:
            break
        yield transcription

    speech_recognizer.stop_continuous_recognition()

async def translate_text(input_text, source_language, target_language):
    """
    Asynchronously translates the input text from the source language to the target language.
    """
    if not translator_key or not translator_region:
        raise ValueError("Azure Translator service key and region must be set.")

    credential = AzureKeyCredential(translator_key)
    text_translator = TextTranslationClient(credential=credential, region=translator_region)

    response = await text_translator.translate(
        content=[input_text],
        to=[target_language],
        source_language=source_language
    )

    if response and response[0].translations:
        translated_text = response[0].translations[0].text
        return translated_text
    else:
        raise Exception("Translation failed. No response received.")

async def synthesize_voice(input_text, language, output_path):
    """
    Asynchronously synthesizes speech from the input text in the specified language and saves it to the output path.
    """
    if not speech_key or not service_region:
        raise ValueError("Azure Speech service key and region must be set.")

    speech_config = speechsdk.SpeechConfig(subscription=speech_key, region=service_region)
    voice_map = {
        "en-US": "en-US-AriaNeural",
        "sr-RS": "sr-RS-NicholasNeural",
        "fr-FR": "fr-FR-DeniseNeural",
        "de-DE": "de-DE-KatjaNeural"
    }

    voice = voice_map.get(language)
    if not voice:
        raise ValueError("Invalid language. Please select a valid language.")

    speech_config.speech_synthesis_voice_name = voice
    audio_config = speechsdk.audio.AudioOutputConfig(filename=output_path)

    speech_synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config, audio_config=audio_config)
    result = await speech_synthesizer.speak_text_async(input_text)

    if result.reason == speechsdk.ResultReason.Canceled:
        cancellation_details = result.cancellation_details
        raise Exception(f"Speech Synthesis canceled: {cancellation_details.reason}")

async def process_pipeline(audio_file_path, output_path, target_language):
    """
    Orchestrates the transcription, translation, and synthesis pipeline.
    """
    async for transcription, detected_language in transcribe_audio(audio_file_path):
        translated_text = await translate_text(transcription, detected_language, target_language)
        await synthesize_voice(translated_text, target_language, output_path)

if __name__ == "__main__":
    audio_file_path = "/path/to/your/input.wav"
    output_path = make_output_path(audio_file_path)
    target_language = "fr-FR"  # Example target language

    asyncio.run(process_pipeline(audio_file_path, output_path, target_language))
