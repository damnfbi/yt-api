from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from api.mp4 import router as mp4_router
from api.mp3 import router as mp3_router
import os

app = FastAPI(
    title="YouTube Downloader API",
    description="High quality YouTube video and audio downloader",
    version="1.0.0"
)

app.include_router(mp4_router, prefix="/api")
app.include_router(mp3_router, prefix="/api")

@app.get("/")
async def root():
    return {
        "message": "YouTube Downloader API",
        "endpoints": {
            "mp4_download": "/api/mp4?url=YOUTUBE_URL",
            "mp4_info": "/api/mp4/info?url=YOUTUBE_URL",
            "mp3_download": "/api/mp3?url=YOUTUBE_URL",
            "mp3_info": "/api/mp3/info?url=YOUTUBE_URL"
        },
        "examples": {
            "mp4": "https://your-vercel-app.vercel.app/api/mp4?url=https://www.youtube.com/watch?v=VIDEO_ID",
            "mp3": "https://your-vercel-app.vercel.app/api/mp3?url=https://www.youtube.com/watch?v=VIDEO_ID"
        }
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "youtube-downloader"}

def handler(request, context):
    from mangum import Mangum
    mangum_handler = Mangum(app)
    return mangum_handler(request, context)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)