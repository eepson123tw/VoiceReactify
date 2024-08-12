from fastapi import FastAPI, HTTPException, Form
from fastapi.responses import FileResponse, StreamingResponse
import torch
from parler_tts import ParlerTTSForConditionalGeneration
from transformers import AutoTokenizer
import soundfile as sf
import os

app = FastAPI()

# 检查是否有可用的 GPU
device = "cuda:0" if torch.cuda.is_available() else "cpu"
print(f"Using device: {device}")

# 加载模型和分词器
print("Loading model...")

model = ParlerTTSForConditionalGeneration.from_pretrained("parler-tts/parler-tts-mini-v1").to(device)

print("Model loaded successfully.")

print("Loading tokenizer...")
tokenizer = AutoTokenizer.from_pretrained("parler-tts/parler-tts-mini-v1")
print("Tokenizer loaded successfully.")

@app.post("/generate-voice/")
async def generate_voice(prompt: str = Form(...), description: str = Form(...)):
    try:
        print(f"Received prompt: {prompt}")
        print(f"Received description: {description}")

        # 限制描述和提示文本的长度
        max_length = 128
        description = description[:max_length]
        prompt = prompt[:max_length]
        print(f"Truncated description: {description}")
        print(f"Truncated prompt: {prompt}")
        
        # 将描述和提示文本转换为模型的输入格式
        print("Tokenizing inputs...")
        encoded_input = tokenizer(description, return_tensors="pt", padding=True, truncation=True, max_length=max_length)
        input_ids = encoded_input.input_ids.to(device)
        attention_mask = encoded_input.attention_mask.to(device)

        prompt_encoded = tokenizer(prompt, return_tensors="pt", padding=True, truncation=True, max_length=max_length)
        prompt_input_ids = prompt_encoded.input_ids.to(device)
        prompt_attention_mask = prompt_encoded.attention_mask.to(device)
        print("Inputs tokenized successfully.")

        # 生成语音时同时传递 attention_mask 和 prompt_attention_mask
        print("Generating speech...")
        generation = model.generate(
            input_ids=input_ids, 
            attention_mask=attention_mask,
            prompt_input_ids=prompt_input_ids, 
            prompt_attention_mask=prompt_attention_mask,
            max_length=200  # 限制生成的最大长度
        )
        print("Speech generated successfully.")

        audio_arr = generation.cpu().numpy().squeeze()

        # 保存生成的音频文件
        output_path = "parler_tts_out.wav"
        print(f"Saving output to {output_path}...")
        sf.write(output_path, audio_arr, model.config.sampling_rate)
        print(f"Output saved to {output_path}.")

        # 使用流式响应返回生成的音频文件
        def iterfile():
            with open(output_path, mode="rb") as file_like:
                yield from file_like

        print("Returning generated file...")
        return StreamingResponse(iterfile(), media_type="audio/wav", headers={"Content-Disposition": "attachment; filename=output.wav"})
    except Exception as e:
        print(f"Error occurred: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
async def root():
    return {"message": "Welcome to the Parler TTS API! Use the /generate-voice/ endpoint to generate speech."}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
