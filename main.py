import os
from datetime import datetime

from fastapi import FastAPI, Request, Depends, File, UploadFile
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles

from sqlalchemy.orm import Session
from PIL import Image

from models import Image as ImageModel
from database import SessionLocal, engine, Base

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount("/image", StaticFiles(directory="image"), name="image")
templates = Jinja2Templates(directory="templates")

Base.metadata.create_all(bind=engine)


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/", response_class=HTMLResponse)
def read_root(request: Request, db: Session = Depends(get_db)):
    image_count = db.query(ImageModel).count()

    return templates.TemplateResponse(
        "index.html", {"request": request, "image_count": image_count}
    )


@app.get("/{image_name}", response_class=HTMLResponse)
async def read_item(request: Request, image_name: str, db: Session = Depends(get_db)):
    image_name = image_name.lower()
    image = db.query(ImageModel).filter(ImageModel.name == image_name).first()

    if image:
        return templates.TemplateResponse(
            "image.html", {"request": request, "image": image}
        )

    return templates.TemplateResponse(
        "upload.html", {"request": request, "image_name": image_name}
    )


@app.post("/{image_name}", response_class=HTMLResponse)
async def upload_image(
    request: Request, file: UploadFile, image_name: str, db: Session = Depends(get_db)
):
    image_name = image_name.lower()
    if not file:
        return templates.TemplateResponse(
            "error.html", {"request": request, "error_message": "no file"}
        )

    ext = file.filename.split(".")[-1]

    if ext not in ("jpg", "jpeg", "png", "bmp", "gif", "tiff", "webp"):
        return templates.TemplateResponse(
            "error.html",
            {"request": request, "error_message": "unsupported image format"},
        )

    content = await file.read()
    temp_file = os.path.join("temp", file.filename)

    with open(
        temp_file,
        "wb",
    ) as fp:
        fp.write(content)  # 서버 로컬 스토리지에 이미지 저장 (쓰기)

    image_dir = os.path.join("image", datetime.now().strftime("%Y_%m"))

    if not os.path.exists(image_dir):
        os.makedirs(image_dir)

    image_file = os.path.join(image_dir, image_name + ".png")
    thumbnail_file = os.path.join(image_dir, image_name + "_th.png")

    image = Image.open(temp_file)
    image.thumbnail((1024, 1024))
    image.save(image_file)
    image.thumbnail((512, 512))
    image.save(thumbnail_file)

    newImage = ImageModel(name=image_name, url=image_file, thumbnail_url=thumbnail_file)
    db.add(newImage)
    db.commit()

    os.remove(temp_file)

    return templates.TemplateResponse(
        "image.html", {"request": request, "image": newImage}
    )
