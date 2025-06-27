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
from agents import today

logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

model_config_path = "model_config.yaml"
state_path = "team_state.json"
history_path = "team_history.json"

# Serve static files
app.mount("/static", StaticFiles(directory="."), name="static")

@app.get("/")
async def root():
    """Serve the chat interface HTML file."""
    logger.info("Serving app.html at root endpoint")
    return FileResponse("app.html")


async def get_team(
    user_input_func: Callable[[str, Optional[CancellationToken]], Awaitable[str]],
) -> RoundRobinGroupChat:
    logger.info("Loading model configuration from %s", model_config_path)
    async with aiofiles.open(model_config_path, "r") as file:
        model_config = yaml.safe_load(await file.read())
    logger.info("Model configuration loaded successfully")
    model_client = ChatCompletionClient.load_component(model_config)
    logger.info("Model client initialized")

    # Create the team.
    logger.info("Initializing agents")
    CallAgent = AssistantAgent(
        name="CallAgent",
        model_client=model_client,
        system_message=f"You are a call assistant. When user provides a phone number, call it using the 'request_call' tool. and after that, tell user that the call is in progress and they will be contacted shortly, and in the End of answers say THANKS.",
    )

    MeetAgent = AssistantAgent(
        name="MeetAgent",
        model_client=model_client,
        system_message="You are a Meeting Assistant. when user provides you a meet link with bot name, join the meet using the 'join_meeting' tool."
    )

    Mailgetter = AssistantAgent(
        name="Mailgetter",
        model_client=model_client,
        system_message=f"You are a Email fetcher, when user provides you his user name and password, fetch his latest 5 emails, using the 'fetch_latest_email' tool."
    )

    RAGAgent = AssistantAgent(
        name="RAGAgent",
        model_client=model_client,
        system_message=f"You are a Retrieval-Augmented Generation (RAG) agent. Given a file path and a question, use the document content to answer the question."
    )

    SchedulerAgent = AssistantAgent(
        name="SchedulerAgent",
        model_client=model_client,
        system_message=f"""You are a smart scheduling assistant. Today is 27-06-2025. When the user provides a start time, participant emails, and duration, schedule a meeting using the 'schedule_meeting' tool.""")

    ConversationAgent = AssistantAgent(
        name="ConversationAgent",
        model_client=model_client,
        system_message=f"""
    You are a smart and helpful AI personal assistant that can:
    - Uses past memory provided in the user message (e.g., summaries, past messages).
    - Chat naturally with the user and answer general questions.
    - Understand when the user needs a specific task done (e.g., calling someone, joining a meeting, checking email, or answering document-based questions).
    - Route these tasks to the appropriate agents: CallAgent, MeetAgent, Mailgetter, or RAGAgent.
    - Respond clearly and concisely, and always be polite and friendly.


    When a task is completed or a response is finished, end your message with a polite phrase that includes the word "Thanks!" or "Thank you!" so the system knows the conversation is done.

    📌 Examples of good endings:
    - "Let me know if you'd like help with anything else. Thanks!"
    - "That's all done. Feel free to ask more. Thanks!"
    - "I've completed that task. If you need anything else, just ask. Thanks!"

    This helps the system stop at the right time. So be sure to end each response with a version of "thanks".

    Be engaging but efficient. You're the user's intelligent assistant—both smart and warm.
    """
    )

    EmailSenderAgent = AssistantAgent(
        name="EmailSenderAgent",
        model_client=model_client,
        system_message=f"""You are a professional email assistant.
    Your job is to help the user send emails based on their message input.

    When the user gives a natural language prompt such as:
    - "Send an email to abc@example.com asking if they're free for a meeting tomorrow"
    - "Mail xyz@gmail.com and say happy birthday"
    - "Inform the team about today's cricket match"

    Use the 'smart_email_sender' tool to:
    1. Extract recipient email addresses from the input.
    2. Understand the message and generate a professional subject and body.
    3. Format it as a complete email with a proper closing like 'Regards, Ajay'.
    Only use 'smart_email_sender' to perform the task. Do not write the email yourself.
    End responses with: "Happy to help further. Just ask! Thanks!
    """
    )
    team = RoundRobinGroupChat(
        [CallAgent, EmailSenderAgent, ConversationAgent, SchedulerAgent, RAGAgent, Mailgetter, MeetAgent],
    )
    logger.info("Agents initialized and team created")

    # Load state from file.
    if not os.path.exists(state_path):
        logger.info("No existing team state found at %s", state_path)
        return team
    logger.info("Loading team state from %s", state_path)
    async with aiofiles.open(state_path, "r") as file:
        state = json.loads(await file.read())
    await team.load_state(state)
    logger.info("Team state loaded successfully")
    return team


# async def get_history() -> list[dict[str, Any]]:
#     """Get chat history from file."""
#     if not os.path.exists(history_path):
#         logger.info("No chat history found at %s", history_path)
#         return []
#     logger.info("Loading chat history from %s", history_path)
#     async with aiofiles.open(history_path, "r") as file:
#         history = json.loads(await file.read())
#     logger.info("Chat history loaded successfully")
#     return history


# @app.get("/history")
# async def history() -> list[dict[str, Any]]:
#     try:
#         logger.info("GET /history called")
#         return await get_history()
#     except Exception as e:
#         logger.error("Error getting history: %s", str(e))
#         raise HTTPException(status_code=500, detail=str(e)) from e


# @app.websocket("/ws/chat")
# async def chat(websocket: WebSocket):
#     logger.info("WebSocket connection accepted")
#     await websocket.accept()

#     # User input function used by the team.
#     async def _user_input(prompt: str, cancellation_token: CancellationToken | None) -> str:
#         logger.info("Waiting for user input via WebSocket")
#         data = await websocket.receive_json()
#         message = TextMessage.model_validate(data)
#         logger.info("Received user input: %s", message.content)
#         return message.content

#     try:
#         while True:
#             # Get user message.
#             logger.info("Waiting for user message via WebSocket")
#             data = await websocket.receive_json()
#             request = TextMessage.model_validate(data)
#             logger.info("Received user message: %s", request.content)

#             try:
#                 # Get the team and respond to the message.
#                 logger.info("Getting team and chat history")
#                 team = await get_team(_user_input)
#                 history = await get_history()
#                 logger.info("Starting team.run_stream for request")
#                 stream = team.run_stream(task=request)
#                 async for message in stream:
#                     if isinstance(message, TaskResult):
#                         logger.info("Received TaskResult, skipping")
#                         continue
#                     logger.info("Sending message to WebSocket: %s", message.model_dump())
#                     await websocket.send_json(message.model_dump())
#                     if not isinstance(message, UserInputRequestedEvent):
#                         # Don't save user input events to history.
#                         history.append(message.model_dump())

#                 # Save team state to file.
#                 logger.info("Saving team state to %s", state_path)
#                 async with aiofiles.open(state_path, "w") as file:
#                     state = await team.save_state()
#                     await file.write(json.dumps(state))

#                 # Save chat history to file.
#                 logger.info("Saving chat history to %s", history_path)
#                 async with aiofiles.open(history_path, "w") as file:
#                     await file.write(json.dumps(history))
                    
#             except Exception as e:
#                 logger.error("Error during chat handling: %s", str(e))
#                 # Send error message to client
#                 error_message = {
#                     "type": "error",
#                     "content": f"Error: {str(e)}",
#                     "source": "system"
#                 }
#                 await websocket.send_json(error_message)
#                 # Re-enable input after error
#                 await websocket.send_json({
#                     "type": "UserInputRequestedEvent",
#                     "content": "An error occurred. Please try again.",
#                     "source": "system"
#                 })
                
#     except WebSocketDisconnect:
#         logger.info("Client disconnected")
#     except Exception as e:
#         logger.error(f"Unexpected error: {str(e)}")
#         try:
#             await websocket.send_json({
#                 "type": "error",
#                 "content": f"Unexpected error: {str(e)}",
#                 "source": "system"
#             })
#         except Exception as send_err:
#             logger.error("Failed to send error message via WebSocket: %s", str(send_err))


# # Example usage
# if __name__ == "__main__":
#     import uvicorn

#     logger.info("Starting FastAPI app with Uvicorn on 0.0.0.0:8002")
#     uvicorn.run(app, host="0.0.0.0", port=8002)

async def get_history() -> list[dict[str, Any]]:
    """Get chat history from file."""
    if not os.path.exists(history_path):
        return []
    async with aiofiles.open(history_path, "r") as file:
        return json.loads(await file.read())


@app.get("/history")
async def history() -> list[dict[str, Any]]:
    try:
        return await get_history()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@app.websocket("/ws/chat")
async def chat(websocket: WebSocket):
    await websocket.accept()

    # User input function used by the team.
    async def _user_input(prompt: str, cancellation_token: CancellationToken | None) -> str:
        data = await websocket.receive_json()
        message = TextMessage.model_validate(data)
        return message.content

    try:
        while True:
            # Get user message.
            data = await websocket.receive_json()
            request = TextMessage.model_validate(data)

            try:
                # Get the team and respond to the message.
                team = await get_team(_user_input)
                history = await get_history()
                stream = team.run_stream(task=request)
                async for message in stream:
                    if isinstance(message, TaskResult):
                        continue
                    await websocket.send_json(message.model_dump())
                    if not isinstance(message, UserInputRequestedEvent):
                        # Don't save user input events to history.
                        history.append(message.model_dump())

                # Save team state to file.
                async with aiofiles.open(state_path, "w") as file:
                    state = await team.save_state()
                    await file.write(json.dumps(state))

                # Save chat history to file.
                async with aiofiles.open(history_path, "w") as file:
                    await file.write(json.dumps(history))
                    
            except Exception as e:
                # Send error message to client
                error_message = {
                    "type": "error",
                    "content": f"Error: {str(e)}",
                    "source": "system"
                }
                await websocket.send_json(error_message)
                # Re-enable input after error
                await websocket.send_json({
                    "type": "UserInputRequestedEvent",
                    "content": "An error occurred. Please try again.",
                    "source": "system"
                })
                
    except WebSocketDisconnect:
        logger.info("Client disconnected")
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        try:
            await websocket.send_json({
                "type": "error",
                "content": f"Unexpected error: {str(e)}",
                "source": "system"
            })
        except:
            pass


# Example usage
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8002)