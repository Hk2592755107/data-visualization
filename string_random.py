import random
import string

def generate_random_string(length):
    """Generates a random string of specified length using alphanumeric characters."""
    characters = string.ascii_letters
    random_string = ''.join(random.choice(characters) for _ in range(length))
    return random_string

def generate_random_email():
    """Generates a random email address."""
    username = generate_random_string(8)
    domain = generate_random_string(5)
    return f"{username}@{domain}.com"

def generate_random_contact_number():
    """Generates a random contact number."""
    return ''.join(random.choice('0123456789') for _ in range(11))