from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import Response
import yt_dlp
from .utils import validate_youtube_url, get_video_info, sanitize_filename

router = APIRouter()

@router.get("/mp4")
async def download_mp4(url: str = Query(..., description="YouTube video URL")):
    if not validate_youtube_url(url):
        raise HTTPException(status_code=400, detail="Invalid YouTube URL")
    
    try:
        video_info = get_video_info(url)
        if not video_info:
            raise HTTPException(status_code=400, detail="Could not fetch video information")
        
        ydl_opts = {
            'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
            'outtmpl': '%(title)s.%(ext)s',
            'quiet': True,
            'no_warnings': True,
            'merge_output_format': 'mp4',
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
            
            with open(filename, 'rb') as video_file:
                video_content = video_file.read()
            
            import os
            os.remove(filename)
            
            safe_filename = sanitize_filename(info['title']) + '.mp4'
            
            return Response(
                content=video_content,
                media_type='video/mp4',
                headers={
                    'Content-Disposition': f'attachment; filename="{safe_filename}"',
                    'Content-Length': str(len(video_content)),
                    'X-Video-Title': safe_filename,
                    'X-Video-Duration': str(info.get('duration', 0)),
                }
            )
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Download failed: {str(e)}")

@router.get("/mp4/info")
async def get_mp4_info(url: str = Query(..., description="YouTube video URL")):
    if not validate_youtube_url(url):
        raise HTTPException(status_code=400, detail="Invalid YouTube URL")
    
    video_info = get_video_info(url)
    if not video_info:
        raise HTTPException(status_code=400, detail="Could not fetch video information")
    
    return {
        "status": "success",
        "data": video_info,
        "download_url": f"/mp4?url={url}"
    }