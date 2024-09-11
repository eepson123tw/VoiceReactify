import os
import asyncio
import json
import uuid
from rich.console import Console
from datetime import datetime
from fastapi import FastAPI, UploadFile, File, HTTPException, Form
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from fastapi.responses import StreamingResponse,JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import torch
import soundfile as sf
import numpy as np
import asyncio
from pydub import AudioSegment

from TTS.api import TTS
from src.voice_model import transcribe_audio
from src.read_service_config import check_system_resources
from src.connectionDB import create_connection, create_voice_record_table



class AddPermissionsPolicyMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        response = await call_next(request)
        # Add the Permissions-Policy header
        response.headers["Permissions-Policy"] = "browsing-topics, private-state-token-redemption, private-state-token-issuance"
        return response


console = Console()

# Lifespan function using async context manager
async def lifespan(app: FastAPI):
    console.print("[cyan]Starting application...[/cyan]")
    conn = create_connection()
    if conn:
        create_voice_record_table(conn)
        conn.close()
    yield  # This allows the app to continue running
    # Cleanup logic if needed


app = FastAPI(lifespan=lifespan)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # 允許的來源應包括你的前端地址
    allow_credentials=True,
    allow_methods=["*"],  # 允許的HTTP方法
    allow_headers=["*"],  # 允許的HTTP標頭
)
app.add_middleware(AddPermissionsPolicyMiddleware)

# Check if GPU is available
device = "cuda:0" if torch.cuda.is_available() else "cpu"
print(f"Using device: {device}")

# Get device
device = "cuda" if torch.cuda.is_available() else "cpu"

# List available 🐸TTS models
print(TTS().list_models())

# Init TTS
tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2").to(device)

outfile_dir = "outVoiceFile"
os.makedirs(outfile_dir, exist_ok=True)


@app.post("/generate-voice")
async def generate_voice(
    prompt: str = Form(...), 
    description: str = Form(...),
):
    try:
        # Log the inputs
        print(f"Received prompt: {prompt}")
        print(f"Received description: {description}")
        # Create a unique file name with timestamp and UUID
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        unique_id = uuid.uuid4()
        output_filename = f"parler_tts_{timestamp}_{unique_id}.wav"
        output_path = os.path.join(outfile_dir, output_filename)
        pakora_path = os.path.join('pekora', "pekora.wav")

        tts.tts_to_file(prompt, speaker_wav=pakora_path, language="en", file_path=output_path)

        # Generator to stream the file
        def iterfile():
            with open(output_path, mode="rb") as file_like:
                yield from file_like

        # Return the generated audio file as a stream
        return StreamingResponse(iterfile(), media_type="audio/wav", headers={"Content-Disposition": f"attachment; filename={output_filename}"})

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))





async def transcribe_streaming(audio_segment):
    for transcription in audio_segment:
        print(f"Transcription: {transcription}")
        yield f"data: {json.dumps({'transcription': transcription})}\n\n"
        await asyncio.sleep(0.1) 


@app.post("/transcribe-stream")
async def transcribe(file: UploadFile = File(...),return_timestamps: bool = Form(False)):
    try:
        print("===== FILE INFO =====")
        print(f"Received file: {file.filename}, Content Type: {file.content_type}")

        audio = AudioSegment.from_file(file.file)
        print("===== AUDIO INFO =====")
        print(f"Audio duration: {audio.duration_seconds} seconds, Channels: {audio.channels}")
        audio = audio.set_frame_rate(16000)
        print("===== STARTING STREAMING TRANSCRIPTION =====")
        audio_data = np.array(audio.get_array_of_samples()).astype(np.float32) / 32768.0
        transcription = transcribe_audio(audio_data, sampling_rate=16000,return_timestamps=return_timestamps)
        print("===== STREAMING TRANSCRIPTION COMPLETED =====")
        print(f"transcription: {transcription} ")
        return StreamingResponse(transcribe_streaming(transcription), media_type="text/event-stream")
    
    except MemoryError as me:
        print("***** MEMORY ERROR *****")
        print("MemoryError during transcription: ", me)
        raise HTTPException(status_code=500, detail="Memory error: " + str(me))
    except TimeoutError as te:
        print("***** TIMEOUT ERROR *****")
        print("TimeoutError during transcription: ", te)
        raise HTTPException(status_code=500, detail="Timeout error: " + str(te))
    except Exception as e:
        print("***** GENERAL ERROR *****")
        print(f"Error during transcription: {e}")
        raise HTTPException(status_code=500, detail=str(e))





@app.post("/transcribe")
async def transcribe(file: UploadFile = File(...),return_timestamps: bool = Form(False)):
    try:
        # Print file info with clear separators
        print("===== FILE INFO =====")
        print(f"Received file: {file.filename}, Content Type: {file.content_type}")
        
        #file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        unique_id = uuid.uuid4()
        output_filename = f"parler_tts_{timestamp}_{unique_id}.wav"
        output_path = os.path.join(outfile_dir, output_filename)
        # Load the uploaded audio file
        audio = AudioSegment.from_file(file.file)
        print("===== AUDIO INFO =====")
        print(f"Audio duration: {audio.duration_seconds} seconds, Channels: {audio.channels}")

        # Resample to 16 kHz
        audio = audio.set_frame_rate(16000)
        print("===== CONVERTING AUDIO TO NUMPY ARRAY =====")
        audio_data = np.array(audio.get_array_of_samples()).astype(np.float32) / 32768.0
        print(f"return_timestamps: {return_timestamps} ")
        # Transcribe audio
        transcription = transcribe_audio(audio_data, sampling_rate=16000,return_timestamps=return_timestamps)
        print(f"transcription: {transcription} ")
        if transcription:
            print("===== TRANSCRIPTION SUCCESSFUL =====")
            print(f"Transcription: {transcription}")
            return {"transcription": transcription}
        else:
            print("===== TRANSCRIPTION FAILED =====")
            raise ValueError("Transcription failed or returned unexpected format.")

    except MemoryError as me:
        print("***** MEMORY ERROR *****")
        print("MemoryError during transcription: ", me)
        raise HTTPException(status_code=500, detail="Memory error: " + str(me))
    except TimeoutError as te:
        print("***** TIMEOUT ERROR *****")
        print("TimeoutError during transcription: ", te)
        raise HTTPException(status_code=500, detail="Timeout error: " + str(te))
    except Exception as e:
        print("***** GENERAL ERROR *****")
        print(f"Error during transcription: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/checkSystem")
async def check_system():
    result = check_system_resources()
    return JSONResponse(content=result.dict())


@app.get("/")
async def root():
    return {"message": "Welcome to the Parler TTS API! Use the /generate-voice/ endpoint to generate speech."}



if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
