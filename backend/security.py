import os
from pwdlib import PasswordHash
from jose import jwt
from datetime import datetime, timedelta


## Password Management
pwd_context = PasswordHash.recommended()


def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(password_input: str, password: str) -> bool:
    return pwd_context.verify(password_input, password)


# Token
SECURITY_KEY = os.getenv("SECRET_KEY")
if not SECURITY_KEY:
    raise RuntimeError("No Security key set on environtment")
ALGORITHMS = "HS256"
EXPIRED_TIME = 30

def create_access_token(data: dict):
    to_encode = data.copy()

    expire = datetime.utcnow() + timedelta(minutes=EXPIRED_TIME)
    to_encode.update({"exp": expire})

    encode_jwt = jwt.encode(to_encode, SECURITY_KEY, algorithm=ALGORITHMS)
    return encode_jwt

if __name__ == "__main__":
    pw = "hoshim1"
    hash_pw = hash_password(pw)
    print(f"plaint: {pw}")
    print(f"hashed: {hash_pw}")
    print(f"fetching: {verify_password(pw, hash_pw)}")
