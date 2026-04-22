from fastapi import FastAPI
from starlette.background import BackgroundTask
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
import yt_dlp
import os
import uuid
import glob

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

DOWNLOAD_FOLDER = "downloads"
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

@app.post("/download")
async def download_video(data: dict):
    url = data.get("url")
    file_id = str(uuid.uuid4())
    outtmpl = os.path.join(DOWNLOAD_FOLDER, f"{file_id}.%(ext)s")

    ydl_opts = {
        "outtmpl": outtmpl,
        "format": "bestvideo[ext=mp4]+bestaudio[ext=m4a]/bestvideo+bestaudio/best",
        "merge_output_format": "mp4",
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

    files = glob.glob(os.path.join(DOWNLOAD_FOLDER, f"{file_id}.*"))
    filepath = files[0]

    background = BackgroundTask(os.remove, filepath)
    response = FileResponse(filepath, filename="video.mp4", background=background)
    return response

@app.get("/")
def root():
    return FileResponse("index.html")
    