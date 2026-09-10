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

    clean_url = raw_url.split("?")[0]
    job_id = str(uuid.uuid4())[:8]
    input_file = f"temp_{job_id}.mp4"
    output_file = f"short_{job_id}.mp4"

    try:
        # Android client मोड (YouTube 429 ब्लॉक से बचने के लिए)
        download_cmd = [
            "yt-dlp",
            "--extractor-args", "youtube:player_client=android",
            "-f", "best[ext=mp4]/best",
            "-o", input_file,
            clean_url
        ]
        res = subprocess.run(download_cmd, capture_output=True, text=True)
        if res.returncode != 0:
            raise Exception(f"Download Error: {res.stderr[:200]}")

        # FFmpeg से 9:16 Shorts में क्रॉप और कट
        crop_filter = "crop=ih*(9/16):ih,scale=720:1280"
        ffmpeg_cmd = [
            "ffmpeg", "-y",
            "-ss", "00:00:05",
            "-t", "00:00:20",
            "-i", input_file,
            "-vf", crop_filter,
            "-c:v", "libx264",
            "-c:a", "aac",
            output_file
        ]
        sub_res = subprocess.run(ffmpeg_cmd, capture_output=True, text=True)
        if sub_res.returncode != 0:
            raise Exception(f"Crop Error: {sub_res.stderr[:200]}")

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
        
