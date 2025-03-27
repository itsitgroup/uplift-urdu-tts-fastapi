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
    allow_origins=["*"],  # Allows all origins (for development only)
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods (including OPTIONS)
    allow_headers=["*"],  # Allows all headers
)

# Uplift AI Orator API endpoint and credentials
API_URL = "https://api.upliftai.org/v1/synthesis/text-to-speech"
STREAM_API_URL = "https://api.upliftai.org/v1/synthesis/text-to-speech/stream"

API_KEY = os.getenv("UPLIFT_AI_API_KEY")
VOICE_ID = "v_30s70t3a"  # recommended for realistic sound in rural Punjab accent
OUTPUT_FORMAT = "MP3_22050_128"

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
    text: Optional[str] = Field(..., max_length=2500)
    voice_id: Optional[VoiceID] = VoiceID.dada_jee
    output_format: Optional[OutputFormat] = OutputFormat.MP3_22050_128

@app.post("/tts")
def text_to_speech(request: TTSRequest):
    """
    Call Uplift AI's Orator TTS API with the given text and return the audio.
    Accepts request as JSON body.
    """
    payload = {
        "voiceId": request.voice_id,
        "text": request.text,
        "outputFormat": request.output_format
    }
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    try:
        response = requests.post(API_URL, json=payload, headers=headers)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Error during API request: {exc}")

    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail=response.text)

    # Optionally, get the audio duration from response headers if needed
    audio_duration = response.headers.get("x-uplift-ai-audio-duration", "unknown")
    print(f"Audio duration: {audio_duration}ms")

    # Return the binary audio content as a streaming response
    return StreamingResponse(io.BytesIO(response.content), media_type="audio/mpeg")

@app.post("/tts-stream")
async def stream_tts(request: TTSRequest):
    """
    Stream Uplift AI's TTS response with configurable voice and format options.
    
    Parameters:
    - text: The text to synthesize (max 2500 characters)
    - voice_id: Voice identifier (default: v_30s70t3a)
        Available options: 
        v_kwmp7zxt (Gen Z), 
        v_yypgzenx (Dada Jee), 
        v_30s70t3a (Nostalgic News)
    - output_format: Audio format (default: MP3_22050_128)
        Available options:
        WAV_22050_16, 
        WAV_22050_32, 
        MP3_22050_32, 
        MP3_22050_64, 
        MP3_22050_128, 
        OGG_22050_16, 
        ULAW_8000_8
    Returns:
    - Streaming audio response with Transfer-Encoding: chunked
    - Content-Type: appropriate mime type based on format
    
    Example request:
    {
        "text": "تست آڈیو",
        "voice_id": "v_30s70t3a",
        "output_format": "ULAW_8000_8"
    }
    """
    # Map output formats to media types
    media_types = {
        "WAV_22050_16": "audio/wav",
        "WAV_22050_32": "audio/wav",
        "MP3_22050_32": "audio/mpeg",
        "MP3_22050_64": "audio/mpeg",
        "MP3_22050_128": "audio/mpeg",
        "OGG_22050_16": "audio/ogg",
        "ULAW_8000_8": "audio/basic"
    }

    payload = {
        "voiceId": request.voice_id,
        "text": request.text,
        "outputFormat": request.output_format
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
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Uplift API error: {str(e)}")

    # Determine media type from output format
    media_type = media_types.get(
        request.output_format, 
        "audio/mpeg"  # Default to MP3 if unknown format
    )

    return StreamingResponse(
        uplink_response.iter_content(chunk_size=1024),
        media_type=media_type,
        headers={
            "Transfer-Encoding": "chunked",
            "X-Audio-Format": request.output_format
        }
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)