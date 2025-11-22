import streamlit as st
import json
import tempfile
import os
import base64
from pathlib import Path
from typing import Optional

from utils.voice import transcribe_audio_bytes, synthesize_speech_bytes
from utils.llm_client import call_agent_llm
from utils.json_prompts import (
    WARMUP_PROMPT,
    WARMUP_CONTINUE_PROMPT,
    INTERVIEW_DECISION_PROMPT,
    FINAL_FEEDBACK_PROMPT,
)

ASSIGNMENT_PDF_PATH = "/mnt/data/AI Agent Building Assignment - Eightfold.pdf"
MIN_INTERVIEW_QUESTIONS = 3

st.set_page_config(page_title="Interview Practice Partner", layout="centered")
st.title("Interview Practice Partner")

def ensure_session_keys():
    defaults = {
        "stage": "warmup",            
        "history": [],                
        "warmup_turn": 0,
        "warmup_question": None,
        "q_index": 0,
        "current_question": None,
        "debug": None,
        "feedback_data": None,
        "followup_count": 0,          
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

ensure_session_keys()


with st.sidebar:
    st.header("Session Settings")
    roles_path = Path("utils/roles.json")
    try:
        roles = json.loads(roles_path.read_text())
    except Exception:
        roles = {
            "software_engineer": {
                "display_name": "Software Engineer",
                "base_questions": ["Tell me about yourself.", "Explain a project you built.", "What are your strengths?"],
            }
        }

    role = st.selectbox("Choose role", list(roles.keys()), format_func=lambda k: roles[k]["display_name"])
    experience = st.selectbox("Experience level", ["Fresher", "1-2 years", "3-5 years", "Senior"])
    difficulty = st.selectbox("Difficulty", ["Easy", "Medium", "Hard"])

    st.markdown("---")
    if Path(ASSIGNMENT_PDF_PATH).exists():
        st.markdown(f"[View assignment PDF]({ASSIGNMENT_PDF_PATH})")

    if st.button("Reset session"):
        st.session_state.clear()
        ensure_session_keys()
        st.rerun()

def save_bytes_to_wav_and_play(bts: bytes):
    """Save raw WAV/MP3 bytes to temp file and play via st.audio."""
    if not bts:
        return
    if isinstance(bts, str):
        try:
            bts = base64.b64decode(bts)
        except Exception:
            return
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
    tmp.write(bts)
    tmp.flush()
    tmp.close()
    try:
        st.audio(tmp.name)
    finally:
        try:
            os.remove(tmp.name)
        except Exception:
            pass

def speak_text(text: str):
    """Silent TTS. If TTS fails, no logs, no warnings, no UI messages."""
    if not text:
        return

    try:
        audio_data = synthesize_speech_bytes(text)
    except Exception:
        return  

    if not audio_data:
        return 

    if isinstance(audio_data, (bytes, bytearray)):
        save_bytes_to_wav_and_play(bytes(audio_data))
        return
    if isinstance(audio_data, str):
        try:
            decoded = base64.b64decode(audio_data)
            save_bytes_to_wav_and_play(decoded)
        except Exception:
            pass  
        return


    if isinstance(audio_data, dict):
        for key in ("audio", "content", "data"):
            val = audio_data.get(key)
            if val:
                try:
                    if isinstance(val, (bytes, bytearray)):
                        save_bytes_to_wav_and_play(bytes(val))
                    elif isinstance(val, str):
                        save_bytes_to_wav_and_play(base64.b64decode(val))
                except Exception:
                    pass
                return



if st.session_state.stage == "warmup":
    st.header("Warmup Phase")
    st.write("Purpose: Help you relax and share background.")

    if st.session_state.warmup_turn == 0 and not st.session_state.warmup_question:
        raw_q = call_agent_llm(WARMUP_PROMPT.format(role=role, experience=experience))
        try:
            parsed = json.loads(raw_q)
            wq = parsed.get("question", "Hi — could you introduce yourself?")
        except Exception:
            wq = "Hi — could you introduce yourself?"
        st.session_state.warmup_question = wq
        st.session_state.warmup_turn = 1
        speak_text(wq)

    st.markdown(
    f"<div style='font-size:20px; font-weight:700; color:#1a237e; "
    "padding:12px 16px; background:#eef2ff; border-left:6px solid #4b6bff; "
    "border-radius:8px; margin:10px 0;'>"
    f"Interviewer: {st.session_state.warmup_question}"
    "</div>",
    unsafe_allow_html=True
)

    audio_key = f"warmup_audio_{st.session_state.warmup_turn}"
    audio_file = st.audio_input("🎙️ Record your warmup answer (press Stop when done)", key=audio_key)

    if audio_file is not None:
        try:
            audio_bytes = audio_file.getvalue()
        except Exception:
            try:
                audio_bytes = audio_file.read()
            except Exception:
                audio_bytes = None

        if not audio_bytes:
            st.error("Could not read recorded audio. Try again.")
        else:
            save_bytes_to_wav_and_play(audio_bytes)
            with st.spinner("Transcribing..."):
                transcript = transcribe_audio_bytes(audio_bytes)

            st.markdown("**Transcript:**")
            st.write(transcript)

            st.session_state.history.append({"q": st.session_state.warmup_question, "a": transcript})

            decision_raw = call_agent_llm(
                WARMUP_CONTINUE_PROMPT.format(
                    warmup_turn=st.session_state.warmup_turn,
                    user_answer=transcript,
                    history=json.dumps(st.session_state.history, indent=2),
                )
            )
            try:
                decision = json.loads(decision_raw)
            except Exception:
                repair = call_agent_llm("Return warmup JSON only: " + decision_raw)
                try:
                    decision = json.loads(repair)
                except Exception:
                    decision = {"next": "start_interview"}

            nxt = decision.get("next", "start_interview")

            if st.session_state.warmup_turn >= 3:
                nxt = "start_interview"

            if nxt == "ask_more":
                st.session_state.warmup_turn += 1
                st.session_state.warmup_question = decision.get("question", "Tell me more about your recent project.")
                speak_text(st.session_state.warmup_question)
                st.rerun()
            else:
                st.session_state.stage = "interview"
                st.session_state.current_question = None
                st.session_state.followup_count = 0
                st.rerun()
    else:
        st.info("Click the record button above to speak your answer, then press Stop. The app will transcribe and continue the flow.")

elif st.session_state.stage == "interview":
    st.header("Interview Phase")
    st.write("The AI agent will ask role-specific technical questions.")

    questions = roles.get(role, {}).get("base_questions", ["Tell me about yourself."])

    if st.session_state.current_question is None:
        if st.session_state.q_index >= len(questions):
            st.session_state.stage = "feedback"
            st.rerun()
        st.session_state.current_question = questions[st.session_state.q_index]
        speak_text(st.session_state.current_question)

    st.markdown(
    f"<div style='font-size:20px; font-weight:700; color:#1a237e; "
    "padding:12px 16px; background:#eef2ff; border-left:6px solid #4b6bff; "
    "border-radius:8px; margin:10px 0;'>"
    f"Interviewer: {st.session_state.current_question}"
    "</div>",
    unsafe_allow_html=True
)


    audio_key = f"interview_audio_q{st.session_state.q_index}_f{st.session_state.followup_count}"
    audio_file = st.audio_input("Record your answer (Stop to finish)", key=audio_key)

    if audio_file is not None:
        try:
            audio_bytes = audio_file.getvalue()
        except Exception:
            try:
                audio_bytes = audio_file.read()
            except Exception:
                audio_bytes = None

        if not audio_bytes:
            st.error("Could not read recorded audio. Try again.")
        else:
            save_bytes_to_wav_and_play(audio_bytes)
            with st.spinner("Transcribing..."):
                transcript = transcribe_audio_bytes(audio_bytes)

            st.markdown("**Transcript:**")
            st.write(transcript)

            st.session_state.history.append({"q": st.session_state.current_question, "a": transcript})

            decision_raw = call_agent_llm(
                INTERVIEW_DECISION_PROMPT.format(
                    role=role,
                    difficulty=difficulty,
                    current_question=st.session_state.current_question,
                    user_answer=transcript,
                    history_json=json.dumps(st.session_state.history, indent=2),
                )
            )

            try:
                decision = json.loads(decision_raw)
            except Exception:
                repair = call_agent_llm("Return valid INTERVIEW JSON only: " + decision_raw)
                try:
                    decision = json.loads(repair)
                except Exception:
                    decision = {"action": "end"}

            action = decision.get("action", "end")

            if action == "end" and (st.session_state.q_index + 1) < MIN_INTERVIEW_QUESTIONS:
                action = "next"

            if action == "follow_up":
                st.session_state.current_question = decision.get("question", "Can you expand on that?")
                st.session_state.followup_count = st.session_state.followup_count + 1
                speak_text(st.session_state.current_question)
                st.rerun()
            elif action == "next":
                st.session_state.q_index += 1
                st.session_state.current_question = None
                st.session_state.followup_count = 0
                st.rerun()
            else:
                st.session_state.stage = "feedback"
                st.rerun()
    else:
        st.info("Click the record button above to speak your answer, then press Stop. The app will transcribe and continue the interview.")

else:
    st.header("Final Feedback")
    st.write("Generating structured feedback based on your interview...")

    history_json = json.dumps(st.session_state.history, indent=2)
    raw = call_agent_llm(FINAL_FEEDBACK_PROMPT.format(role=role, history_json=history_json))

    try:
        data = json.loads(raw)
    except Exception:
        repair = call_agent_llm("Return STRICT FEEDBACK JSON ONLY: " + raw)
        try:
            data = json.loads(repair)
        except Exception:
            data = {
                "feedback": {
                    "scores": {"structure": 3, "clarity": 3, "examples": 3, "communication": 3, "confidence": 3},
                    "strengths": ["Clear introduction."],
                    "improvements": ["Provide more concrete examples."],
                    "sample_answer": "Improved example answer placeholder.",
                    "summary": "Overall solid performance."
                }
            }

    feedback = data["feedback"]
    st.markdown("### Scores")
    for k, v in feedback["scores"].items():
        st.write(f"- **{k.capitalize()}:** {v}/5")

    st.markdown("### Strengths")
    for s in feedback.get("strengths", []):
        st.write(f"- {s}")

    st.markdown("### Improvements")
    for imp in feedback.get("improvements", []):
        st.write(f"- {imp}")

    st.markdown("### Sample Improved Answer")
    st.write(feedback.get("sample_answer", ""))

    st.markdown("### Summary")
    st.write(feedback.get("summary", ""))

    summary_speak = (
        f"Final feedback. Structure {feedback['scores']['structure']} out of 5. "
        f"Clarity {feedback['scores']['clarity']} out of 5. "
        f"Strengths: {', '.join(feedback.get('strengths', []))}. "
        f"Improvements: {', '.join(feedback.get('improvements', []))}. "
        f"Summary: {feedback.get('summary','')}"
    )
    speak_text(summary_speak)

    if st.button("Restart interview"):
        st.session_state.clear()
        ensure_session_keys()
        st.rerun()
