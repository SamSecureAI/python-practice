import getpass
import hashlib
import json
import os

# ================= Constants =================
DATA_FILE = "users.json"
MAX_ATTEMPTS = 3
MIN_PIN_LENGTH = 6

# ================= Helper Functions =================
def hash_pin(pin: str) -> str:
    """Return a SHA-256 hash of the pin."""
    return hashlib.sha256(pin.encode()).hexdigest()

def load_users():
    """Load users from JSON file or return empty dict."""
    if not os.path.exists(DATA_FILE):
        return {}
    with open(DATA_FILE, "r") as f:
        return json.load(f)

def save_users(users):
    """Save users dictionary to JSON file."""
    with open(DATA_FILE, "w") as f:
        json.dump(users, f, indent=4)

# ================= Core Functions =================
def set_pin() -> str:
    """Securely set a PIN with confirmation and return its hash."""
    while True:
        pin = getpass.getpass("\nSet your PIN (minimum 4 digits): ").strip()
        if not pin.isdigit():
            print("PIN must contain only digits. Try again.")
            continue
        if len(pin) < MIN_PIN_LENGTH:
            print(f"PIN must be at least {MIN_PIN_LENGTH} digits long. Try again.")
            continue
        confirm = getpass.getpass("Confirm your PIN: ").strip()
        if pin != confirm:
            print("PINs do not match. Try again.")
            continue
        print("✅ PIN set successfully.")
        return hash_pin(pin)

def login(users):
    """Login with up to MAX_ATTEMPTS attempts. Return username if successful."""
    name = input("Enter your name: ").strip().title()
    if name not in users:
        print("No account with this name.")
        return None

    for attempt in range(MAX_ATTEMPTS, 0, -1):
        entered_pin = getpass.getpass("Enter your PIN: ").strip()
        if hash_pin(entered_pin) == users[name]["pin"]:
            print(f"✅ Welcome {name}, login successful.")
            return name
        else:
            print(f"❌ Incorrect PIN ({attempt-1} attempts left).")

    print("🚨 Too many failed attempts. Account locked.")
    return None

def get_user_details(users):
    """Collect user details for registration."""
    name = input("Enter your name: ").strip().title()
    if name in users:
        print("❌ An account with this name already exists.")
        return None, None, None, None

    gender = ""
    while gender not in ("M", "F", "O"):
        gender = input("Enter your gender (M/F/O for Other): ").strip().upper()
        if gender not in ("M", "F", "O"):
            print("Please enter M, F, or O.")

    while True:
        try:
            age = int(input("Enter your age: "))
            if age <= 0:
                print("Age must be positive.")
                continue
            break
        except ValueError:
            print("Invalid age input. Please enter a number.")

    is_vip = False
    if age < 18:
        is_vip = input("Are you a VIP? (yes/no): ").strip().lower() == "yes"
        if not is_vip:
            print("❌ You must be at least 18 or a VIP to register.")
            return None, None, None, None

    return name, gender, age, is_vip

def deposit(balance: float) -> float:
    """Deposit funds into balance."""
    try:
        amount = float(input("Enter deposit amount: "))
        if amount <= 0:
            print("Deposit must be positive.")
            return balance
    except ValueError:
        print("Invalid input.")
        return balance

    balance += amount
    print(f"✅ Deposited: {amount:,.2f}\n💰 New Balance: {balance:,.2f}")
    return balance

def withdraw(balance: float) -> float:
    """Withdraw funds from balance."""
    try:
        amount = float(input("Enter withdrawal amount: "))
        if amount <= 0:
            print("Withdrawal must be positive.")
            return balance
    except ValueError:
        print("Invalid input.")
        return balance

    if amount > balance:
        print("❌ Insufficient funds.")
        return balance

    balance -= amount
    print(f"✅ Withdrawn: {amount:,.2f}\n💰 New Balance: {balance:,.2f}")
    return balance

def banking_menu(username: str, users: dict):
    """Show banking menu for a logged-in user."""
    while True:
        print("\n=== Banking Menu ===")
        print("1. Deposit")
        print("2. Withdraw")
        print("3. Check Balance")
        print("4. Logout")

        choice = input("Choose option (1-4): ").strip()
        match choice:
            case "1":
                users[username]["balance"] = deposit(users[username]["balance"])
                save_users(users)
            case "2":
                users[username]["balance"] = withdraw(users[username]["balance"])
                save_users(users)
            case "3":
                print(f"💰 Current Balance: {users[username]['balance']:,.2f}")
            case "4":
                print("👋 Logged out.")
                break
            case _:
                print("❌ Invalid option.")
                
def register(users):
    """Register a new user."""
    name, gender, age, is_vip = get_user_details(users)
    if name is None:
        return
    pin_hash = set_pin()
    users[name] = {"pin": pin_hash, "balance": 0.0, "age": age, "vip": is_vip}

    save_users(users)
    title = "Mr." if gender == "M" else "Ms." if gender == "F" else ""
    print(f"✅ Registration complete. Welcome {title} {name}!")

# ================= Main Program =================
def main():
    users = load_users()

    while True:
        print("\n=== Welcome to Mini-Bank ===")
        print("1. Register")
        print("2. Login")
        print("3. Exit")

        option = input("Choose (1-3): ").strip()
        match option:
            case "1":
                register(users)
            case "2":
                username = login(users)
                if username:
                    banking_menu(username, users)
            case "3":
                print("🙏 Thanks for using Mini-Bank. Goodbye!")
                break
            case _:
                print("❌ Invalid choice.")

if __name__ == "__main__":
    main()
