from fastapi import FastAPI

app = FastAPI(title="User Simulator - Release 1")

@app.get("/")
def root():
    return {"message": "Hello from Release 1 foundation!"}
