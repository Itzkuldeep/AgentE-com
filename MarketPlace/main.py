# import json
# import logging
# import os
# from typing import Any, Awaitable, Callable, Optional

# import aiofiles
# import yaml
# from autogen_agentchat.agents import AssistantAgent, UserProxyAgent
# from autogen_agentchat.base import TaskResult
# from autogen_agentchat.messages import TextMessage, UserInputRequestedEvent
# from autogen_agentchat.teams import RoundRobinGroupChat
# from autogen_core import CancellationToken
# from autogen_core.models import ChatCompletionClient
# from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
# from fastapi.middleware.cors import CORSMiddleware
# from fastapi.responses import FileResponse
# from fastapi.staticfiles import StaticFiles

# # Import agents from call_agent.py
# from agents import (
#     CallAgent,
#     MeetAgent,
#     Mailgetter,
#     RAGAgent,
#     SchedulerAgent,
#     EmailSenderAgent,
#     ConversationAgent,
#     UserProxyAgent as CustomUserProxyAgent,
#     llm_config
# )

# logger = logging.getLogger(__name__)

# app = FastAPI()

# # Add CORS middleware
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# model_config_path = "model_config.yaml"
# state_path = "team_state.json"
# history_path = "team_history.json"

# # Serve static files
# app.mount("/static", StaticFiles(directory="."), name="static")

# @app.get("/")
# async def root():
#     """Serve the chat interface HTML file."""
#     return FileResponse("app.html")

# async def get_team(
#     user_input_func: Callable[[str, Optional[CancellationToken]], Awaitable[str]],
# ):
#     # Get model client from config
#     async with aiofiles.open(model_config_path, "r") as file:
#         model_config = yaml.safe_load(await file.read())
#     model_client = ChatCompletionClient.load_component(model_config)

#     # Create agents with WebSocket input function
#     user_proxy = CustomUserProxyAgent(
#         name="UserAgent",
#         llm_config=llm_config,  # Import from call_agent or redefine
#         input_func=user_input_func,
#         code_execution_config=False,
#         human_input_mode="NEVER"
#     )
    
#     # Create team with all agents
#     team = RoundRobinGroupChat(
#         agents=[
#             CallAgent, 
#             MeetAgent, 
#             Mailgetter, 
#             RAGAgent,
#             SchedulerAgent,
#             EmailSenderAgent,
#             ConversationAgent,
#             user_proxy
#         ]
#     )

#     # Load state if exists
#     if os.path.exists(state_path):
#         async with aiofiles.open(state_path, "r") as file:
#             state = json.loads(await file.read())
#         await team.load_state(state)

#     return team

# async def get_history() -> list[dict[str, Any]]:
#     """Get chat history from file."""
#     if not os.path.exists(history_path):
#         return []
#     async with aiofiles.open(history_path, "r") as file:
#         return json.loads(await file.read())

# @app.get("/history")
# async def history() -> list[dict[str, Any]]:
#     try:
#         return await get_history()
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e)) from e

# @app.websocket("/ws/chat")
# async def chat(websocket: WebSocket):
#     await websocket.accept()

#     # User input function used by the team
#     async def _user_input(prompt: str, cancellation_token: CancellationToken | None) -> str:
#         data = await websocket.receive_json()
#         message = TextMessage.model_validate(data)
#         return message.content

#     try:
#         while True:
#             # Get user message
#             data = await websocket.receive_json()
#             request = TextMessage.model_validate(data)

#             try:
#                 # Get the team and respond to the message
#                 team = await get_team(_user_input)
#                 history = await get_history()
#                 stream = team.run_stream(task=request)  # Use run_stream instead of aask_stream

#                 async for message in stream:
#                     if isinstance(message, TaskResult):
#                         continue
#                     await websocket.send_json(message.model_dump())
#                     if not isinstance(message, UserInputRequestedEvent):
#                         history.append(message.model_dump())

#                 # Save team state and history
#                 async with aiofiles.open(state_path, "w") as file:
#                     state = await team.save_state()
#                     await file.write(json.dumps(state))
#                 async with aiofiles.open(history_path, "w") as file:
#                     await file.write(json.dumps(history))
                    
#             except Exception as e:
#                 # Error handling remains the same
#                 ...
                
#     except WebSocketDisconnect:
#         logger.info("Client disconnected")
#     except Exception as e:
#         logger.error(f"Unexpected error: {str(e)}")
#         # Error handling remains the same

# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run(app, host="0.0.0.0", port=8002)


import json
import logging
import os
from typing import Any, Awaitable, Callable, Optional

import aiofiles
import yaml
from autogen_agentchat.agents import AssistantAgent, UserProxyAgent
from autogen_agentchat.base import TaskResult
from autogen_agentchat.messages import TextMessage, UserInputRequestedEvent
from autogen_agentchat.teams import RoundRobinGroupChat
from autogen_core import CancellationToken
from autogen_core.models import ChatCompletionClient
from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from agents import (
    CallAgent,
    MeetAgent,
    Mailgetter,
    RAGAgent,
    SchedulerAgent,
    EmailSenderAgent,
    ConversationAgent,
    UserProxyAgent as CustomUserProxyAgent,
    llm_config  # Import LLM config to use for user proxy
)

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

model_config_path = "model_config.yaml"
state_path = "team_state.json"
history_path = "team_history.json"

app.mount("/static", StaticFiles(directory="."), name="static")

@app.get("/")
async def root():
    return FileResponse("app.html")

async def get_team(
    user_input_func: Callable[[str, Optional[CancellationToken]], Awaitable[str]],
):
    logger.info("Creating agent team...")
    # Get model client from config (not used currently, since agents are predefined)
    if os.path.exists(model_config_path):
        async with aiofiles.open(model_config_path, "r") as file:
            model_config = yaml.safe_load(await file.read())
        model_client = ChatCompletionClient.load_component(model_config)
        logger.info("Loaded model config.")
    else:
        logger.warning("model_config.yaml not found. Skipping model client setup.")

    user_proxy = CustomUserProxyAgent(
        name="UserAgent",
        llm_config=llm_config,
        code_execution_config=False,
        human_input_mode="ALWAYS"  # or "TERMINATE" or "DEFAULT"
    )

    logger.info("User proxy agent created.")

# Assuming llm_config is defined/imported

    call_agent = CallAgent(name="CallAgent", llm_config=llm_config)
    meet_agent = MeetAgent(name="MeetAgent", llm_config=llm_config)
    mailgetter = Mailgetter(name="Mailgetter", llm_config=llm_config)
    rag_agent = RAGAgent(name="RAGAgent", llm_config=llm_config)
    scheduler_agent = SchedulerAgent(name="SchedulerAgent", llm_config=llm_config)
    email_sender_agent = EmailSenderAgent(name="EmailSenderAgent", llm_config=llm_config)
    conversation_agent = ConversationAgent(name="ConversationAgent", llm_config=llm_config)
    user_proxy = CustomUserProxyAgent(
        name="UserAgent",
        llm_config=llm_config,
        human_input_mode="ALWAYS"
    )

    team = RoundRobinGroupChat(
        [
            call_agent,
            meet_agent,
            mailgetter,
            rag_agent,
            scheduler_agent,
            email_sender_agent,
            conversation_agent,
            user_proxy
        ]
    )

    logger.info("Team assembled.")

    # Load previous state if available
    if os.path.exists(state_path):
        async with aiofiles.open(state_path, "r") as file:
            content = await file.read()
            if content.strip():
                state = json.loads(content)
                await team.load_state(state)
                logger.info("Team state loaded from file.")
            else:
                logger.warning("State file was empty. Skipping load.")
    else:
        logger.info("No team state file found. Starting fresh.")

    return team

async def get_history() -> list[dict[str, Any]]:
    if not os.path.exists(history_path):
        logger.info("No history file found. Returning empty history.")
        return []
    async with aiofiles.open(history_path, "r") as file:
        content = await file.read()
        if content.strip():
            logger.info("History file loaded.")
            return json.loads(content)
        else:
            logger.warning("History file was empty.")
            return []

@app.get("/history")
async def history() -> list[dict[str, Any]]:
    try:
        return await get_history()
    except Exception as e:
        logger.error(f"Failed to load history: {e}")
        raise HTTPException(status_code=500, detail=str(e)) from e

@app.websocket("/ws/chat")
async def chat(websocket: WebSocket):
    await websocket.accept()
    logger.info("Client connected to WebSocket.")

    async def _user_input(prompt: str, cancellation_token: CancellationToken | None) -> str:
        logger.info(f"Prompt to user: {prompt}")
        data = await websocket.receive_json()
        message = TextMessage.model_validate(data)
        logger.info(f"User replied: {message.content}")
        return message.content

    try:
        while True:
            data = await websocket.receive_json()
            request = TextMessage.model_validate(data)
            logger.info(f"Received user message: {request.content}")

            try:
                team = await get_team(_user_input)
                history = await get_history()
                logger.info("Starting agent response stream...")

                stream = team.run_stream(task=request)

                async for message in stream:
                    if isinstance(message, TaskResult):
                        logger.debug("TaskResult skipped.")
                        continue

                    logger.info(f"Agent [{message.source}]: {message.content}")
                    await websocket.send_json(message.model_dump())

                    if not isinstance(message, UserInputRequestedEvent):
                        history.append(message.model_dump())

                # Save team state
                state = await team.save_state()
                async with aiofiles.open(state_path, "w") as file:
                    await file.write(json.dumps(state))
                    logger.info("Saved team state.")

                # Save chat history
                async with aiofiles.open(history_path, "w") as file:
                    await file.write(json.dumps(history))
                    logger.info("Saved chat history.")

            except Exception as e:
                logger.exception("Error during agent response handling.")
                await websocket.send_json({
                    "type": "error",
                    "content": f"Error: {str(e)}",
                    "source": "system"
                })
                await websocket.send_json({
                    "type": "UserInputRequestedEvent",
                    "content": "An error occurred. Please try again.",
                    "source": "system"
                })

    except WebSocketDisconnect:
        logger.info("Client disconnected")
    except Exception as e:
        logger.exception(f"Unexpected WebSocket error: {str(e)}")
        try:
            await websocket.send_json({
                "type": "error",
                "content": f"Unexpected error: {str(e)}",
                "source": "system"
            })
        except:
            pass

if __name__ == "__main__":
    import uvicorn
    logger.info("Starting FastAPI server on http://0.0.0.0:8002")
    uvicorn.run(app, host="0.0.0.0", port=8002)
