import logging
import os
from dotenv import load_dotenv
from livekit.agents import AutoSubscribe, JobContext, JobProcess, WorkerOptions, cli
from livekit.agents.voice import Agent, AgentSession
from livekit.plugins import silero, elevenlabs
from livekit.plugins.openai import STT, LLM

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


def make_jai_agent(query: str = "") -> Agent:
    if query:
        try:
            from rag import retrieve
            context = retrieve(query)
            instructions = f"{BASE_INSTRUCTIONS}\n\nCONTEXT:\n{context}"
        except Exception as e:
            logger.warning(f"RAG retrieval failed: {e}")
            instructions = BASE_INSTRUCTIONS
    else:
        instructions = BASE_INSTRUCTIONS

    return Agent(instructions=instructions)


async def entrypoint(ctx: JobContext):
    logger.info(f"connecting to room {ctx.room.name}")
    await ctx.connect(auto_subscribe=AutoSubscribe.AUDIO_ONLY)

    session = AgentSession(
        vad=ctx.proc.userdata["vad"],
        stt=STT(model="whisper-large-v3", base_url="https://api.groq.com/openai/v1", api_key=os.environ["GROQ_API_KEY"]),
        llm=LLM(model="llama-3.3-70b-versatile", base_url="https://api.groq.com/openai/v1", api_key=os.environ["GROQ_API_KEY"]),
        tts=elevenlabs.TTS(),
    )

    async def before_llm_cb(agent: Agent, chat_ctx):
        # Get last user message to use as RAG query
        user_messages = [m for m in chat_ctx.messages if m.role == "user"]
        if user_messages:
            query = str(user_messages[-1].content)
            try:
                from rag import retrieve
                context = retrieve(query)
                # Inject context into system instructions
                agent._instructions = f"{BASE_INSTRUCTIONS}\n\nCONTEXT:\n{context}"
            except Exception as e:
                logger.warning(f"RAG retrieval failed: {e}")

    await session.start(
        agent=Agent(instructions=BASE_INSTRUCTIONS),
        room=ctx.room,
    )

    await session.say(
        "Hi! I'm Jai, your Jaro Education AI assistant. How can I help you with your course or career today?",
        allow_interruptions=True,
    )


if __name__ == "__main__":
    cli.run_app(WorkerOptions(entrypoint_fnc=entrypoint, prewarm_fnc=prewarm, agent_name="jai"))
