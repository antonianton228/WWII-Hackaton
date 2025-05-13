import logging

from FastApiApplication.ProcessStatuses import ProcessStatuses
from ImageGen.StaticImageGenerator import StaticImageGenerator
from SpeechGenerator.SpeechGenerator import SpeechGenerator
from TextGenerator.TextGenerator import TextGenerator


class LetterProcess:
    def __init__(self, letter_text: str, user_id: int, text_gen: TextGenerator):
        self.logger = logging.getLogger(__name__)
        self.letter_text = letter_text
        self.user_id = user_id
        self.logger.info(f"Process for user {user_id} inited")
        self.status: ProcessStatuses = ProcessStatuses.LETTER_LOADED


        self.text_gen: TextGenerator = text_gen
        self.text_gen_result: dict = {}
        self.img_gen: StaticImageGenerator = None
        self.anim_gen = None
        self.speech_gen: SpeechGenerator = None

    async def start_text_scenes_generation(self) -> None:
        self.text_gen_result = await self.text_gen.analyze_letter(self.letter_text)
        print(self.text_gen_result)
        self.status = ProcessStatuses.LETTER_READY_FOR_IMAGE_GENERATING
