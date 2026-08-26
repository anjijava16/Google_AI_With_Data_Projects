from fastapi import FastAPI

app = FastAPI(
    title="Hello World API",
    version="1.0.0",
)


@app.get("/")
def hello_world():
    return {
        "message": "Hello World",
        "service": "FastAPI on Cloud Run",
    }


@app.get("/health")
def health():
    return {
        "status": "healthy"
    }