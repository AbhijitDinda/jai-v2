# LiveKit + Groq Voice Agent

An end-to-end AI voice agent:

- **STT**: Groq `whisper-large-v3`
- **LLM**: Groq `llama-3.3-70b-versatile`
- **TTS**: ElevenLabs
- **VAD**: Silero
- **Transport**: LiveKit WebRTC

## 1. About your credentials

The env values you pasted earlier included live secrets, so they were **not** used
anywhere in this project. Please:

1. Treat those keys as compromised and rotate them (LiveKit, Deepgram, OpenAI,
   Rumik, Groq, ElevenLabs — regenerate each in its respective dashboard).
2. Use `.env.local.example` below as the template, fill in the *new* keys locally,
   and never paste real secrets into a chat.

## 2. Backend setup

```bash
cd livekit-voice-agent
cp .env.local.example .env.local
# now edit .env.local with your real (rotated) keys

python3 -m venv venv
source venv/bin/activate
python3 -m pip install -r requirements.txt

python3 agent.py dev
```

### Variable name notes

Your original list used slightly different variable names than what the LiveKit
plugins expect. Mapping:

| Your original name  | Required name (used by the plugin) |
|----------------------|-------------------------------------|
| `GROQ_KEY`           | `GROQ_API_KEY`                      |
| `ELEVENLABS_API_KEY` | `ELEVEN_API_KEY`                    |

`.env.local.example` already uses the correct required names — just paste your
rotated key values in.

You don't need `DEEPGRAM_API_KEY`, `OPENAI_API_KEY`, or the Rumik variables for
this configuration, since Groq handles both STT and LLM, and ElevenLabs handles TTS.

## 3. Frontend setup (Next.js voice assistant UI)

The LiveKit CLI scaffolds this for you — it needs to run on your own machine
(it opens a browser to authenticate with your LiveKit Cloud account, which I
can't do from here):

```bash
# install the LiveKit CLI if you haven't already
curl -sSL https://get.livekit.io/cli | bash

# authenticate
lk cloud auth

# from the parent directory of livekit-voice-agent/
lk app create --template voice-assistant-frontend
cd voice-assistant-frontend
pnpm install
pnpm dev
```

Then visit `http://localhost:3000`, click **Connect**, and talk to your agent
(make sure `agent.py dev` is running in another terminal first).

## 4. Try the challenge

Turn this into a travel-planning assistant by editing the `initial_ctx` system
prompt in `agent.py`, e.g.:

```python
text=(
    "You are a friendly travel agent voice assistant. Help the user plan "
    "trips by asking about their destination, budget, dates, and interests, "
    "then suggest itineraries. Keep responses short and conversational."
),
```
