from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import Response
import yt_dlp
from .utils import validate_youtube_url, get_video_info, sanitize_filename

router = APIRouter()

@router.get("/mp3")
async def download_mp3(url: str = Query(..., description="YouTube video URL")):
    if not validate_youtube_url(url):
        raise HTTPException(status_code=400, detail="Invalid YouTube URL")
    
    try:
        video_info = get_video_info(url)
        if not video_info:
            raise HTTPException(status_code=400, detail="Could not fetch video information")
        
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': '%(title)s.%(ext)s',
            'quiet': True,
            'no_warnings': True,
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '320',  
            }],
            'postprocessor_args': [
                '-ar', '44100',           
                '-ac', '2',               
                '-b:a', '320k',           
            ],
            'prefer_ffmpeg': True,
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            
            base_filename = ydl.prepare_filename(info)
            mp3_filename = base_filename.rsplit('.', 1)[0] + '.mp3'
            
            with open(mp3_filename, 'rb') as audio_file:
                audio_content = audio_file.read()
            
            import os
            if os.path.exists(mp3_filename):
                os.remove(mp3_filename)
            if os.path.exists(base_filename):
                os.remove(base_filename)
            
            safe_filename = sanitize_filename(info['title']) + '.mp3'
            
            return Response(
                content=audio_content,
                media_type='audio/mpeg',
                headers={
                    'Content-Disposition': f'attachment; filename="{safe_filename}"',
                    'Content-Length': str(len(audio_content)),
                    'X-Audio-Title': safe_filename,
                    'X-Audio-Duration': str(info.get('duration', 0)),
                    'X-Audio-Bitrate': '320k',
                }
            )
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Download failed: {str(e)}")

@router.get("/mp3/info")
async def get_mp3_info(url: str = Query(..., description="YouTube video URL")):
    if not validate_youtube_url(url):
        raise HTTPException(status_code=400, detail="Invalid YouTube URL")
    
    video_info = get_video_info(url)
    if not video_info:
        raise HTTPException(status_code=400, detail="Could not fetch video information")
    
    return {
        "status": "success",
        "data": video_info,
        "download_url": f"/mp3?url={url}"
    }