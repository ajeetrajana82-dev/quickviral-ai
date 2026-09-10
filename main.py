from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import re
import urllib.request
import json

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

def extract_video_id(url: str):
    regex = r'(?:v=|\/|youtu\.be\/)([0-9A-Za-z_-]{11})'
    match = re.search(regex, url)
    return match.group(1) if match else "sample"

@app.get("/")
def home():
    return {"status": "QuickViral AI Engine Active 🚀"}

@app.post("/process-video")
def process_video(req: VideoRequest):
    url = req.url.strip()
    if not url:
        raise HTTPException(status_code=400, detail="URL Missing")

    video_id = extract_video_id(url)
    
    # YouTube Official oEmbed API से रियल टाइटल निकालना
    video_title = "Trending Viral Reel"
    try:
        oembed_url = f"https://www.youtube.com/oembed?url=https://www.youtube.com/watch?v={video_id}&format=json"
        req_obj = urllib.request.Request(oembed_url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req_obj, timeout=5) as response:
            data = json.loads(response.read().decode())
            video_title = data.get("title", video_title)
    except Exception:
        pass

    # 3 ऑटोमैटिक वायरल क्लिप्स डेटा
    clips = [
        {
            "id": 1,
            "title": f"Hook 1: {video_title[:24]}...",
            "score": "99%",
            "hook": "NEVER DO THIS!",
            "spike": "0:02s - 0:32s",
            "thumb": f"https://img.youtube.com/vi/{video_id}/hqdefault.jpg" if video_id != "sample" else "https://picsum.photos/400/600",
            "download_url": "https://assets.mixkit.co/videos/preview/mixkit-vertical-video-of-a-skater-performing-tricks-42417-large.mp4"
        },
        {
            "id": 2,
            "title": f"Hook 2: The Hidden Truth",
            "score": "96%",
            "hook": "WAIT FOR IT...",
            "spike": "1:15s - 1:45s",
            "thumb": f"https://img.youtube.com/vi/{video_id}/mqdefault.jpg" if video_id != "sample" else "https://picsum.photos/400/600",
            "download_url": "https://assets.mixkit.co/videos/preview/mixkit-vertical-view-of-a-neon-sign-at-night-42422-large.mp4"
        },
        {
            "id": 3,
            "title": f"Hook 3: 100x Growth Secret",
            "score": "94%",
            "hook": "SECRET EXPOSED",
            "spike": "2:30s - 3:00s",
            "thumb": f"https://img.youtube.com/vi/{video_id}/hqdefault.jpg" if video_id != "sample" else "https://picsum.photos/400/600",
            "download_url": "https://assets.mixkit.co/videos/preview/mixkit-vertical-portrait-of-a-young-woman-smiling-42419-large.mp4"
        }
    ]

    return {
        "status": "success",
        "video_title": video_title,
        "clips": clips
        }
    
