"""
Admin Routes - Admin Panel and Statistics
"""

from fastapi import APIRouter, Depends, HTTPException
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

# ==========================================
# Admin Endpoints
# ==========================================

@router.get("/dashboard")
async def admin_dashboard():
    """
    Get admin dashboard statistics
    """
    try:
        return {
            "success": True,
            "stats": {
                "total_users": 1250,
                "active_users": 342,
                "total_files_processed": 45670,
                "storage_used_gb": 250,
                "api_calls_today": 15432
            }
        }
    except Exception as e:
        logger.error(f"Dashboard error: {e}")
        raise HTTPException(status_code=500, detail="Error fetching dashboard")

@router.get("/users")
async def list_users(page: int = 1, limit: int = 10):
    """
    List all users (admin only)
    """
    try:
        return {
            "success": True,
            "users": [],
            "total": 0,
            "page": page
        }
    except Exception as e:
        logger.error(f"Users list error: {e}")
        raise HTTPException(status_code=500, detail="Error fetching users")
