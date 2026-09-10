from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import subprocess
import os
import uuid

app = FastAPI()

# Frontend को अनुमति (CORS)
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
    yt_url = req.url
    if not yt_url:
        raise HTTPException(status_code=400, detail="URL Missing")

    job_id = str(uuid.uuid4())[:8]
    input_file = f"temp_{job_id}.mp4"
    output_file = f"short_{job_id}.mp4"

    try:
        # 1. YouTube वीडियो डाउनलोड
        download_cmd = [
            "yt-dlp",
            "-f", "bestvideo[height<=720]+bestaudio/best[height<=720]",
            "-o", input_file,
            yt_url
        ]
        subprocess.run(download_cmd, check=True)

        # 2. FFmpeg से 9:16 Shorts कट (30 सेकंड)
        crop_filter = "crop=ih*(9/16):ih,scale=1080:1920"
        ffmpeg_cmd = [
            "ffmpeg", "-y",
            "-ss", "00:00:10",
            "-t", "00:00:30",
            "-i", input_file,
            "-vf", crop_filter,
            "-c:v", "libx264",
            "-c:a", "aac",
            output_file
        ]
        subprocess.run(ffmpeg_cmd, check=True)

        # टेम्परेरी फ़ाइल साफ़ करना
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
      
