
from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

router = APIRouter()
templates = Jinja2Templates(directory="public")

@router.get("/", response_class=HTMLResponse)
async def get_index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@router.get("/grading", response_class=HTMLResponse)
async def get_grading(request: Request):
    return templates.TemplateResponse("grading.html", {"request": request})
