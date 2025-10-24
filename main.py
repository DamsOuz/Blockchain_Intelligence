import os
from src.ingest_contract import get_contract_data
from src.analyze_contract import analyze_contract
from src.parse_source import parse_solidity_source
from src.utils import print_summary
from src.query_assistant import answer_question


def main():
    # USDC contract address
    address = "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48"

    if not os.path.exists(f"data/{address}_abi.json") or not os.path.exists(f"data/{address}_source.sol"):
        get_contract_data(address)

    abi_summary = analyze_contract(address)
    parsed_source = parse_solidity_source(address)

    contract_knowledge = {
        "address": address,
        "abi_summary": abi_summary,
        "source_analysis": parsed_source,
    }

    print("\nABI Summary:")
    print_summary(abi_summary)
    print("\nSource Code Summary:")
    print_summary(parsed_source)

    while True:
        question = input("\nAsk a question about this contract (or 'exit'): ")
        if question.lower() == "exit":
            break
        answer = answer_question(question, contract_knowledge)
        print("\nAnswer:", answer)

    print("Code finished")


if __name__ == "__main__":
    main()
