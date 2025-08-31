import secrets
import string


class TokenUtils:
    @staticmethod
    def generate_api_key(prefix="pulsetap_", length=32):
        characters = string.ascii_letters + string.digits
        api_key = "".join(secrets.choice(characters) for _ in range(length))
        return prefix + api_key
