from fastapi import FastAPI, APIRouter, Depends
from helpers.config import get_settings, Settings

base_router = APIRouter(
    prefix="/api/v1" , 
    tags=["api_v1"]
)

@base_router.get('/')
def welcome(app_settings: Settings = Depends(get_settings)):
    # app_settings = app_settings()
    app_name = app_settings.APP_NAME
    return {
        "Hello": app_name
        }