import secrets
import string

def append_to_items():
    print("hi")

def secure_random_hash(length=15):
    return ''.join(secrets.choice(string.digits) for _ in range(length))
