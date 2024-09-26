from datetime import datetime
import logging

from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from rich.console import Console

from routers import tts, transcription, system, welcome,voice_records
from middleware.permissions import AddPermissionsPolicyMiddleware
from services.db import initialize_database
from services.tts_service import initialize_tts
from utils.dependencies import database_exception_handler, DatabaseError

# Initialize logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

console = Console()

# Lifespan function to handle startup and shutdown events
async def lifespan(app: FastAPI):
    console.print("[cyan]Starting application...[/cyan]")
    initialize_database()
    initialize_tts()
    yield
    console.print("[cyan]Shutting down application...[/cyan]")

# Initialize FastAPI with lifespan
app = FastAPI(lifespan=lifespan)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Update as per your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add custom Permissions Policy middleware
app.add_middleware(AddPermissionsPolicyMiddleware)

app.add_exception_handler(DatabaseError, database_exception_handler)

# Include routers
app.include_router(welcome.router)
app.include_router(tts.router, prefix="/tts", tags=["TTS"])  # tags are used for OpenAPI documentation
app.include_router(transcription.router, prefix="/transcription", tags=["Transcription"])
app.include_router(system.router, prefix="/system", tags=["System"])
app.include_router(voice_records.router, prefix="/voice-records",tags=["Voice Records"])

# Optional: Root endpoint if not handled by welcome.router
@app.get("/", response_class=HTMLResponse)
async def root():
    return welcome.welcome_page_template()

# Run the application
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
