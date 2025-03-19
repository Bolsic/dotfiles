import azure.cognitiveservices.speech as speechsdk

speech_key = "8DWayvEHZerwdy1oXOhSMJRQJ2ic0boQIkoVo6BhVwbHMDGRnLiiJQQJ99BBAC5RqLJXJ3w3AAAYACOGKpnv"
service_region = "westeurope"
translator_key = "8uzkNOPtkQURJWrm2Zxih0R0NpHJ36rXNoVUG9226ZJ2Yx6pMcLSJQQJ99BBAC5RqLJXJ3w3AAAbACOGpome"
translator_region = "westeurope"
translator_endpoint = "https://api.cognitive.microsofttranslator.com"

def test_voice_synthesis():
    # Replace with your Azure Speech subscription key and service region.

    # Create a speech configuration and set synthesis parameters.
    speech_config = speechsdk.SpeechConfig(subscription=speech_key, region=service_region)
    speech_config.speech_synthesis_language = "en-US"
    # Use a known English neural voice (adjust as needed)
    speech_config.speech_synthesis_voice_name = "en-US-AriaNeural"

    # Create a synthesizer that uses the default speaker for audio output.
    synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config)

    text = "Hello, this is a test of the voice synthesis service."
    print("Synthesizing voice for text:")
    print(text)

    # Synthesize the text asynchronously and wait for the result.
    result = synthesizer.speak_text_async(text).get()

    # Check the result and print status.
    if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
        print("Synthesis completed successfully!")
    elif result.reason == speechsdk.ResultReason.Canceled:
        cancellation_details = result.cancellation_details
        print("Synthesis canceled: {}".format(cancellation_details.reason))
        if cancellation_details.reason == speechsdk.CancellationReason.Error:
            print("Error details: {}".format(cancellation_details.error_details))

if __name__ == "__main__":
    test_voice_synthesis()
