from fastapi import FastAPI
from src.routes.issues import router as issues_router
from src.middlewre.middlewre import timing_middleware
from fastapi.middlewre.cors import CORSMiddleware

app = FastAPI(
    title = "Issue Tracking API v1",
    description = "Mini API using FastAPI",
    version = "0.0.1"
)

app.include_router(issues_router)
app.middleware("http")(timing_middleware)
app.add_middleware(CORSMiddleware,    
    allow_origins=["*"],  #
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)