import os


def get_authentication_header():
    return f"Bearer {os.getenv('INFINITY_GAUNTLET_AUTH')}"
