import base64
import io
import json
import time

import requests
from PIL import Image
import logging
import asyncio
import os
from dotenv import load_dotenv
import requests

from ImageGen.KandinskyGenTask import KandinskyGenTask

load_dotenv()
logging.basicConfig(encoding='utf-8', level=logging.DEBUG)  # логгер

class StaticImageGenerator:
    def __init__(self):
        self.__prompt_strings: list[str] = []
        self.__ready_images: list[Image] = []

        self.logger = logging.getLogger(__name__)  # Логгер

        self.logger.info("Static image generator inited")

    def get_prompt_count(self) -> int:
        return len(self.__prompt_strings)

    def add_prompt(self, new_prompt: str) -> None:
        self.__prompt_strings.append(new_prompt)
        self.logger.info(f"Prompt with index {self.get_prompt_count() - 1} added")

    def edit_prompt(self, prompt_id: int, new_prompt_text: str) -> bool:
        if self.get_prompt_count()  > prompt_id:
            self.__prompt_strings[prompt_id] = new_prompt_text
            self.logger.info(f"Prompt with index {prompt_id} edited")
            return True
        else:
            self.logger.warning(f"Can't edit prompt with index {prompt_id}. Max id is {self.get_prompt_count()  - 1}")
            return False

    async def __generate_one_img(self, prompt_id: int) -> bool:
        self.logger.info(f"Start async generate task with prompt {self.__prompt_strings[prompt_id]}")
        kandinsky_task = KandinskyGenTask(self.__prompt_strings[prompt_id])
        result = await kandinsky_task.generate_image()
        self.__ready_images.append(result)
        return True

    async def __run_generations(self):
        coroutines: list[asyncio.coroutine] = []
        for prompt in range(self.get_prompt_count()):
            coroutines.append(self.__generate_one_img(prompt))
        await asyncio.gather(*coroutines)

    def start_image_generations(self) -> list[Image]:
        asyncio.run(self.__run_generations())
        self.logger.info("End of generation")
        return self.__ready_images



if __name__ == "__main__":
    generator = StaticImageGenerator()
    generator.add_prompt('Письмо перед боем.')
    generator.add_prompt('Через полтора часа бой, неизвестно, вернется ли.')
    generator.add_prompt('Письмо может быть последним.')
    generator.add_prompt('Желание жить.')
    generator.add_prompt('Вступил в ряды ВКП(Б).')
    generator.add_prompt('Пойдет в бой коммунистом.')
    generator.add_prompt('Жить под ярмом немцев не хочет, лучше погибнуть.')
    generator.add_prompt('Прощание.')
    generator.add_prompt('24 января 1943 года.')
    result = generator.start_image_generations()
    for img in result:
        img.show()
