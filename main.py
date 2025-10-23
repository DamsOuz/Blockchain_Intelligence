from src.ingest_contract import get_contract_data


def main():
    # USDC contract address
    address = "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48"
    contract = get_contract_data(address)
    print("Code finished")


if __name__ == "__main__":
    main()