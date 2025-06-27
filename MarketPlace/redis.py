import redis
import json
import os
from dotenv import load_dotenv
load_dotenv()

REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
REDIS_DB = int(os.getenv("REDIS_DB", 0))

client = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB, decode_responses=True)

def save_user_context(user_id, key, data):
    context = client.get(user_id)
    if context:
        context = json.loads(context)
    else:
        context = {}

    context[key] = data
    client.set(user_id, json.dumps(context))

def get_user_context(user_id, key):
    context = client.get(user_id)
    if context:
        context = json.loads(context)
        return context.get(key, None)
    return None

def clear_user_context(user_id):
    client.delete(user_id)


def get_memory_block(user_id="session1"):
    summary = get_user_context(user_id, "last_summary") or "None"
    history = get_user_context(user_id, "history") or []
    last_messages = "\n".join(f"- {msg}" for msg in history[-3:])
    return f"""
### CONTEXT MEMORY:
Summary:
{summary}

Recent conversation:
{last_messages if last_messages else 'None'}
"""
