# AI Voice SDR: CloudSave Cold Caller

An intelligent, real-time voice AI agent built to simulate a B2B cold call. This bot acts as "Alex," an SDR for a hypothetical company called CloudSave. It dynamically converses with prospects, handles objections, qualifies leads based on cloud infrastructure spend, and automatically records the outcome.



## 🌟 Key Features

* **Real-Time Voice Interaction:** Full-duplex voice conversation with interruption handling (barge-in) using Pipecat.
* **Adaptive Conversational Design:** No hardcoded linear scripts. The bot uses state-based prompting to navigate the conversation dynamically, extract information in any order, and pivot based on user resistance.
* **Automated Qualification:** Identifies if a lead uses AWS/Azure and spends >$1,000/month.
* **Intelligent Tool Calling:** Uses function calling (`record_call_outcome`) to decide when the conversation is naturally over, saving the structured lead data to a JSON file.
* **Full-Stack Ready:** Designed to run as a subprocess spawned by a FastAPI backend (`server.py`), passing data back to a React frontend.
* **Hardware Optimized:** Audio sample rates (16kHz) strictly synchronized across Deepgram TTS and local macOS audio transports to guarantee zero-stutter, high-fidelity audio.

## 🛠️ Technology Stack

* **Framework:** [Pipecat](https://github.com/pipecat-ai/pipecat) (Open-source framework for voice/multimodal AI)
* **LLM Engine:** [Groq](https://groq.com/) (`llama-3.3-70b-versatile` / `llama-3.1-8b-instant`) for ultra-low latency inference and tool calling.
* **Speech-to-Text (STT):** [Deepgram](https://deepgram.com/)
* **Text-to-Speech (TTS):** Deepgram (Aura Voices - `aura-helios-en`)
* **Voice Activity Detection (VAD):** Silero VAD

## ⚙️ Architecture Flow

1.  **Listen:** Local transport captures user audio via mic. Silero VAD detects speech endpoints.
2.  **Transcribe:** Deepgram STT converts audio to text instantly.
3.  **Think:** Groq Llama 3 processes the context. It decides whether to reply verbally or trigger the closing tool.
4.  **Speak:** Deepgram TTS synthesizes the response into audio.
5.  **Resolve:** Once qualified/disqualified, the LLM calls `record_call_outcome`, saves `outcome.json`, and triggers a clean `os._exit(0)` to release hardware resources.

## 🚀 Setup & Installation

### Prerequisites
* Python 3.11+
* API Keys for Deepgram and Groq.

### 1. Clone & Environment setup
```bash
git clone <your-repo-url>
cd cold-call-bot
python -m venv venv
source venv/bin/activate