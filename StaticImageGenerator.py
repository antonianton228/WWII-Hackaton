import time

from PIL import Image
import logging
import asyncio


class StaticImageGenerator:
    def __init__(self):
        self.__prompt_strings: list[str] = []
        self.__ready_images: list[Image] = []

        self.logger = logging.getLogger(__name__)  # Логгер
        logging.basicConfig(encoding='utf-8', level=logging.DEBUG)  # логгер

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

    async def generate_one_img(self, prompt_id: int) -> bool:
        self.logger.warning(f"Start async generate task with prompt {self.__prompt_strings[prompt_id]}")
        
        return True

    async def run_generations(self):
        coroutines: list[asyncio.coroutine] = []
        for prompt in range(self.get_prompt_count()):
            coroutines.append(self.generate_one_img(prompt))
        await asyncio.gather(*coroutines)

    def start_image_generations(self):
        asyncio.run(self.run_generations())
        self.logger.warning("End of generation")



if __name__ == "__main__":
    generator = StaticImageGenerator()
    generator.add_prompt("aaaaa")
    generator.add_prompt("vvv")
    generator.add_prompt("2222")
    generator.edit_prompt(0, "bbbb")
    generator.edit_prompt(1, "bbbb")
    generator.start_image_generations()
