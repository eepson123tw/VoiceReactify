import torch
from transformers import AutoModelForSpeechSeq2Seq, AutoProcessor, pipeline
import numpy as np
from fastapi import UploadFile, File, HTTPException
from pydub import AudioSegment

device = "cuda:0" if torch.cuda.is_available() else "cpu"
torch_dtype = torch.float16 if torch.cuda.is_available() else torch.float32

model_id = "openai/whisper-large-v3"
model = AutoModelForSpeechSeq2Seq.from_pretrained(
    model_id, 
    torch_dtype=torch_dtype, 
    low_cpu_mem_usage=True, 
    use_safetensors=True
)
model.to(device)

processor = AutoProcessor.from_pretrained(model_id)

pipe = pipeline(
    "automatic-speech-recognition",
    model=model,
    tokenizer=processor.tokenizer,
    feature_extractor=processor.feature_extractor,
    torch_dtype=torch_dtype,
    device=device,
    chunk_length_s=30,
    batch_size=16,
)

def transcribe_audio(audio_data, sampling_rate):
    try:
        input_data = {
            "raw": audio_data,
            "sampling_rate": sampling_rate
        }
        result = pipe(input_data,return_timestamps=True)
        # or can return result["text"]
        return result["chunks"]
    except Exception as e:
        print(f"Error during transcription: {str(e)}")
        return None
