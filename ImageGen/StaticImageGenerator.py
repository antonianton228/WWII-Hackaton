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
        result.show()
        return True

    async def __run_generations(self):
        coroutines: list[asyncio.coroutine] = []
        for prompt in range(self.get_prompt_count()):
            coroutines.append(self.__generate_one_img(prompt))
        await asyncio.gather(*coroutines)

    def start_image_generations(self):
        asyncio.run(self.__run_generations())
        self.logger.info("End of generation")



if __name__ == "__main__":
    start_time = time.time()
    generator = StaticImageGenerator()
    generator.add_prompt("Молодой солдат в темной землянке при свете коптилки пишет письмо домой. На его лице смесь решимости и тоски, в глазах отблеск пламени. На столе лежит партбилет ВКП(Б), винтовка прислонена к бревенчатой стене. За окном зимняя ночь, видны вспышки далекого боя. Стиль: драматичная военная живопись, темные тона с контрастом огня и теней")
    generator.add_prompt("Видение солдата: его мать, бабушка, Нина, Юра и Ольга стоят в солнечной комнате довоенного дома. Они улыбаются, но их образы полупрозрачны, как мираж. На переднем плане — сам боец в каске, его лицо в тени, а вокруг него уже не дом, а снежное поле с разрывами снарядов. Стиль: сюрреалистичное смешение прошлого и настоящего, теплые и холодные цвета в контрасте.")
    generator.add_prompt("Рассвет над окопами, алый свет зари окрашивает снег. Солдат сжимает винтовку, на его шинели — значок ВКП(Б). Рядом товарищи готовятся к атаке, лица напряжены. Вдали дым и огонь боя. На лице главного героя — последняя мысль о доме перед рывком. Стиль: динамичная батальная сцена в духе советского военного плаката, резкие тени, кроваво-красное небо.")
    generator.add_prompt('Крупный план рук солдата, крепко сжимающих карандаш и листок с недописанными словами. Второй лист уже вложен в конверт с надписью «Моей семье». На заднем плане — звук сирены, бойцы поднимаются в атаку. В глазах солдата — слеза, но губы сжаты в решимости. Стиль: эмоциональный гиперреализм, акцент на деталях: дрожь руки, помятая бумага, тусклый свет утра.')
    generator.add_prompt('Альтернативная реальность (метафора жертвы)')
    generator.start_image_generations()
    print(f"time = {time.time() - start_time}")
