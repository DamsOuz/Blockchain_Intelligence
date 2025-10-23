import json
from src.ingest_contract import get_contract_data
from src.analyze_contract import analyze_contract
from src.parse_source import parse_solidity_source
from src.utils import print_summary


def main():
    # USDC contract address
    address = "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48"
    contract = get_contract_data(address)
    print(contract)

    summary_abi = analyze_contract(address)
    print_summary(summary_abi)

    print("\n------------------------------------------------------------------------------------------------\n")

    summary_source = parse_solidity_source(address)
    print_summary(summary_source)

    print("Code finished")


if __name__ == "__main__":
    main()
