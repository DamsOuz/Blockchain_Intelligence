# Blockchain Intelligence  
### *Smart Contract Analyzer by Local LLM (Phi-3)*


## Overview

Blockchain Intelligence is an interactive smart contract auditor that combines Solidity static analysis with a LLM to answer natural-language questions about Ethereum smart contracts

It automatically:
- Fetches verified smart contract source code and ABI from Etherscan  
- Parses Solidity code (functions, modifiers, events, state variables...)  
- Summarizes the contract structure  
- Lets you ask natural questions like “Who can upgrade the implementation?” or “Which events does it emit when tokens are transferred?”  
- Generates precise, contextual answers using Phi-3, a local LLM running via Ollama


## Installation

### Prerequisites

- Python >= 3.9
- pip and virtualenv
- Ollama (for running local LLMs like Phi-3)


### Clone the repository and install requirements

- git clone https://github.com/DamsOuz/Blockchain_Intelligence.git
- cd Blockchain_Intelligence
- pip install -r requirements.txt
- ollama pull phi3 (to install LLM)

### Create a .env with :
ETHERSCAN_API_KEY = your api key

## Running the project

- ollama serve in a terminal
- run main.py and write your questions in the terminal (or 'exit' if you want to stop the code)
- Examples of questions : "what functions can be called by anyone?"; "which events does it emit when tokens are transferred?"; "who can upgrade the implementation?"; "does it store admin information on-chain?"
