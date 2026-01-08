"""Config loader for Susu bot."""
import json
import os

CONFIG_FILE = "config.json"


def load_config() -> dict:
    """Load configuration from config.json."""
    if not os.path.exists(CONFIG_FILE):
        raise FileNotFoundError(
            f"Missing {CONFIG_FILE}. Create it with:\n"
            "{\n"
            '  "telegram_bot_token": "YOUR_TOKEN",\n'
            '  "telegram_chat_id": "YOUR_CHAT_ID",\n'
            '  "wallet_address": "0x...",\n'
            '  "etherscan_api_key": "YOUR_KEY"\n'
            "}"
        )
    with open(CONFIG_FILE, "r") as f:
        return json.load(f)


def get_config() -> dict:
    """Get cached config."""
    return load_config()
