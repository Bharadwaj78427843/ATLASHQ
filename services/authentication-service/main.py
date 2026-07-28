from fastapi import FastAPI

app = FastAPI(title="Atlas Authentication Service")

@app.get("/health")
def health_check():
    return {"status": "ok", "service": "authentication-service"}
