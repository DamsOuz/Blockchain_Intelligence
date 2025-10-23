import os
import json
import requests
from dotenv import load_dotenv

load_dotenv()

ETHERSCAN_API_KEY = os.getenv("ETHERSCAN_API_KEY")
ETHERSCAN_API_URL = "https://api.etherscan.io/v2/api"
CHAIN_ID = "1"  # Ethereum Mainnet

DATA_DIR = "data"
os.makedirs(DATA_DIR, exist_ok=True)


def get_contract_data(address: str):
    params = {
        "chainid": CHAIN_ID,
        "module": "contract",
        "action": "getsourcecode",
        "address": address,
        "apikey": ETHERSCAN_API_KEY,
    }

    response = requests.get(ETHERSCAN_API_URL, params=params)
    data = response.json()

    if data["status"] != "1":
        raise Exception(f"Error API Etherscan : {data.get('result')}")

    result = data["result"][0]

    source_code = result["SourceCode"]
    abi = json.loads(result["ABI"])

    save_path_code = os.path.join(DATA_DIR, f"{address}_source.sol")
    save_path_abi = os.path.join(DATA_DIR, f"{address}_abi.json")

    with open(save_path_code, "w", encoding="utf-8") as f:
        f.write(source_code)

    with open(save_path_abi, "w", encoding="utf-8") as f:
        json.dump(abi, f, indent=2)

    return {"address": address, "source_code": source_code, "abi": abi}
