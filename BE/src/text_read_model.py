import torch
from TTS.api import TTS

# Get device
device = "cuda" if torch.cuda.is_available() else "cpu"

# List available 🐸TTS models
print(TTS().list_models())

# Init TTS
tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2").to(device)


tts.tts_to_file("Python auto-instrumentation library for LlamaIndex.These traces are fully OpenTelemetry compatible and can be sent to an OpenTelemetry collector for viewing, such as arize-phoenix.", speaker_wav="../pekora/pekora.wav", language="en", file_path="../outVoiceFile/parler_tts_20240907_010021_19ecbb16-b490-4539-8776-eb23e5c0b29e.wav")

