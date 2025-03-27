# uplift-urdu-tts-fastapi

A simple FastAPI implementation of the Uplift AI Text-to-Speech API for Urdu. It does have a frontend interface to test their streaming api in real-time. But beware, browsers do not support mew-law (ULAW_8000_8) so you will have to use the other formats.

## Project Structure

```text
./
├── frontend
│   └── index.html
├── main.py
└── requirements.txt
```

## Setup

1. **Install dependencies**

```bash
pip install -r requirements.txt
```

2. **Environment Configuration**

- Create a `.env` file in the root directory with your Uplift AI API key:

```env
UPLIFT_AI_API_KEY=your_api_key_here
```

## Running the Application

Start the FastAPI backend:

```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

Open `frontend/index.html` in a browser, input text, and stream audio from your backend.

## Features

- Real-time audio streaming via Uplift AI API.
- Customizable voice and audio formats.
- User-friendly web interface.

## Technology Stack

- FastAPI
- HTML/CSS/JavaScript
- Uplift AI Text-to-Speech API
