import os
import base64
import tempfile
from gtts import gTTS
from dotenv import load_dotenv

try:
    from groq import Groq
except Exception:
    Groq = None

load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

client = None
if Groq and GROQ_API_KEY:
    try:
        client = Groq(api_key=GROQ_API_KEY)
    except:
        client = None


def transcribe_audio_bytes(audio_bytes: bytes, model="whisper-large-v3"):
    if client is None:
        return "[STT error: Groq client not configured]"
    try:
        response = client.audio.transcriptions.create(
            file=("audio.wav", audio_bytes, "audio/wav"),
            model=model
        )
        if isinstance(response, dict) and "text" in response:
            return response["text"]
        if hasattr(response, "text"):
            return response.text
        return str(response)
    except Exception as e:
        return f"[STT error: {str(e)}]"



def synthesize_speech_bytes(text: str, model="playai-tts", voice="alloy"):
    if client:
        try:
            response = client.audio.speech.create(
                model=model,
                input=text,
                voice=voice
            )

            if isinstance(response, dict):
                audio_b64 = response.get("audio")
            else:
                audio_b64 = getattr(response, "audio", None)

            if audio_b64:
                return base64.b64decode(audio_b64), "wav"
        except:
            pass

    try:
        tts = gTTS(text, lang="en")
        tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
        tts.save(tmp.name)
        with open(tmp.name, "rb") as f:
            audio_bytes = f.read()
        os.remove(tmp.name)
        return audio_bytes, "mp3"
    except:
        return None, None
