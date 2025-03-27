import io
import os
import requests
from enum import Enum
from typing import Optional
from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

API_URL = "https://api.upliftai.org/v1/synthesis/text-to-speech"
STREAM_API_URL = "https://api.upliftai.org/v1/synthesis/text-to-speech/stream"
API_KEY = os.getenv("UPLIFT_AI_API_KEY")

class VoiceID(str, Enum):
    gen_z = "v_kwmp7zxt"
    dada_jee = "v_yypgzenx"
    nostalgic_news = "v_30s70t3a"

class OutputFormat(str, Enum):
    WAV_22050_16 = "WAV_22050_16"
    WAV_22050_32 = "WAV_22050_32"
    MP3_22050_32 = "MP3_22050_32"
    MP3_22050_64 = "MP3_22050_64"
    MP3_22050_128 = "MP3_22050_128"
    OGG_22050_16 = "OGG_22050_16"
    ULAW_8000_8 = "ULAW_8000_8"

class TTSRequest(BaseModel):
    text: str = Field(
        default="سلام، آپ اِس وقت اوریٹر کی آواز سن رہے ہیں۔",
        max_length=2500
    )
    voice_id: VoiceID = VoiceID.nostalgic_news
    output_format: OutputFormat = OutputFormat.MP3_22050_128

def get_media_type(output_format: OutputFormat) -> str:
    """Map output format to appropriate media type"""
    format_map = {
        "WAV": "audio/wav",
        "MP3": "audio/mpeg",
        "OGG": "audio/ogg",
        "ULAW": "audio/basic"
    }
    return format_map[output_format.value.split("_")[0]]

@app.post("/tts")
async def text_to_speech(request: TTSRequest):
    payload = {
        "voiceId": request.voice_id.value,
        "text": request.text,
        "outputFormat": request.output_format.value
    }
    
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    try:
        response = requests.post(API_URL, json=payload, headers=headers)
        response.raise_for_status()
    except requests.exceptions.HTTPError as err:
        raise HTTPException(status_code=err.response.status_code, detail=err.response.text)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"API request failed: {str(exc)}")

    return StreamingResponse(
        content=io.BytesIO(response.content),
        media_type=get_media_type(request.output_format),
        headers={"X-Audio-Duration": response.headers.get("x-uplift-ai-audio-duration", "unknown")}
    )

@app.post("/tts-stream")
async def stream_tts(request: TTSRequest):
    payload = {
        "voiceId": request.voice_id.value,
        "text": request.text,
        "outputFormat": request.output_format.value
    }
    
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    try:
        uplink_response = requests.post(
            STREAM_API_URL,
            json=payload,
            headers=headers,
            stream=True
        )
        uplink_response.raise_for_status()
    except requests.exceptions.HTTPError as err:
        raise HTTPException(status_code=err.response.status_code, detail=err.response.text)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Uplift API error: {str(exc)}")

    return StreamingResponse(
        content=uplink_response.iter_content(chunk_size=1024),
        media_type=get_media_type(request.output_format),
        headers={
            "Transfer-Encoding": "chunked",
            "X-Audio-Format": request.output_format.value
        }
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)