import random
import string

def generate_login_code():
    return ''.join(random.choices(string.digits, k=8))

def generate_username():
    return f"Human{random.randint(1000000, 9999999)}"
