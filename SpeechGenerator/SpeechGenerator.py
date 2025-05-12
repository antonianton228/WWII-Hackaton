import requests

class SpeechGenerator:
    def __init__(self, speech_text: str):
        self.speech_text = speech_text

        self.url = 'https://tts.api.cloud.yandex.net'

        self.request_body = {
            'model': "",
            'text': self.speech_text,
            'text_template': "",
            'hints': [],
            'output_audio_spec': {
                "raw_audio": {
                    "audio_encoding": "AUDIO_ENCODING_UNSPECIFIED",
                    "sample_rate_hertz": 48000
                },
                "container_audio": {
                    "container_audio_type": "MP3"
                }
            },
            "unsafe_mode": True
        }

    def test(self):
        res = requests.get(self.url, data=self.request_body).text
        print(res)


if __name__ == "__main__":
    test = SpeechGenerator("ABCD")
    test.test()