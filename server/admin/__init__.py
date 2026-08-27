"""Nexus Frontier Admin Package."""
from server.admin.admin_service import admin_service, AdminService
from server.admin.routes import router as admin_router

__all__ = ["admin_service", "AdminService", "admin_router"]
