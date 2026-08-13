import logging
import os
from dotenv import load_dotenv
from livekit.agents import JobContext, JobProcess, WorkerOptions, cli
from livekit.agents.voice import Agent, AgentSession
from livekit.plugins import silero, elevenlabs
from livekit.plugins.openai import STT, LLM
from livekit.agents import llm

load_dotenv(dotenv_path=".env.local")

logger = logging.getLogger("voice-agent")
logging.basicConfig(level=logging.INFO)

BASE_INSTRUCTIONS = (
    "You are Jai, an AI voice assistant for Jaro Education. "
    "You help students with course selection, career guidance, and educational planning. "
    "Use the CONTEXT section below (scraped from jaroeducation.com) to answer accurately. "
    "If the context doesn't cover the question, answer from general knowledge but stay relevant to education. "
    "Keep responses short, friendly, and conversational."
)


def prewarm(proc: JobProcess):
    proc.userdata["vad"] = silero.VAD.load()


class JaiAgent(Agent):
    def __init__(self):
        super().__init__(instructions=BASE_INSTRUCTIONS)

    async def on_user_turn_completed(self, turn_ctx: llm.ChatContext, new_message: llm.ChatMessage) -> None:
        query = new_message.text_content
        if query:
            try:
                from rag import retrieve
                context = retrieve(query)
                new_message.content = [f"{query}\n\nCONTEXT:\n{context}"]
            except Exception as e:
                logger.warning(f"RAG retrieval failed: {e}")


async def entrypoint(ctx: JobContext):
    logger.info(f"connecting to room {ctx.room.name}")

    session = AgentSession(
        vad=ctx.proc.userdata["vad"],
        stt=STT(model="whisper-large-v3", base_url="https://api.groq.com/openai/v1", api_key=os.environ["GROQ_API_KEY"]),
        llm=LLM(model="llama-3.3-70b-versatile", base_url="https://api.groq.com/openai/v1", api_key=os.environ["GROQ_API_KEY"]),
        tts=elevenlabs.TTS(),
    )

    await session.start(
        agent=JaiAgent(),
        room=ctx.room,
    )

    await session.say(
        "Hi! I'm Jai, your Jaro Education AI assistant. How can I help you with your course or career today?",
        allow_interruptions=True,
    )


if __name__ == "__main__":
    cli.run_app(WorkerOptions(entrypoint_fnc=entrypoint, prewarm_fnc=prewarm, agent_name="jai"))
