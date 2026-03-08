from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def root():
    return{"message": "Welcome to pendapatan daerah api root page"}

@app.post("/login")
def login(username: str, password: str):
    if username == "falXks" and password == "falXks123":
        return {"status": "success", "token": "secret-token1223"}
    return {"status": "failed", "message": "Username or password wrong"}

@app.post("/register")
def register(username: str, password:str, confirmPassword:str):
    if password != confirmPassword:
        return{"status": "failed", "message": "Password doesn't match"}
    return{"status": "success", "message": "success create new account"}
    