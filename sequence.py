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

# Start a sequence of two-agent chats.
# Each element in the list is a dictionary that specifies the arguments
# for the initiate_chat method.
chat_results = number_agent.initiate_chats(
    [
        {
            "recipient": adder_agent,
            "message": "14",
            "max_turns": 2,
            "summary_method": "last_msg",
        },
        {
            "recipient": multiplier_agent,
            "message": "These are my numbers",
            "max_turns": 2,
            "summary_method": "last_msg",
        },
        {
            "recipient": subtracter_agent,
            "message": "These are my numbers",
            "max_turns": 2,
            "summary_method": "last_msg",
        },
        {
            "recipient": divider_agent,
            "message": "These are my numbers",
            "max_turns": 2,
            "summary_method": "last_msg",
        },
    ]
)