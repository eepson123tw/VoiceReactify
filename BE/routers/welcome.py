from fastapi import APIRouter
from fastapi.responses import HTMLResponse
from services.welcome import welcomePageTemplate

router = APIRouter()

@router.get("/", response_class=HTMLResponse)
async def root():
    return welcomePageTemplate()
