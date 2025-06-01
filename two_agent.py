#TWO AGENT CHAT

import os

from autogen import ConversableAgent

student_agent = ConversableAgent(
    name="Student_Agent",
    system_message="You are a student willing to learn.",
    llm_config={"config_list": [{"model": "gpt-4o-mini", "api_key": "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"}]},
)
teacher_agent = ConversableAgent(
    name="Teacher_Agent",
    system_message="You are a math teacher.",
    llm_config={"config_list": [{"model": "gpt-4o-mini", "api_key": "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"}]},
)

chat_result = student_agent.initiate_chat(
    teacher_agent,
    message="What is triangle inequality?",
    summary_method="reflection_with_llm",
    max_turns=2,
)

print(chat_result.summary)