from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.background import BackgroundTasks
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

def cleanup_files(*files):
    for f in files:
        if os.path.exists(f):
            try:
                os.remove(f)
            except Exception:
                pass

@app.get("/")
def home():
    return {"status": "QuickViral Upload Engine Ready 🚀"}

@app.post("/upload-cut")
async def upload_cut(background_tasks: BackgroundTasks, file: UploadFile = File(...)):
    job_id = str(uuid.uuid4())[:8]
    input_file = f"input_{job_id}.mp4"
    output_file = f"short_{job_id}.mp4"

    try:
        # यूजर द्वारा भेजी गई वीडियो फाइल को सर्वर पर सेव करना
        with open(input_file, "wb") as f:
            content = await file.read()
            f.write(content)

        # FFmpeg से 9:16 Shorts (Vertical) में क्रॉप और 15-20 सेकंड कट
        # ih*(9/16):ih सेंटर से 9:16 आस्पेक्ट रेशियो में क्रॉप करता है
        crop_filter = "crop=ih*(9/16):ih,scale=720:1280"
        ffmpeg_cmd = [
            "ffmpeg", "-y",
            "-ss", "00:00:00",
            "-t", "00:00:15",
            "-i", input_file,
            "-vf", crop_filter,
            "-c:v", "libx264",
            "-preset", "ultrafast",
            "-c:a", "aac",
            output_file
        ]

        res = subprocess.run(ffmpeg_cmd, capture_output=True, text=True)
        if res.returncode != 0:
            raise Exception(f"FFmpeg Error: {res.stderr[:200]}")

        # डाउनलोड पूरा होने के बाद सर्वर से फाइल डिलीट कर दी जाएगी
        background_tasks.add_task(cleanup_files, input_file, output_file)

        return FileResponse(
            path=output_file,
            filename=f"QuickViral_{job_id}.mp4",
            media_type="video/mp4"
        )

    except Exception as e:
        cleanup_files(input_file, output_file)
        raise HTTPException(status_code=500, detail=str(e))
        
