from typing import Union

from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


@app.get("/", response_class=HTMLResponse)
def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/upload")
def read_root():
    return {"Hello": "World"}


@app.get("/{image_name}", response_class=HTMLResponse)
async def read_item(request: Request, image_name: str):
    return templates.TemplateResponse(
        "image.html", {"request": request, "image_name": image_name}
    )
