from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from starlette.background import BackgroundTask
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

@app.post("/info")
async def get_info(data: dict):
    url = data.get("url")
    ydl_opts = {"quiet": True, "skip_download": True}
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
        return JSONResponse({
            "title": info.get("title", "Video"),
            "thumbnail": info.get("thumbnail", ""),
            "duration": info.get("duration", 0),
        })

@app.post("/download")
async def download_video(data: dict):
    url = data.get("url")
    formato = data.get("formato", "mp4")
    file_id = str(uuid.uuid4())

    if formato == "mp3":
        outtmpl = os.path.join(DOWNLOAD_FOLDER, f"{file_id}.%(ext)s")
        ydl_opts = {
            "outtmpl": outtmpl,
            "format": "bestaudio/best",
            "postprocessors": [{
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "320",
            }],
        }
        ext = "mp3"
    else:
        outtmpl = os.path.join(DOWNLOAD_FOLDER, f"{file_id}.%(ext)s")
        ydl_opts = {
            "outtmpl": outtmpl,
            "format": "bestvideo[ext=mp4]+bestaudio[ext=m4a]/bestvideo+bestaudio/best",
            "merge_output_format": "mp4",
        }
        ext = "mp4"

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

    files = glob.glob(os.path.join(DOWNLOAD_FOLDER, f"{file_id}.*"))
    filepath = files[0]
    filename = f"video.{ext}"

    background = BackgroundTask(os.remove, filepath)
    return FileResponse(filepath, filename=filename, background=background)

@app.get("/")
def root():
    return FileResponse("index.html")