import bcrypt


def verify_password(plain_password: str, hashed_password: bytes) -> bool:
    password_bytes = bytes(plain_password, "utf-8")
    return bcrypt.checkpw(password_bytes, hashed_password)


def get_password_hash(password: str) -> bytes:
    pw = bytes(password, "utf-8")
    return bcrypt.hashpw(pw, bcrypt.gensalt())


