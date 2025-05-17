import asyncio

import uvicorn
from fastapi import FastAPI, Body
from starlette.requests import Request
from starlette.responses import FileResponse, HTMLResponse, PlainTextResponse, JSONResponse
from starlette.templating import Jinja2Templates

from FastApiApplication.LetterProcess import LetterProcess
from TextGenerator.TextGenerator import TextGenerator


class Application:
    def __init__(self):
        self.app = FastAPI()
        self.setup_routing()
        self.running_processes: dict[int, LetterProcess] = {}
        self.text_analizer = TextGenerator()


    async def add_new_letter(self, data=Body()) -> JSONResponse:
        # body format: {“letter”: “Текст введённого пользователем письма”}
        if self.running_processes.keys():
            user_id = max(self.running_processes.keys()) + 1
        else:
            user_id = 0
        current_process = LetterProcess(data['letter'], user_id, self.text_analizer)
        self.running_processes[user_id] = current_process
        await current_process.start_text_scenes_generation()

        return JSONResponse({
            "status_code": 0,
            "user_id": user_id,
            "text_generation_result": current_process.text_gen_result
        })

    async def init_img_generation(self, data=Body()) -> JSONResponse:
        # body format: {"user_id": 0}
        if "user_id" not in data:
            return JSONResponse(
                {"status_code": -1,
                 "message": "wrong body"}
            )
        if data["user_id"] not in self.running_processes:
            return JSONResponse({
                JSONResponse(
                    {"status_code": -2,
                     "message": "generation prcess not finded"}
                )
            })

        user_id = data["user_id"]
        await self.running_processes[user_id].start_image_generation()
        return JSONResponse({
            "status_code": 0
        })

    async def get_images(self, data=Body()) -> JSONResponse:
        user_id = data["user_id"]
        images = await self.running_processes[user_id].get_images_base_64()
        if images:
            return JSONResponse({
                "status": 0,
                "images": images
            })
        else:
            return JSONResponse({
                "status": 1,
                "message": "images in generation process"
            })


    def setup_routing(self):
        self.app.add_api_route(
            f"/api/init_text_generation",
            methods=["POST"],
            endpoint=self.add_new_letter,
            response_class=JSONResponse,
            name=f"get_main"
        )

        self.app.add_api_route(
            f"/api/init_img_generation",
            methods=["POST"],
            endpoint=self.init_img_generation,
            response_class=JSONResponse,
            name=f"start_img_gen"
        )
        self.app.add_api_route(
            f"/api/get_images",
            methods=["GET"],
            endpoint=self.get_images,
            response_class=JSONResponse,
            name=f"start_img_gen"
        )



