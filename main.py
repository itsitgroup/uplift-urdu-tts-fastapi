import io
import os
import requests
from typing import Optional
from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

# Uplift AI Orator API endpoint and credentials
API_URL = "https://api.upliftai.org/v1/synthesis/text-to-speech"
API_KEY = os.getenv("UPLIFT_AI_API_KEY")
VOICE_ID = "v_30s70t3a"  # recommended for realistic sound in rural Punjab accent
OUTPUT_FORMAT = "MP3_22050_128"

# Request model for JSON body
class TTSRequest(BaseModel):
    text: Optional[str] = "سلام، آپ اِس وقت اوریٹر کی آواز سن رہے ہیں۔"
    voice_id: Optional[str] = VOICE_ID
    output_format: Optional[str] = OUTPUT_FORMAT

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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)