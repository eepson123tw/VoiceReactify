from fastapi import FastAPI, UploadFile, File, HTTPException, Form
from fastapi.responses import FileResponse, StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
import torch
from parler_tts import ParlerTTSForConditionalGeneration
from transformers import AutoTokenizer
import soundfile as sf
from io import BytesIO
import numpy as np
from pydub import AudioSegment
from pydantic import BaseModel
from src.voice_model import transcribe_audio

app = FastAPI()


# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # 允許的來源應包括你的前端地址
    allow_credentials=True,
    allow_methods=["*"],  # 允許的HTTP方法
    allow_headers=["*"],  # 允許的HTTP標頭
)



# Check if GPU is available
device = "cuda:0" if torch.cuda.is_available() else "cpu"
print(f"Using device: {device}")

# Load model and tokenizer
print("Loading model...")
model = ParlerTTSForConditionalGeneration.from_pretrained("parler-tts/parler-tts-mini-v1").to(device)
print("Model loaded successfully.")

print("Loading tokenizer...")
tokenizer = AutoTokenizer.from_pretrained("parler-tts/parler-tts-mini-v1")
print("Tokenizer loaded successfully.")

@app.post("/generate-voice")
async def generate_voice(prompt: str = Form(...), description: str = Form(...)):
    try:
        print(f"Received prompt: {prompt}")
        print(f"Received description: {description}")

        # Limit the length of the description and prompt text
        max_length = 128
        description = description[:max_length]
        prompt = prompt[:max_length]
        print(f"Truncated description: {description}")
        print(f"Truncated prompt: {prompt}")

        # Tokenize inputs
        print("Tokenizing inputs...")
        encoded_input = tokenizer(description, return_tensors="pt", padding=True, truncation=True, max_length=max_length)
        input_ids = encoded_input.input_ids.to(device)
        attention_mask = encoded_input.attention_mask.to(device)

        prompt_encoded = tokenizer(prompt, return_tensors="pt", padding=True, truncation=True, max_length=max_length)
        prompt_input_ids = prompt_encoded.input_ids.to(device)
        prompt_attention_mask = prompt_encoded.attention_mask.to(device)
        print("Inputs tokenized successfully.")

        # Generate speech with attention mask
        print("Generating speech...")
        generation = model.generate(
            input_ids=input_ids, 
            attention_mask=attention_mask,
            prompt_input_ids=prompt_input_ids, 
            prompt_attention_mask=prompt_attention_mask,
            max_length=200  # 限制生成的最大长度
        )
        print("Speech generated successfully.")

        # Convert the generated output to audio array
        audio_arr = generation.cpu().numpy().squeeze()

        # Save the generated audio file
        output_path = "parler_tts_out.wav"
        print(f"Saving output to {output_path}...")
        sf.write(output_path, audio_arr, model.config.sampling_rate)
        print(f"Output saved to {output_path}.")

        # Return the generated audio file
        def iterfile():
            with open(output_path, mode="rb") as file_like:
                yield from file_like

        print("Returning generated file...")
        return StreamingResponse(iterfile(), media_type="audio/wav", headers={"Content-Disposition": "attachment; filename=output.wav"})
    except Exception as e:
        print(f"Error occurred: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/transcribe")
async def transcribe(file: UploadFile = File(...)):
    try:
        # Print file info
        print(f"Received file: {file.filename}, Content Type: {file.content_type}")
        
        # Load the uploaded audio file
        audio = AudioSegment.from_file(file.file)
        print(f"Audio duration: {audio.duration_seconds} seconds, Channels: {audio.channels}")

        # Resample to 16 kHz
        audio = audio.set_frame_rate(16000)

        # Convert audio to NumPy array and normalize
        audio_data = np.array(audio.get_array_of_samples()).astype(np.float32) / 32768.0

        # Transcribe audio
        transcription = transcribe_audio(audio_data, sampling_rate=16000)

        if transcription:
            return {"transcription": transcription}
        else:
            raise ValueError("Transcription failed or returned unexpected format.")

    except Exception as e:
        print(f"Error during transcription: {e}")
        raise HTTPException(status_code=500, detail=str(e))  # Corrected line
    
@app.get("/")
async def root():
    return {"message": "Welcome to the Parler TTS API! Use the /generate-voice/ endpoint to generate speech."}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
