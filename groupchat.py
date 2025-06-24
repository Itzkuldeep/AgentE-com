import os
from autogen import ConversableAgent

# The Number Agent always returns the same numbers.
number_agent = ConversableAgent(
    name="Number_Agent",
    system_message="You return me the numbers I give you, one number each line.",
    llm_config={"config_list": [{"model": "gpt-4o-mini", "api_key": "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"}]},
    human_input_mode="NEVER",
)

# The Adder Agent adds 1 to each number it receives.
adder_agent = ConversableAgent(
    name="Adder_Agent",
    system_message="You add 1 to each number I give you and return me the new numbers, one number each line.",
    llm_config={"config_list": [{"model": "gpt-4o-mini", "api_key": "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"}]},
    human_input_mode="NEVER",
)

# The Multiplier Agent multiplies each number it receives by 2.
multiplier_agent = ConversableAgent(
    name="Multiplier_Agent",
    system_message="You multiply each number I give you by 2 and return me the new numbers, one number each line.",
    llm_config={"config_list": [{"model": "gpt-4o-mini", "api_key": "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"}]},
    human_input_mode="NEVER",
)

# The Subtracter Agent subtracts 1 from each number it receives.
subtracter_agent = ConversableAgent(
    name="Subtracter_Agent",
    system_message="You subtract 1 from each number I give you and return me the new numbers, one number each line.",
    llm_config={"config_list": [{"model": "gpt-4o-mini", "api_key": "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"}]},
    human_input_mode="NEVER",
)

# The Divider Agent divides each number it receives by 2.
divider_agent = ConversableAgent(
    name="Divider_Agent",
    system_message="You divide each number I give you by 2 and return me the new numbers, one number each line.",
    llm_config={"config_list": [{"model": "gpt-4o-mini", "api_key": "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"}]},
    human_input_mode="NEVER",
)

# The `description` attribute is a string that describes the agent.
# It can also be set in `ConversableAgent` constructor.
adder_agent.description = "Add 1 to each input number."
multiplier_agent.description = "Multiply each input number by 2."
subtracter_agent.description = "Subtract 1 from each input number."
divider_agent.description = "Divide each input number by 2."
number_agent.description = "Return the numbers given."

from autogen import GroupChat

group_chat = GroupChat(
    agents=[multiplier_agent, subtracter_agent, divider_agent, number_agent],
    messages=[],
    max_round=10,
    send_introductions=True
)

from autogen import GroupChatManager

group_chat_manager = GroupChatManager(
    groupchat=group_chat,
    llm_config={"config_list": [{"model": "gpt-4o-mini", "api_key": "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"}]},
)

chat_result = number_agent.initiate_chat(
    group_chat_manager,
    message="My number is 3, I want to turn it into 13.",
    summary_method="reflection_with_llm",
)