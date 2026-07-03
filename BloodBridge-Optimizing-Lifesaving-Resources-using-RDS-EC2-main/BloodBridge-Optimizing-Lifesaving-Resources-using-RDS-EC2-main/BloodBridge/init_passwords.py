from werkzeug.security import generate_password_hash

# Generate fresh hashes
print("=== BloodBridge Password Hashes ===")
print()

passwords = {
    "admin123": "Admin / Hospital / Blood Bank / Donor",
}

for pwd, desc in passwords.items():
    h = generate_password_hash(pwd)
    print(f"Password: {pwd}")
    print(f"Description: {desc}")
    print(f"Hash: {h}")
    print()

print("Copy the hash above and replace in schema.sql")
print("Or run: python init_passwords.py")
