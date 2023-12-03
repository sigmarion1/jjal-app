import os

from fastapi import FastAPI, Request, Depends, File, UploadFile
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session

from models import Image
from database import SessionLocal, engine, Base

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")
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
def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/upload/{image_name}")
async def upload_image(
    file: UploadFile, image_name: str, db: Session = Depends(get_db)
):
    if not file:
        return {"message": "no file"}

    content = await file.read()

    with open(
        os.path.join("temp", file.filename),
        "wb",
    ) as fp:
        fp.write(content)  # 서버 로컬 스토리지에 이미지 저장 (쓰기)

    return {"filename": file.filename}

    UPLOAD_DIR = "./photo"  # 이미지를 저장할 서버 경로

    content = await File.read()
    filename = f"{str(uuid.uuid4())}.jpg"  # uuid로 유니크한 파일명으로 변경
    with open(os.path.join(UPLOAD_DIR, filename), "wb") as fp:
        fp.write(content)  # 서버 로컬 스토리지에 이미지 저장 (쓰기)

    return {"filename": filename}

    newImage = Image(name="newImage" + image_name)
    db.add(newImage)
    db.commit()
    print(db.query(Image).first())

    return {"Hello": "World"}


@app.get("/{image_name}", response_class=HTMLResponse)
async def read_item(request: Request, image_name: str, db: Session = Depends(get_db)):
    image = db.query(Image).filter(Image.name == image_name).first()

    if image:
        return templates.TemplateResponse(
            "image.html", {"request": request, "image_name": image_name}
        )

    return templates.TemplateResponse(
        "upload.html", {"request": request, "image_name": image_name}
    )
