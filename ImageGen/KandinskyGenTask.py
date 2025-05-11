import base64
import io
import json
import logging
import os

from PIL import Image
import aiohttp
import asyncio

from dotenv import load_dotenv

load_dotenv()
logging.basicConfig(encoding='utf-8', level=logging.DEBUG)  # логгер

class KandinskyGenTask:
    def __init__(self, prompt: str):
        self.URL = "https://api-key.fusionbrain.ai/"

        self.logger = logging.getLogger(__name__)  # Логгер

        self.image_params = json.loads(open("CONFIGS/image_settings.json", encoding="utf-8").read())
        self.image_params["generateParams"]["query"] += prompt

        self.pipeline: str|None = None

        self.image_id = None

        self.AUTH_HEADERS = {
            'X-Key': f'Key {os.getenv("KANDINSKY_API")}',
            'X-Secret': f'Secret {os.getenv("KANDINSKY_SECRET")}',
        }
        if os.getenv("KANDINSKY_API") == None or os.getenv("KANDINSKY_SECRET") == None:
            self.logger.warning("Error while getting auth keys from .env file. check it")

        self.logger.info("Kandinsky task inited. Start pipeline getter")


    async def __set_pipeline(self) -> None:
        async with aiohttp.ClientSession() as session:
            async with session.get(self.URL + 'key/api/v1/pipelines', headers=self.AUTH_HEADERS) as response:
                self.pipeline = (await response.json())[0]['id']
                self.logger.info(f"Pipeline {self.pipeline} getted from API")

    async def __start_file_generation(self) -> None:
        request_data = aiohttp.FormData()
        request_data.add_field('pipeline_id', self.pipeline)
        request_data.add_field('params',
                       json.dumps(self.image_params),
                       content_type='application/json')

        self.logger.info("Image generation task started")
        async with aiohttp.ClientSession() as session:
            async with session.post(self.URL + 'key/api/v1/pipeline/run', headers=self.AUTH_HEADERS, data=request_data) as response:
                self.logger.info("Image generation task ended")
                self.image_id = (await response.json())['uuid']


    async def __get_result(self) -> Image or int: # Вернет None, если генерация не завершена
        if self.image_id is None:
            self.logger.warning("Start image generation first!!!")
            return 0
        self.logger.info("Status getting task started")
        async with aiohttp.ClientSession() as session:
            async with session.get(self.URL + 'key/api/v1/pipeline/status/' + self.image_id, headers=self.AUTH_HEADERS) as response:
                data = await response.json()
                if data['status'] == 'INITIAL' or data['status'] == 'PROCESSING':
                    self.logger.info(f"Current status of task is {data['status']}")
                    return 0
                elif data['status'] == 'DONE':
                    self.logger.info(f"File generated")
                    base_64_coded_file = data['result']['files'][0]
                    base_64_coded_file = base64.b64decode(base_64_coded_file)
                    buffer = io.BytesIO(base_64_coded_file)
                    img_pil = Image.open(buffer)
                    return img_pil

    async def generate_image(self) -> Image:
        self.logger.info(f"Start generate image")
        await self.__set_pipeline()
        await self.__start_file_generation()
        await self.__start_file_generation()
        result = await self.__get_result()
        while result == 0:
            result = await self.__get_result()
            await asyncio.sleep(2)
        return result


async def main():
    generation_task = KandinskyGenTask("реалистичный кадр, рассветные лучи освещают заснеженное поле, силуэт советского солдата уходит в туман навстречу бою, камера позади, на заднем плане едва различимы фигуры других бойцов, небо в розово‑серых оттенках, кадр наполнен тихой трагичностью и надеждой, без флагов")
    result = await generation_task.generate_image()
    result.show()



if __name__ == "__main__":
    asyncio.run(main())