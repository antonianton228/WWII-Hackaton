import requests
from speechkit import Session, SpeechSynthesis
import os
import logging
from dotenv import load_dotenv

load_dotenv()
logging.basicConfig(encoding='utf-8', level=logging.DEBUG)

class SpeechGenerator:
    def __init__(self, speech_text: str, sex: int):
        self.speech_text = speech_text
        self.speaker_voice = "jane" if sex == 0 else "ermil"
        self.logger = logging.getLogger("SpeechGenerationMain")
        self.oauth_session = Session.from_yandex_passport_oauth_token(os.getenv("YANDEX_OATH_TOKEN"),
                                                                      os.getenv("YANDEX_CATALOG_ID"))
        if os.getenv("YANDEX_OATH_TOKEN") is None or os.getenv("YANDEX_CATALOG_ID") is None:
            self.logger.warning("check .env file setup")
        self.synthesizeAudio = SpeechSynthesis(self.oauth_session)
        self.logger.info("End of setupping Speech gen")

    def generate_voice(self) -> bytes:
        audio_data = self.synthesizeAudio.synthesize_stream(
            text=self.speech_text,
            voice=self.speaker_voice, format='oggopus', sampleRateHertz='16000'
        )
        return audio_data


if __name__ == "__main__":
    test = SpeechGenerator('''Очень благодарна своему бывшему мужу. Он всегда жил свою жизнь. Это не про не уважении ко мне. Это о том, что он всегда шёл своим путем 
Я же предпочитал плыть по течению. Рядом с таким мужчиной как бывший муж это очень сладко делать. 
А потом он ушёл к другой. И.. Я не стала жалеть себя и оскорблять его перед подружками.''', sex=1)
    test.generate_voice()
