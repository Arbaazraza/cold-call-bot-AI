import asyncio
import os
import sys
import json

from dotenv import load_dotenv
from loguru import logger

from pipecat.audio.vad.silero import SileroVADAnalyzer
from pipecat.audio.vad.vad_analyzer import VADParams
from pipecat.transports.local.audio import LocalAudioTransport, LocalAudioTransportParams
from pipecat.pipeline.pipeline import Pipeline
from pipecat.pipeline.runner import PipelineRunner
from pipecat.pipeline.task import PipelineParams, PipelineTask
from pipecat.services.deepgram import DeepgramSTTService, DeepgramTTSService
from pipecat.services.openai import OpenAILLMService
from pipecat.processors.aggregators.openai_llm_context import OpenAILLMContext
from pipecat.frames.frames import LLMRunFrame

load_dotenv(override=True)

logger.remove(0)
logger.add(sys.stderr, level="INFO")

async def main():
    # 1. AUDIO: Safe Mode (16kHz) 
    transport = LocalAudioTransport(
        params=LocalAudioTransportParams(
            audio_out_enabled=True,
            audio_in_enabled=True,
            audio_out_sample_rate=16000, 
            audio_out_channels=1,
            audio_in_sample_rate=16000,
            audio_in_channels=1,
            vad_enabled=True,
            vad_analyzer=SileroVADAnalyzer(params=VADParams(
                min_volume=0.1, 
                stop_secs=0.8
            ))
        )
    )

    stt = DeepgramSTTService(api_key=os.getenv("DEEPGRAM_API_KEY"))
    # Match sample rate to Transport to prevent stutter
    tts = DeepgramTTSService(api_key=os.getenv("DEEPGRAM_API_KEY"), voice="aura-helios-en", sample_rate=16000)
    
    # 2. INTELLIGENCE: 70B Model for high-level reasoning
    llm = OpenAILLMService(
        api_key=os.getenv("GROQ_API_KEY"),
        base_url="https://api.groq.com/openai/v1",
        model="llama-3.3-70b-versatile"
    )

    tools = [
        {
            "type": "function",
            "function": {
                "name": "record_call_outcome",
                "description": "Call this ONLY when the negotiation is finished (Meeting Booked OR Hard Rejection).",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "qualified": {"type": "boolean"},
                        "reasoning": {"type": "string"},
                        "next_step": {"type": "string", "enum": ["book_demo", "follow_up", "disregard"]}
                    },
                    "required": ["qualified", "reasoning", "next_step"]
                }
            }
        }
    ]

    # 3. THE "CONTEXT-AWARE" PROMPT (No Linear Steps)
    messages = [
        {
            "role": "system",
            "content": """You are Alex, a savvy Account Executive at CloudSave.
            
            YOUR MISSION:
            Identify if the user is a good fit for our cloud optimization service (AWS/Azure > $1k spend) and convince them to take a 15-minute demo.
            
            INTELLIGENCE INSTRUCTIONS:
            - **Do not follow a script.** Listen to what the user says.
            - **Information Gaps:** You need to know which Cloud they use and how much they spend. If the user volunteers this info early, do NOT ask for it again.
            - **The "Human" Element:** When you hear a high spend number, you must react naturally (e.g., "Wow, that's a lot") before pivoting to your solution.
            - **Objection Handling:** If they are busy, respect it but try to squeeze in a "callback" request.
            
            TOOL CALLING RULES (The Guardrails):
            1. You generally cannot book a meeting until you have proposed the value (saving 30%).
            2. **DO NOT call 'record_call_outcome'** until the user has given a clear Verbal Yes or Verbal No to the next step.
            
            Start casually: 'Hi, is this the business owner?'"""
        },
    ]

    context = OpenAILLMContext(messages, tools=tools)
    context_aggregator = llm.create_context_aggregator(context)

    pipeline = Pipeline([
        transport.input(),   
        stt,                 
        context_aggregator.user(), 
        llm,                 
        tts,                 
        transport.output(),  
        context_aggregator.assistant() 
    ])

    task = PipelineTask(
        pipeline, 
        params=PipelineParams(
            allow_interruptions=True,
            idle_timeout_secs=60 
        )
    )

    async def record_outcome(function_name, tool_call_id, args, llm, context, result_callback):
        print(f"\n🎯 OUTCOME GENERATED: {args}\n")
        with open("outcome.json", "w") as f:
            json.dump(args, f, indent=2)

        if args['qualified']:
            await result_callback("Outcome saved. Say: 'Awesome, invite sent. Thanks!' and hang up.")
        else:
            await result_callback("Outcome saved. Say: 'Understood, thanks anyway.' and hang up.")
        
        await asyncio.sleep(5) 
        os._exit(0)

    llm.register_function("record_call_outcome", record_outcome)

    async def start_call():
        await asyncio.sleep(2)
        print(">> Triggering First Message...")
        await task.queue_frames([LLMRunFrame()])

    asyncio.create_task(start_call())
    
    runner = PipelineRunner(handle_sigint=True)
    
    try:
        await runner.run(task)
    except Exception as e:
        print(f"Error: {e}")
    finally:
        print("Call ended.")
        os._exit(0)

if __name__ == "__main__":
    asyncio.run(main())