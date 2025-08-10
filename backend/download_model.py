
import os
from transformers import pipeline

MODEL_ID = os.getenv("HUGGING_FACE_TRANSCRIPTION_MODEL", "openai/whisper-base")

# This will download and cache the model and tokenizer
pipeline("automatic-speech-recognition", model=MODEL_ID)

print(f"Model {MODEL_ID} downloaded successfully.")
