# AgentE-com

AgentE-com is a Python-based project for building and experimenting with multi-agent systems, chatbots, and data visualization tools. It features modules for agent communication (using websockets and FastAPI), group and team chat, and a MarketPlace for agent interactions. The project also includes scripts for analyzing and plotting stock market gains.

## Features
- Multi-agent communication and orchestration
- Websocket and FastAPI-based chat interfaces
- MarketPlace for agent collaboration and Redis integration
- Data analysis and visualization scripts for stock market data
- Modular design for easy extension and experimentation

## Project Structure
- **agentchat_fastapi/**: FastAPI apps and HTML interfaces for agent and team chat
- **MarketPlace/**: MarketPlace platform for agent interactions, Redis integration, and web UI
- **coding/**: Scripts for stock data analysis and plotting
- **Various Python files**: Core agent logic, tools, and utilities

## Getting Started
1. **Clone the repository:**
	```sh
	git clone https://github.com/Itzkuldeep/AgentE-com.git
	cd AgentE-com
	```
2. **Install dependencies:**
	```sh
	pip install -r MarketPlace/requirements.txt
	```
3. **Run the MarketPlace app:**
	```sh
	cd MarketPlace
	python main.py
	```
4. **Run FastAPI agent chat apps:**
	```sh
	cd agentchat_fastapi
	uvicorn app_agent:app --reload
	# or
	uvicorn app_team:app --reload
	```

## Testing
To test the project, you can run the provided scripts and interact with the web interfaces:
- For MarketPlace: Open `http://localhost:8000` in your browser after running `main.py`.
- For agent chat: Open the respective HTML files in `agentchat_fastapi/` or access the FastAPI endpoints.
- For data analysis: Run scripts in the `coding/` directory, e.g.:
  ```sh
  python coding/plot_stock_gains.py
  ```

## Contributing
Contributions are welcome! To contribute:
1. Fork the repository and create your branch:
	```sh
	git checkout -b feature/your-feature
	```
2. Make your changes and commit them with clear messages.
3. Push to your fork and open a pull request.
4. Ensure your code is well-documented and tested.
