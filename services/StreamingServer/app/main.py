from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routers.api import router as api_router
from .routers.admin import router as admin_router

app = FastAPI(title="StreamingServer")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], allow_credentials=True,
    allow_methods=["*"], allow_headers=["*"],
)

app.include_router(api_router)
app.include_router(admin_router)

@app.get("/healthz")
def healthz():
    return {"ok": True}
