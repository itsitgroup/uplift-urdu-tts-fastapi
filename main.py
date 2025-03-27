import io
import os
import requests
from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

# Uplift AI Orator API endpoint and credentials
API_URL = "https://api.upliftai.org/v1/synthesis/text-to-speech"
API_KEY = os.getenv("UPLIFT_AI_API_KEY")
VOICE_ID = "v_30s70t3a"  # recommended for realistic sound in rural Punjab accent
OUTPUT_FORMAT = "MP3_22050_128"

@app.get("/tts")
def text_to_speech(text: str = "سلام، آپ اِس وقت اوریٹر کی آواز سن رہے ہیں۔"):
    """
    Call Uplift AI’s Orator TTS API with the given text and return the audio.
    """
    payload = {
        "voiceId": VOICE_ID,
        "text": text,
        "outputFormat": OUTPUT_FORMAT
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