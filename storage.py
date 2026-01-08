"""Storage module for JSON file operations."""
import json
import os

GOALS_FILE = "goals.json"
DEPOSITS_FILE = "deposits.json"
WALLET_FILE = "wallet.json"


def load_json(filename: str) -> dict | list:
    """Load data from JSON file."""
    if not os.path.exists(filename):
        return {} if filename in (GOALS_FILE, WALLET_FILE) else []
    with open(filename, "r") as f:
        return json.load(f)


def save_json(filename: str, data: dict | list) -> None:
    """Save data to JSON file."""
    with open(filename, "w") as f:
        json.dump(data, f, indent=2)


def get_goals() -> dict:
    return load_json(GOALS_FILE)


def save_goals(goals: dict) -> None:
    save_json(GOALS_FILE, goals)


def get_deposits() -> list:
    return load_json(DEPOSITS_FILE)


def save_deposits(deposits: list) -> None:
    save_json(DEPOSITS_FILE, deposits)


def get_wallet_state() -> dict:
    return load_json(WALLET_FILE)


def save_wallet_state(state: dict) -> None:
    save_json(WALLET_FILE, state)
