import torch
from transformers import AutoModelForSpeechSeq2Seq, AutoProcessor, pipeline
import numpy as np
from fastapi import UploadFile, File, HTTPException
from pydub import AudioSegment

# 设置设备和数据类型
device = "cuda:0" if torch.cuda.is_available() else "cpu"
torch_dtype = torch.float16 if torch.cuda.is_available() else torch.float32

# 加载模型和处理器
model_id = "openai/whisper-large-v3"
model = AutoModelForSpeechSeq2Seq.from_pretrained(
    model_id, 
    torch_dtype=torch_dtype, 
    low_cpu_mem_usage=True, 
    use_safetensors=True
)
model.to(device)

processor = AutoProcessor.from_pretrained(model_id)

# 创建 pipeline
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
        # 准备输入数据
        input_data = {
            "raw": audio_data,
            "sampling_rate": sampling_rate
        }
        
        # 使用 pipeline 进行转录
        result = pipe(input_data)
        return result["text"]
    except Exception as e:
        print(f"Error during transcription: {str(e)}")
        return None
