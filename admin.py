#!/usr/bin/env python3
"""
Admin script for managing users in users.csv
Usage:
    python admin.py add <username> <password> <email> <name>
    python admin.py remove <username>
    python admin.py list
    python admin.py reset <username> <new_password>
"""

import csv
import sys
import os

USERS_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "users", "users.csv")


def load_users():
    """Load users from CSV file"""
    users = {}
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, "r", encoding="utf-8", newline="") as f:
            reader = csv.DictReader(f)
            for row in reader:
                users[row["username"]] = {
                    "password": row["password"],
                    "email": row["email"],
                    "name": row["name"]
                }
    return users


def save_users(users):
    """Save users to CSV file"""
    os.makedirs(os.path.dirname(USERS_FILE), exist_ok=True)
    with open(USERS_FILE, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["username", "password", "email", "name"])
        for username, info in users.items():
            writer.writerow([username, info["password"], info["email"], info["name"]])


def add_user(username: str, password: str, email: str, name: str):
    """Add a new user"""
    users = load_users()
    
    if username in users:
        print(f"Error: User '{username}' already exists!")
        return False
    
    users[username] = {
        "password": password,
        "email": email,
        "name": name
    }
    
    save_users(users)
    print(f"User '{username}' added successfully!")
    return True


def remove_user(username: str):
    """Remove a user"""
    users = load_users()
    
    if username not in users:
        print(f"Error: User '{username}' not found!")
        return False
    
    del users[username]
    save_users(users)
    print(f"User '{username}' removed successfully!")
    return True


def list_users():
    """List all users"""
    users = load_users()
    
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
    users = load_users()
    
    if username not in users:
        print(f"Error: User '{username}' not found!")
        return False
    
    users[username]["password"] = new_password
    save_users(users)
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
