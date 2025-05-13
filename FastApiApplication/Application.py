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
        self.running_processes: list[LetterProcess] = []

        self.text_analizer = TextGenerator()



    async def add_new_letter(self, data=Body()) -> JSONResponse:
        current_process = LetterProcess(data['letter'], 0, self.text_analizer)
        self.running_processes.append(current_process)
        await current_process.start_text_scenes_generation()
        return JSONResponse({
            "status_code": 0,
            "user_id": 0,
            "text_generation_result": current_process.text_gen_result
        })

    def setup_routing(self):
        self.app.add_api_route(
            f"/api/init_generation",
            methods=["POST"],
            endpoint=self.add_new_letter,
            response_class=JSONResponse,
            name=f"get_main"
        )


if __name__ == "__main__":
    app = Application()
    uvicorn.run(
        app.app,  # передаём сюда свойство app
        host="0.0.0.0",
        port=8001,
        reload=False,
        access_log=True,
    )
