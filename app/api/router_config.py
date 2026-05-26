from fastapi import APIRouter
from api.routes import (
    management_routes,
    common_routes,
    discord_routes,
    sheets_routes,
    spreadsheet_routes,
    worksheet_routes
)

api_router = APIRouter()

api_router.include_router(management_routes.router, tags=["management-endpoints"])
api_router.include_router(common_routes.router, tags=["common-endpoints"])
api_router.include_router(discord_routes.router, tags=["discord-endpoints"])
api_router.include_router(sheets_routes.router, tags=["sheets-endpoints"])
api_router.include_router(spreadsheet_routes.router, tags=["spreadsheet-endpoints"])
api_router.include_router(worksheet_routes.router, tags=["worksheet-endpoints"])
