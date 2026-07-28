from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import health
from app.routers import auth as auth_router
from app.routers import organizations as orgs_router
from app.routers import organization_members as org_members_router
from app.routers import workspaces as workspaces_router
from app.routers import projects as projects_router

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
app.include_router(auth_router.router)
app.include_router(orgs_router.router, prefix="/api")
app.include_router(org_members_router.router, prefix="/api")
app.include_router(workspaces_router.router, prefix="/api")
app.include_router(projects_router.router, prefix="/api")
