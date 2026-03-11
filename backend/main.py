from fastapi import FastAPI, HTTPException, status
import psycopg2
import time

from fastapi.params import Depends
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from security import hash_password, verify_password, create_access_token
from database import init_db
from pydantic import BaseModel, Field
from contextlib import asynccontextmanager
from pydantic_settings import BaseSettings, SettingsConfigDict
from jose import jwt, JWTError

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Initializing database")
    init_db()

    yield
    print("Cleaning up resources")

app = FastAPI(lifespan=lifespan)

#Model
class userRegistry(BaseModel):
    username: str = Field(..., min_length=4, max_length=50, description="Username for login", examples=["Mikohara_Kohane"])
    password: str = Field(..., min_length=8, description="password minimum 8 character")
    confirmPassword: str = Field(..., min_length=8, description="confirm password, make sure the password is the same")

class Settings(BaseSettings):
    DB_USER: str
    DB_PASSWORD: str
    DB_NAME: str
    host: str = 'db'
    model_config = SettingsConfigDict(
        extra = "ignore"
    )
try:
    settings = Settings()
except Exception as e:
    print(f"ERROR: Incomplete Credential. {e}")
    exit(1)

DATABASE_URL = f"postgresql://{settings.DB_USER}:{settings.DB_PASSWORD}@{settings.host}:5432/{settings.DB_NAME}"

def get_db_connection():
    retries = 5
    while retries > 0:
        try:
            conn = psycopg2.connect(DATABASE_URL)
            return conn
        except Exception as x:
            print(f"Trying to connect to database... {x}")
            time.sleep(2)
            retries -= 1
    raise Exception("Couldn't open database...")


@app.get("/")
def read_root():
    return{"message": "Welcome to pendapatan daerah api root page"}

@app.get("/health")
def check_health():
    return {"status": "ok"}

@app.get("/check-db")
def check_db():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT version();')
    db_version = cur.fetchone()
    cur.close()
    conn.close()
    return {"database_version": db_version}

@app.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute(
            "SELECT password FROM users WHERE username = %s", (form_data.username,)
        )
        user = cur.fetchone()
        if not user:
            raise HTTPException(
                status_code= status.HTTP_401_UNAUTHORIZED,
                detail="username or password wrong"
            )
        stored_password = user[0]
        if verify_password(form_data.password, stored_password):
            access_token = create_access_token({"sub": form_data.username})
            return {"access_token": access_token, "token_type": "bearer"}
        else:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="username or password wrong"
            )
    finally:
        cur.close()
        conn.close()

@app.post("/register")
def register(user: userRegistry):
    ##password matching
    if user.password != user.confirmPassword:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="password doesn't match"
        )

    hashed_password = hash_password(user.password)
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute(
            "INSERT INTO users (username, password) VALUES (%s, %s)", (user.username, hashed_password)
        )
        conn.commit()
        return{"status": "success", "message": "success create new account"}
    except psycopg2.IntegrityError:
        conn.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Username already exists"
        )
    except Exception as ex:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database Error: {ex}"
        )
    finally:
        cur.close()
        conn.close()


def get_current_user(token: str = Depends(oauth2_scheme)):
    from security import SECURITY_KEY, ALGORITHMS

    try:
        payload = jwt.decode(token, SECURITY_KEY, algorithms=[ALGORITHMS])
        username = payload.get("sub")
        if username is None:
            raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid Token")
        return username
    except JWTError:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "damaged or expired token")

@app.get("/me")
def whoami(current_user: str = Depends(get_current_user)):
    return {"username": current_user, "message": "token still active until now"}