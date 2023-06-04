import hashlib


def check_sha256_password(pass1: str, pass2: str):
    return hashlib.sha256(pass1.encode('UTF-8')).hexdigest() == hashlib.sha256(pass2.encode('UTF-8')).hexdigest()


def sha256(password: str) -> str:
    return hashlib.sha256(password.encode('UTF-8')).hexdigest()
