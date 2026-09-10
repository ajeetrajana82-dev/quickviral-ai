from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import subprocess
import os
import uuid

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class VideoRequest(BaseModel):
    url: str

@app.get("/")
def home():
    return {"status": "QuickViral AI Engine Active 🚀"}

@app.post("/process-video")
def process_video(req: VideoRequest):
    raw_url = req.url.strip()
    if not raw_url:
        raise HTTPException(status_code=400, detail="URL Missing")

    # URL से ट्रैकिंग पैरामीटर (?si=...) हटाना
    clean_url = raw_url.split("?")[0]

    job_id = str(uuid.uuid4())[:8]
    input_file = f"temp_{job_id}.mp4"
    output_file = f"short_{job_id}.mp4"

    try:
        # YouTube से सिंगल 720p/360p स्ट्रीम डाउनलोड करना
        download_cmd = [
            "yt-dlp",
            "--no-check-certificates",
            "--user-agent", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "-f", "b[ext=mp4]/best[ext=mp4]/best",
            "-o", input_file,
            clean_url
        ]
        res = subprocess.run(download_cmd, capture_output=True, text=True)
        if res.returncode != 0:
            raise Exception(f"Download Failed: {res.stderr[:200]}")

        # FFmpeg से 9:16 Shorts कट (30 सेकंड)
        crop_filter = "crop=ih*(9/16):ih,scale=720:1280"
        ffmpeg_cmd = [
            "ffmpeg", "-y",
            "-ss", "00:00:05",
            "-t", "00:00:25",
            "-i", input_file,
            "-vf", crop_filter,
            "-c:v", "libx264",
            "-c:a", "aac",
            output_file
        ]
        sub_res = subprocess.run(ffmpeg_cmd, capture_output=True, text=True)
        if sub_res.returncode != 0:
            raise Exception(f"Crop Failed: {sub_res.stderr[:200]}")

        if os.path.exists(input_file):
            os.remove(input_file)

        return {
            "status": "success",
            "message": "Clip generated successfully!",
            "clip_url": output_file
        }

    except Exception as e:
        if os.path.exists(input_file):
            os.remove(input_file)
        return {"status": "error", "message": str(e)}
