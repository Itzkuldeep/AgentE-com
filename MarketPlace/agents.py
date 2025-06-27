# call_agent.py
import os
from autogen import GroupChat, GroupChatManager
from autogen import AssistantAgent, UserProxyAgent
from tools import *
from datetime import datetime
# from redis import get_memory_block
from dotenv import load_dotenv
load_dotenv()

today = datetime.now().strftime('%B %d, %Y')


# hist = get_memory_block("session1")
# print(hist)

function_schema_rag = {
    "name": "load_and_query_rag_doc",
    "description": "Answer a question using the provided text file as knowledge base",
    "parameters": {
        "type": "object",
        "properties": {
            "file_path": {
                "type": "string",
                "description": "Path to the file to use for RAG"
            },
            "query": {
                "type": "string",
                "description": "User's question to be answered from the document"
            }
        },
        "required": ["file_path", "query"]
    }
}

function_schema_call = {
    "name": "request_call",
    "description": "Place a phone call to a given number.",
    "parameters": {
        "type": "object",
        "properties": {
            "phone_number": {
                "type": "string",
                "description": "The phone number to call in international format"
            }
        },
        "required": ["phone_number"]
    }
}

function_schema_meeting = {
    "name": "join_meeting",
    "description": "Join a Google Meet meeting with a bot.",
    "parameters": {
        "type": "object",
        "properties": {
            "meeting_url": {
                "type": "string",
                "description": "The URL of the Google Meet to join"
            },
            "bot_name": {
                "type": "string",
                "description": "Name of the bot to introduce in the meeting"
            }
        },
        "required": ["meeting_url", "bot_name"]
    }
}

function_schema_email = {
    "name": "fetch_latest_email",
    "description": "Fetch the latest email from a Gmail inbox using IMAP.",
    "parameters": {
        "type": "object",
        "properties": {
            "username": {
                "type": "string",
                "description": "Gmail address to fetch emails from"
            },
            "password": {
                "type": "string",
                "description": "App password or login password (App password recommended)"
            }
        },
        "required": ["username", "password"]
    }
}

function_schema_schedule_meeting = {
    "name": "schedule_meeting",
    "description": "Schedule a meeting on Google Calendar with given emails.",
    "parameters": {
        "type": "object",
        "properties": {
            "start_time": {"type": "string", "description": "Meeting start time in ISO format."},
            "emails": {"type": "string", "description": "Participant emails."},
            "duration_minutes": {"type": "integer", "description": "Duration in minutes."},
            "summary": {"type": "string", "description": "Meeting summary/title."}
        },
        "required": ["start_time", "emails"]
    }
}


function_schema_email_send = {
    "name": "smart_email_sender",
    "description": "Send a professionally formatted email with AI-generated subject and closing from natural text.",
    "parameters": {
        "type": "object",
        "properties": {
            "recipients": {
                "type": "array",
                "items": {"type": "string"},
                "description": "List of email addresses to send the email to"
            },
            "message": {
                "type": "string",
                "description": "The natural language message content (e.g., 'Ask if they are available for cricket today')"
            },
            "sender_name": {
                "type": "string",
                "description": "Name to be used in 'Regards, {name}'",
                "default": "Ajay Singh"
            }
        },
        "required": ["recipients", "message"]
    }
}


# ------------------ LLM Config ------------------
OPENAI_API = os.getenv("OPENAI_API_KEY")

llm_config = {
    "config_list": [
        {
            "model": "gpt-4o-mini", 
            "api_key": OPENAI_API,
            "api_type": "openai"
        }
    ],
    "tools": [
        {"type": "function", "function": function_schema_call},
        {"type": "function", "function": function_schema_meeting},
        {"type": "function", "function": function_schema_email},
        {"type": "function", "function": function_schema_rag},
        {"type": "function", "function": function_schema_email_send}
    ]
}

llm_config_manager = {
    "config_list": [
        {
            "model": "gpt-4o-mini", 
            "api_key": OPENAI_API,
            "api_type": "openai"
        }
    ]
}
# ------------------ Agent Setup ------------------
# Setup the agent
CallAgent = AssistantAgent(
    name="CallAgent",
    llm_config=llm_config,
    is_termination_msg=lambda msg: "thanks" in msg["content"].lower(),
    system_message=f"You are a call assistant. When user provides a phone number, call it using the 'request_call' tool. and after that, tell user that the call is in progress and they will be contacted shortly, and in the End of answers say THANKS.",
)

MeetAgent = AssistantAgent(
    name="MeetAgent",
    llm_config=llm_config,
    is_termination_msg=lambda msg: "thanks" in msg["content"].lower(),
    system_message="You are a Meeting Assistant. when user provides you a meet link with bot name, join the meet using the 'join_meeting' tool."
)

Mailgetter = AssistantAgent(
    name="Mailgetter",
    llm_config=llm_config,
    is_termination_msg=lambda msg: "thanks" in msg["content"].lower(),
    system_message=f"You are a Email fetcher, when user provides you his user name and password, fetch his latest 5 emails, using the 'fetch_latest_email' tool."
)

RAGAgent = AssistantAgent(
    name="RAGAgent",
    llm_config=llm_config,
    is_termination_msg=lambda msg: "thanks" in msg["content"].lower(),
    system_message=f"You are a Retrieval-Augmented Generation (RAG) agent. Given a file path and a question, use the document content to answer the question."
)

SchedulerAgent = AssistantAgent(
    name="SchedulerAgent",
    llm_config=llm_config,
    is_termination_msg=lambda msg: "thanks" in msg["content"].lower(),
    system_message=f"""You are a smart scheduling assistant. Today is {today}. When the user provides a start time, participant emails, and duration, schedule a meeting using the 'schedule_meeting' tool.""")



ConversationAgent = AssistantAgent(
    name="ConversationAgent",
    llm_config=llm_config_manager,
    is_termination_msg=lambda msg: "thanks" or "thank you" in msg["content"].lower(),
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
    llm_config=llm_config,
    is_termination_msg=lambda msg: "thank you" in msg["content"].lower() or "thanks" in msg["content"].lower(),
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


# Register the tool signature with the assistant agent.
CallAgent.register_for_llm(name="request_call", description="Make a call to a given phone number")(request_call)
MeetAgent.register_for_llm(name="join_meeting", description="Join a Google Meet meeting with a bot.")(join_meeting)
Mailgetter.register_for_llm(name="fetch_latest_email", description="Fetch emails of user with name and password.")(fetch_latest_email)
RAGAgent.register_for_llm(name="load_and_query_rag_doc", description="Answer using the provided document")(load_and_query_rag_doc)
SchedulerAgent.register_for_llm(name="schedule_meeting", description="Schedule a meeting on Google Calendar with given emails.")(schedule_meeting)
EmailSenderAgent.register_for_llm(name="smart_email_sender", description="Sends an email with AI-generated subject and body from a natural language message.")(smart_email_sender)
# Register the tool function with the user proxy agent.
# Register tool functions for their respective agents (needed for group chat execution)
RAGAgent.register_for_execution(name="load_and_query_rag_doc")(load_and_query_rag_doc)
CallAgent.register_for_execution(name="request_call")(request_call)
MeetAgent.register_for_execution(name="join_meeting")(join_meeting)
Mailgetter.register_for_execution(name="fetch_latest_email")(fetch_latest_email)
SchedulerAgent.register_for_execution(name="schedule_meeting")(schedule_meeting)
EmailSenderAgent.register_for_execution(name="smart_email_sender")(smart_email_sender)

# Create a user proxy agent that will handle user interactions
User = UserProxyAgent(
    name="UserAgent",
    llm_config=llm_config,
    description=f"""
You are a human user. You may engage in normal conversations or ask for help with tasks.

If the user message appears to request a task (e.g., send email, make call, join meeting), ensure it contains all required details. If not, ask the user to provide complete information before proceeding.

DO NOT assume anything from vague statements like "can you do it?" or "send a message" unless the user gives exact information (e.g., recipient email, message content, phone number, meeting link, etc.).

Be smart about differentiating general conversation from actionable commands.

When summarizing, calling, emailing, or scheduling — proceed only if the user's input is fully sufficient.

Always end your message with 'THANKS' to signal completion.
""",
    code_execution_config=False,
    is_termination_msg=lambda msg: "thanks" in msg["content"].lower(),
    human_input_mode="NEVER"
)

# print(User.description)


# Register the tool signature with the assistant agent.
User.register_for_llm(name="request_call", description="Make a call to a given phone number")(request_call)
User.register_for_llm(name="join_meeting", description="Join a Google Meet meeting with a bot.")(join_meeting)
User.register_for_llm(name="fetch_latest_email", description="Fetch emails of user with name and password.")(fetch_latest_email)
User.register_for_llm(name="load_and_query_rag_doc", description="Answer using the provided document")(load_and_query_rag_doc)
User.register_for_llm(name="schedule_meeting", description="Schedule a meeting on Google Calendar with given emails.")(schedule_meeting)
User.register_for_llm(name="smart_email_sender", description="Sends an email with AI-generated subject and body from a natural language message.")(smart_email_sender)
# Register the tool function with the user proxy agent.
# Register tool functions for their respective agents (needed for group chat execution)
User.register_for_execution(name="smart_email_sender")(smart_email_sender)
User.register_for_execution(name="load_and_query_rag_doc")(load_and_query_rag_doc)
User.register_for_execution(name="schedule_meeting")(schedule_meeting)
User.register_for_execution(name="request_call")(request_call)
User.register_for_execution(name="join_meeting")(join_meeting)
User.register_for_execution(name="fetch_latest_email")(fetch_latest_email)

# Define the group chat participants (agents only)
group_chat = GroupChat(
    agents=[User, CallAgent, MeetAgent, Mailgetter, RAGAgent, ConversationAgent, SchedulerAgent, EmailSenderAgent],  # ✅ now includes RAG
    messages=[],
  # Limit the number of rounds to keep interactions short
    allow_repeat_speaker= False,
    speaker_selection_method="auto",  # Round-robin speaker selection
)

ManagerAgent = GroupChatManager(
    name="ManagerAgent",
    system_message="""
You are a manager assistant. The user may ask you to perform multiple tasks, such as making calls, joining meetings, fetching emails, or answering questions using documents. Your responsibilities include:

1. Breaking down the user's request into actionable steps.
2. Delegating tasks to the appropriate agents (CallAgent, MeetAgent, Mailgetter, RAGAgent, or ConversationAgent).
3. Waiting for confirmation from the user after each task before proceeding to the next step.
4. Providing clear and concise updates to the user about the progress and results of each task.
5. Detecting and breaking conversational loops by monitoring repeated messages or patterns.

Ensure that all tasks are executed efficiently and accurately.
""",
    groupchat=group_chat,
    llm_config=llm_config_manager
)


# Redirect user input to the manager instead of a specific agent
# --- NEW FUNCTION FOR EXPORT ---
def build_team_with_manager(user_input_func=None):
    # Set input_func if user proxy is to be interactive (via WebSocket)
    if user_input_func:
        User.human_input_mode = "TERMINAL"
        User.input_func = user_input_func
    else:
        User.human_input_mode = "NEVER"

    # Return the manager (entry point for the WebSocket chat)
    return ManagerAgent


# Add to end of call_agent.py
__all__ = [
    'CallAgent',
    'MeetAgent',
    'Mailgetter',
    'RAGAgent',
    'SchedulerAgent',
    'EmailSenderAgent',
    'ConversationAgent',
    'User'  # Rename to UserProxyAgent if needed
]
