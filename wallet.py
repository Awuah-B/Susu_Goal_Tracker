"""USDC wallet balance fetcher using Etherscan API."""
import requests
from config import get_config

# USDC contract on Ethereum mainnet
USDC_CONTRACT = "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48"
USDC_DECIMALS = 6


def get_usdc_balance(wallet_address: str = None) -> float:
    """Fetch USDC balance for wallet address using Etherscan V2 API."""
    config = get_config()
    address = wallet_address or config["wallet_address"]
    api_key = config["etherscan_api_key"]
    
    # Etherscan V2 API endpoint
    url = (
        f"https://api.etherscan.io/v2/api"
        f"?chainid=1"
        f"&module=account"
        f"&action=tokenbalance"
        f"&contractaddress={USDC_CONTRACT}"
        f"&address={address}"
        f"&tag=latest"
        f"&apikey={api_key}"
    )
    
    response = requests.get(url, timeout=10)
    data = response.json()
    
    if data["status"] != "1":
        # Include result field which often has more details
        msg = data.get("message", "Unknown error")
        result = data.get("result", "")
        raise Exception(f"Etherscan error: {msg} - {result}")
    
    # Convert from smallest unit (6 decimals for USDC)
    balance = int(data["result"]) / (10 ** USDC_DECIMALS)
    return balance
