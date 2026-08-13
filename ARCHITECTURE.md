# Jai — AI Voice Assistant Architecture

Jai is a real-time AI voice assistant for Jaro Education, built on LiveKit Agents. It has two parts: a **Python backend agent** and a **Next.js frontend**.

---

## Project Structure

```
AI/
├── jai/          # Next.js frontend
└── jai-v2/       # Python voice agent backend
    ├── scraper.py
    ├── rag.py
    ├── agent.py
    └── requirements.txt
```

---

## Data Pipeline (run once, offline)

These scripts are run once to build the knowledge base before starting the agent.

| File | Tools | Task |
|------|-------|------|
| `scraper.py` | `requests`, `BeautifulSoup` | Crawls up to 60 pages of jaroeducation.com, extracts and chunks text (~400 words/chunk), saves to `jaro_chunks.json` |
| `rag.py` | `sentence-transformers`, `FAISS` | Embeds chunks using `all-MiniLM-L6-v2` (local, no API key), builds a FAISS vector index, saves `jaro_index.faiss` + `jaro_chunks_indexed.json` |

### Setup Order

```bash
python scraper.py   # step 1 — scrape website
python rag.py       # step 2 — build vector index
python agent.py     # step 3 — start the voice agent
```

---

## Voice Agent Backend (`agent.py`)

Each component handles one stage of the voice pipeline.

| Component | Service | Task |
|-----------|---------|------|
| VAD | Silero | Detects when the user starts/stops speaking |
| STT | Groq — Whisper large-v3 | Converts user speech → text |
| RAG | FAISS + sentence-transformers | On each user turn, retrieves top-4 relevant Jaro Education content chunks and injects them as context into the prompt |
| LLM | Groq — LLaMA 3.3 70B | Generates a response using the user query + RAG context |
| TTS | ElevenLabs | Converts the LLM text response → natural-sounding speech |
| Orchestration | LiveKit Agents | Manages the real-time audio session, agent lifecycle, and room connection |

---

## Frontend (`jai/`)

| File/Folder | Service | Task |
|-------------|---------|------|
| `app/api/token/route.ts` | `livekit-server-sdk` | Generates a short-lived JWT (15 min) for the user to join a LiveKit room |
| `components/agents-ui/` | LiveKit React SDK | Audio visualizers, chat transcript, mic/speaker controls |
| `app/page.tsx` | Next.js | Main UI — connects the browser to the LiveKit room where the agent is running |

---

## End-to-End Data Flow

```
User speaks
  → LiveKit room captures audio
  → Silero VAD detects speech boundaries
  → Groq Whisper transcribes speech → text
  → FAISS retrieves relevant Jaro Education content
  → Groq LLaMA 3.3 70B generates a response
  → ElevenLabs converts response → speech
  → Audio streamed back to user via LiveKit
```

---

## Environment Variables

| Variable | Used By | Purpose |
|----------|---------|---------|
| `GROQ_API_KEY` | `agent.py` | Auth for Groq STT (Whisper) and LLM (LLaMA) |
| `ELEVEN_API_KEY` | `agent.py` | Auth for ElevenLabs TTS |
| `LIVEKIT_URL` | `agent.py`, `jai/` | LiveKit server WebSocket URL |
| `LIVEKIT_API_KEY` | `jai/` | LiveKit token generation |
| `LIVEKIT_API_SECRET` | `jai/` | LiveKit token signing |

---

## Key Design Decisions

- **Groq for STT + LLM** — used for both Whisper and LLaMA to keep latency low (Groq runs on LPU hardware)
- **Local embeddings** — `all-MiniLM-L6-v2` runs locally via `sentence-transformers`, no API cost for RAG
- **FAISS** — lightweight local vector store, no external database needed
- **ElevenLabs TTS** — high-quality natural voice output (requires paid API key; free tier available)
- **RAG injection** — context is injected per-turn in `on_user_turn_completed`, keeping the base system prompt clean
