# Jai — Setup Guide

Jai is a voice AI agent for Jaro Education.  
**Backend** (`jai-v2`) — Python / LiveKit Agents  
**Frontend** (`jai`) — Next.js / LiveKit React

---

## Prerequisites

| Tool | Version |
|------|---------|
| Python | 3.10+ |
| Node.js | 18+ |
| pnpm | any (installed below) |

---

## 1. Clone the repo

```bash
git clone <repo-url>
cd <repo-folder>
```

---

## 2. Backend setup (`jai-v2`)

### 2a. Install dependencies

```bash
cd jai-v2
pip install -r requirements.txt
```

### 2b. Create environment file

Create `jai-v2/.env.local`:

```env
LIVEKIT_URL=wss://<your-project>.livekit.cloud
LIVEKIT_API_KEY=<your-livekit-api-key>
LIVEKIT_API_SECRET=<your-livekit-api-secret>
GROQ_API_KEY=<your-groq-api-key>
ELEVEN_API_KEY=<your-elevenlabs-api-key>
```

> Get LiveKit credentials from [cloud.livekit.io](https://cloud.livekit.io)  
> Get Groq key from [console.groq.com](https://console.groq.com)  
> Get ElevenLabs key from [elevenlabs.io](https://elevenlabs.io)

### 2c. Build the RAG index (run once)

This scrapes jaroeducation.com and builds the vector index:

```bash
python scraper.py   # scrapes site → saves jaro_chunks.json
python rag.py       # builds FAISS index → saves jaro_index.faiss
```

> Skip this step if `jaro_index.faiss` and `jaro_chunks_indexed.json` already exist.

### 2d. Start the agent

```bash
python agent.py dev
```

---

## 3. Frontend setup (`jai`)

### 3a. Install pnpm (if not installed)

```bash
npm install -g pnpm
```

### 3b. Install dependencies

```bash
cd jai
pnpm install
```

### 3c. Create environment file

Create `jai/.env.local`:

```env
LIVEKIT_URL=wss://<your-project>.livekit.cloud
LIVEKIT_API_KEY=<your-livekit-api-key>
LIVEKIT_API_SECRET=<your-livekit-api-secret>
```

### 3d. Start the frontend

```bash
pnpm dev
```

Open [http://localhost:3000](http://localhost:3000)

---

## 4. Running both together

Open two terminals:

**Terminal 1 — Backend**
```bash
cd jai-v2
python agent.py dev
```

**Terminal 2 — Frontend**
```bash
cd jai
pnpm dev
```

Then visit `http://localhost:3000`, click **Connect**, and talk to Jai.

---

## Stack

| Layer | Technology |
|-------|-----------|
| STT | Groq `whisper-large-v3` |
| LLM | Groq `llama-3.3-70b-versatile` |
| TTS | ElevenLabs |
| VAD | Silero |
| Transport | LiveKit WebRTC |
| RAG | FAISS + `all-MiniLM-L6-v2` |
| Frontend | Next.js 15 + LiveKit React |
