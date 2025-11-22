Interview Practice Partner — AI Voice-Based Mock Interview Agent

This project is an advanced conversational AI system built as part of the Eightfold.ai AI Agent Building Assignment.
It simulates a real interviewer, conducts role-specific mock interviews, asks intelligent follow-up questions, and provides deeply structured feedback — all through natural voice interactions.

The system focuses on conversation quality, agentic decision-making, and human-like interaction flow, matching the assignment’s evaluation criteria.

Features
Voice Interaction (STT + TTS)

Voice-based interviewing for natural, hands-free conversations

Powered by Groq Whisper for transcription

Groq TTS with a gTTS fallback for reliability

Adaptive Warmup Phase

Friendly warmup questions to build rapport

Adaptive continuation or early transition based on user comfort

Never repeats questions

Evaluates communication quality to decide when to start the interview

Agentic Interview Behavior

Structured multi-stage interview flow

Smart follow-ups when answers are incomplete or vague

Advances to the next question when answers are strong

Ends early when consistent quality is detected

Incorporates role-specific logic for multiple domains

Detailed Final Feedback

Scoring categories: structure, clarity, examples, communication, confidence, technical depth, follow-up handling

List of strengths and targeted improvements

STAR/CAR-style rewritten answer for learning

High-level readiness summary

Multi-Persona Support

Designed to handle several user profiles for testing:

Confused user

Efficient user

Chatty user

Edge-case or off-topic user

Project Structure
root/
│
├── frontend.py            # Main Streamlit UI and interview state machine
│
├── utils/
│   ├── llm_client.py      # Groq LLM client with strict JSON enforcement
│   ├── voice.py           # Speech-to-text and text-to-speech processing
│   ├── json_prompts.py    # Warmup, interview, and feedback system prompts
│   └── roles.json         # Domain-specific questions and follow-ups
│
├── requirements.txt
└── README.md


Important components:

frontend.py — orchestrates warmup → interview → feedback flow

utils/json_prompts.py — contains all system prompts and JSON schemas

utils/llm_client.py — interfaces with the Llama-4-Scout model

utils/voice.py — handles audio recording, STT, and TTS

utils/roles.json — defines supported roles and question sets

Setup Instructions
1. Clone the Repository
git clone <your-public-repo-link>
cd <your-repo>

2. Create and Activate Virtual Environment
python -m venv venv
venv\Scripts\activate      # Windows
source venv/bin/activate   # Mac/Linux

3. Install Dependencies
pip install -r requirements.txt

4. Configure Environment Variables

Create a .env file in the project root:

GROQ_API_KEY=your_api_key_here


Required for:

LLM completions

Speech-to-text

Text-to-speech

5. Run the Application
streamlit run frontend.py

Architecture Overview

The system follows a three-layer architecture for clarity and extensibility.

1. Conversation Engine (LLM Reasoning Layer)

Files: llm_client.py, json_prompts.py
Handles:

Strict JSON system prompting

Warmup question logic

Follow-up decision making

Early termination rules

Final feedback generation

Reasoning:
Strict JSON prevents unpredictable LLM outputs, stabilizing the entire pipeline.
It enables state-machine-style reasoning essential for multi-turn interviews.

2. Voice Engine (Input/Output Processing)

File: voice.py
Handles:

Groq Whisper transcription

Groq PlayAI TTS

gTTS fallback for reliability

Reasoning:
Creates a realistic, highly natural interaction experience.
Ensures smooth demo even with API variability.

3. Experience Layer (UI + State Management)

File: frontend.py

Handles:

Stage transitions

Session state

Rendering questions and transcriptions

Collecting audio input

Displaying structured feedback

Reasoning:
Streamlit provides a clean, interactive interface ideal for demos and rapid development.

Key Design Decisions
Strict JSON Enforcement

Ensures predictable responses from the LLM, eliminating hallucinations and parsing failures.
Essential for reliable state management.

Multi-Stage Interview Flow

Warmup → Interview → Feedback
Improves realism and user comfort while maintaining a professional tone.

Role-Driven Interviewing

Role definitions stored in roles.json allow flexibility and coverage across domains.

Follow-Up Intelligence

Follow-ups are precise, context-aware, and depth-oriented rather than generic or repetitive.

Voice-First Interaction

Chosen to satisfy assignment preference and elevate the immersive interviewing experience.

Testing Strategy

Tested across recommended personas:

Confused: vague answers → triggers follow-ups

Efficient: strong answers → quick progression

Chatty: long answers → agent extracts focus

Edge-case: irrelevant answers → agent recovers gracefully

These scenarios validate agent adaptability and conversational robustness.

Demo Video Guidelines

To align with assignment requirements:

Maximum 10-minute duration

Pure product demonstration (no slides)

Include:

Multiple roles

Warmup behavior

Follow-up questions

Final feedback

Voice interaction

Different user personas

Strengths of This Project

Strong agentic reasoning

Voice-first design

Clean modular architecture

Strict JSON for reliability

Highly adaptive follow-up logic

Detailed scoring and feedback

Professional and scalable code structure

License

MIT License.
