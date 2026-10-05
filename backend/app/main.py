from contextlib import asynccontextmanager
from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from app.database import init_db

# Import routers
from app.api.health import router as health_router
from app.api.projects import router as projects_router
from app.api.uploads import router as uploads_router
from app.api.scenarios import router as scenarios_router
from app.api.breach import router as breach_router
from app.api.runs import router as runs_router
from app.api.results import router as results_router
from app.api.measurements import router as measurements_router
from app.api.annotations import router as annotations_router
from app.api.exports import router as exports_router
from app.api.analysis import router as analysis_router
from app.api.compare import router as compare_router
from app.api.solvers import router as solvers_router
from app.api.maps import router as maps_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Initialize DB
    await init_db()
    yield
    # Shutdown logic if any

app = FastAPI(title="BREACHSCOPE API", version="1.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health_router, prefix="/api/health", tags=["Health"])
app.include_router(projects_router, prefix="/api/projects", tags=["Projects"])
app.include_router(uploads_router, prefix="/api/projects", tags=["Uploads"])
app.include_router(scenarios_router, prefix="/api/projects", tags=["Scenarios"])
app.include_router(breach_router, prefix="/api/projects", tags=["Breach"])
app.include_router(runs_router, prefix="/api/projects", tags=["Runs"])
app.include_router(results_router, prefix="/api/projects", tags=["Results"])
app.include_router(measurements_router, prefix="/api/projects", tags=["Measurements"])
app.include_router(annotations_router, prefix="/api/projects", tags=["Annotations"])
app.include_router(exports_router, prefix="/api", tags=["Exports"])
app.include_router(analysis_router, prefix="/api/projects", tags=["Analysis"])
app.include_router(compare_router, prefix="/api/projects", tags=["Compare"])
app.include_router(solvers_router, prefix="/api/solvers", tags=["Solvers"])
app.include_router(maps_router, prefix="/api", tags=["Maps"])

@app.get("/")
async def root():
    return {"message": "Welcome to BREACHSCOPE API"}

@app.websocket("/ws/runs")
async def runs_websocket(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            await websocket.send_text(f"Message text was: {data}")
    except Exception:
        pass
