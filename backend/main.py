import os
from fastapi import FastAPI, HTTPException, status
import psycopg2
import time
from database import init_db

app = FastAPI()

db_user = os.getenv("DB_USER")
db_password = os.getenv("DB_PASSWORD")
db_name = os.getenv("DB_NAME")
host = 'db'

DATABASE_URL = f"postgresql://{db_user}:{db_password}@{host}:5432/{db_name}"

def get_db_connection():
    retries = 5
    while retries > 0:
        try:
            conn = psycopg2.connect(DATABASE_URL)
            return conn
        except Exception as e:
            print(f"Trying to connect to database... {e}")
            time.sleep(2)
            retries -= 1
    raise Exception("Couldn't open database...")


@app.on_event("startup")
def startap_event():
    init_db()

@app.get("/")
def read_root():
    return{"message": "Welcome to pendapatan daerah api root page"}

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
def login(username: str, password: str):
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        i = cur.execute(
            "SELECT * FROM users WHERE username = %s AND password = %s", (username, password)
        )
        user = cur.fetchone()
        if user:
            return {"status": "success", "message": "Login Success"}
        else:
            raise HTTPException(
                status_code= status.HTTP_401_UNAUTHORIZED,
                detail="username or password wrong"
            )
    finally:
        cur.close()
        conn.close()

@app.post("/register")
def register(username: str, password:str, confirmPassword:str):
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        if password != confirmPassword:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="password doesn't match"
            )

        cur.execute(
            "INSERT INTO users (username, password) VALUES (%s, %s)", (username, password)
        )
        conn.commit()
        return{"status": "success", "message": "success create new account"}
    except psycopg2.IntegrityError:
        conn.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Username already exists"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database Error: {e}"
        )
    finally:
        cur.close()
        conn.close()
