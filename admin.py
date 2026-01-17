#!/usr/bin/env python3
"""
Admin script for managing users in config.yaml
Usage:
    python admin.py add <username> <password> <email> <name>
    python admin.py remove <username>
    python admin.py list
    python admin.py reset <username> <new_password>
"""

import yaml
import bcrypt
import sys
import os

CONFIG_FILE = "config.yaml"


def load_config():
    """Load the config file"""
    if not os.path.exists(CONFIG_FILE):
        return {
            "credentials": {"usernames": {}},
            "cookie": {
                "name": "mark_trading_auth",
                "key": "change_this_to_a_random_secret_key",
                "expiry_days": 30
            }
        }
    with open(CONFIG_FILE, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def save_config(config):
    """Save the config file"""
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        yaml.dump(config, f, allow_unicode=True, default_flow_style=False)


def hash_password(password: str) -> str:
    """Hash a password using bcrypt"""
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def add_user(username: str, password: str, email: str, name: str):
    """Add a new user"""
    config = load_config()
    
    if username in config["credentials"]["usernames"]:
        print(f"Error: User '{username}' already exists!")
        return False
    
    config["credentials"]["usernames"][username] = {
        "email": email,
        "name": name,
        "password": hash_password(password)
    }
    
    save_config(config)
    print(f"User '{username}' added successfully!")
    return True


def remove_user(username: str):
    """Remove a user"""
    config = load_config()
    
    if username not in config["credentials"]["usernames"]:
        print(f"Error: User '{username}' not found!")
        return False
    
    del config["credentials"]["usernames"][username]
    save_config(config)
    print(f"User '{username}' removed successfully!")
    return True


def list_users():
    """List all users"""
    config = load_config()
    users = config["credentials"]["usernames"]
    
    if not users:
        print("No users found.")
        return
    
    print(f"\n{'Username':<20} {'Name':<25} {'Email':<30}")
    print("-" * 75)
    for username, info in users.items():
        print(f"{username:<20} {info.get('name', 'N/A'):<25} {info.get('email', 'N/A'):<30}")
    print(f"\nTotal: {len(users)} user(s)")


def reset_password(username: str, new_password: str):
    """Reset a user's password"""
    config = load_config()
    
    if username not in config["credentials"]["usernames"]:
        print(f"Error: User '{username}' not found!")
        return False
    
    config["credentials"]["usernames"][username]["password"] = hash_password(new_password)
    save_config(config)
    print(f"Password for '{username}' reset successfully!")
    return True


def print_usage():
    print(__doc__)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print_usage()
        sys.exit(1)
    
    command = sys.argv[1].lower()
    
    if command == "add":
        if len(sys.argv) != 6:
            print("Usage: python admin.py add <username> <password> <email> <name>")
            sys.exit(1)
        add_user(sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5])
    
    elif command == "remove":
        if len(sys.argv) != 3:
            print("Usage: python admin.py remove <username>")
            sys.exit(1)
        remove_user(sys.argv[2])
    
    elif command == "list":
        list_users()
    
    elif command == "reset":
        if len(sys.argv) != 4:
            print("Usage: python admin.py reset <username> <new_password>")
            sys.exit(1)
        reset_password(sys.argv[2], sys.argv[3])
    
    else:
        print(f"Unknown command: {command}")
        print_usage()
        sys.exit(1)
