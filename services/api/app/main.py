from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routers import health

app = FastAPI(title="Atlas API", version="0.1.0")

# Add CORS middleware just in case frontend needs it from browser, though server components don't strictly need it.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router)
