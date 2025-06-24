from datetime import datetime
from websockets.sync.client import connect as ws_connect
import autogen
from autogen.io.websockets import IOWebsockets

def on_connect(iostream: IOWebsockets) -> None:
    print(f" - on_connect(): Connected to client using IOWebsockets {iostream}", flush=True)
    print(" - on_connect(): Receiving message from client.", flush=True)

    # 1. Receive Initial Message
    initial_msg = iostream.input()
    if not initial_msg:
        raise ValueError("Initial message from client is empty.")
    print(f" - on_connect(): Received initial message: {initial_msg}", flush=True)

    # 2. Instantiate ConversableAgent
    agent = autogen.ConversableAgent(
        name="chatbot",
        system_message="Complete a task given to you and reply TERMINATE when the task is done. "
                       "If asked about the weather, use tool 'weather_forecast(city)' to get the weather forecast for a city.",
        llm_config={"config_list": [{"model": "gpt-4o-mini", "api_key": "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"}]},
    )

    # 3. Define UserProxyAgent
    user_proxy = autogen.UserProxyAgent(
        name="user_proxy",
        system_message="A proxy for the user.",
        is_termination_msg=lambda msg: msg.get("content") is not None and "TERMINATE" in msg["content"],
        human_input_mode="ALWAYS",
        max_consecutive_auto_reply=10,
        code_execution_config=False,
    )

    # 4. Define Agent-specific Functions
    def weather_forecast(city: str) -> str:
        return f"The weather forecast for {city} at {datetime.now()} is sunny."

    autogen.register_function(
        weather_forecast, caller=agent, executor=user_proxy, description="Weather forecast for a city"
    )

    # 5. Initiate conversation
    print(f" - on_connect(): Initiating chat with agent {agent} using message '{initial_msg}'", flush=True)
    user_proxy.initiate_chat(agent, message=initial_msg)

    print(" - on_connect(): Conversation finished.", flush=True)

# Start the server in a thread
with IOWebsockets.run_server_in_thread(on_connect=on_connect, port=8765) as uri:
    print(f" - test_setup() with websocket server running on {uri}.", flush=True)

    # Client code for testing
    with ws_connect(uri) as websocket:
        print(f" - Connected to server on {uri}", flush=True)
        print(" - Sending message to server.", flush=True)
        websocket.send("Check out the weather in Paris and write a poem about it.")

        while True:
            try:
                message = websocket.recv()
                message = message.decode("utf-8") if isinstance(message, bytes) else message
                print(message, end="", flush=True)
                if "TERMINATE" in message:
                    print()
                    print(" - Received TERMINATE message. Exiting.", flush=True)
                    break
            except Exception as e:
                print(f" - Error while receiving message: {e}", flush=True)
                break
            finally:
                print(" - WebSocket client loop terminated.", flush=True)

