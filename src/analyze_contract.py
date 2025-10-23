import json
import os
from typing import Dict

DATA_DIR = "data"


def load_abi(address: str):
    path = os.path.join(DATA_DIR, f"{address}_abi.json")

    if not os.path.exists(path):
        raise FileNotFoundError(f"ABI file not found for address {address}")

    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def analyze_contract(address: str):
    abi = load_abi(address)

    functions = [item for item in abi if item["type"] == "function"]
    events = [item for item in abi if item["type"] == "event"]
    constructors = [item for item in abi if item["type"] == "constructor"]
    fallbacks = [item for item in abi if item["type"] == "fallback"]

    public_functions = [func["name"] for func in functions]
    view_functions = [func["name"] for func in functions if func.get("stateMutability") == "view"]
    payable_functions = [func["name"] for func in functions if func.get("stateMutability") == "payable"]
    restricted_functions = [func["name"] for func in functions if any(keyword in func["name"].lower() for keyword in ["admin", "owner"])]
    emitted_events = [ev["name"] for ev in events]

    return {
        "total_functions": len(functions),
        "total_events": len(events),
        "total_constructors": len(constructors),
        "total_fallbacks": len(fallbacks),
        "public_functions": public_functions,
        "view_functions": view_functions,
        "payable_functions": payable_functions,
        "owner_related_functions": restricted_functions,
        "emitted_events": emitted_events
    }
