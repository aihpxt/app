from fastapi import APIRouter, Depends
from datetime import datetime
import sqlite3
import psutil
import os
from pathlib import Path

router = APIRouter(prefix="/health", tags=["系统健康检查"])

@router.get("")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "service": "小龙虾择校API"
    }

@router.get("/detailed")
async def detailed_health_check():
    db_status = "healthy"
    db_size = 0
    db_tables = 0
    
    try:
        db_path = Path("data/schools.db")
        if db_path.exists():
            db_size = db_path.stat().st_size / 1024 / 1024
            
            conn = sqlite3.connect(str(db_path))
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM sqlite_master WHERE type='table'")
            db_tables = cursor.fetchone()[0]
            conn.close()
        else:
            db_status = "not_found"
    except Exception as e:
        db_status = f"error: {str(e)}"
    
    cpu_percent = psutil.cpu_percent(interval=1)
    memory = psutil.virtual_memory()
    disk = psutil.disk_usage("/")
    
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "service": {
            "name": "小龙虾择校API",
            "version": "1.0.0",
            "environment": os.getenv("APP_ENV", "development")
        },
        "database": {
            "status": db_status,
            "size_mb": round(db_size, 2),
            "tables": db_tables
        },
        "system": {
            "cpu_percent": cpu_percent,
            "memory_percent": memory.percent,
            "memory_used_gb": round(memory.used / 1024 / 1024 / 1024, 2),
            "memory_total_gb": round(memory.total / 1024 / 1024 / 1024, 2),
            "disk_percent": disk.percent,
            "disk_used_gb": round(disk.used / 1024 / 1024 / 1024, 2),
            "disk_total_gb": round(disk.total / 1024 / 1024 / 1024, 2)
        }
    }

@router.get("/ready")
async def readiness_check():
    checks = {
        "database": False,
        "api": True
    }
    
    try:
        db_path = Path("data/schools.db")
        if db_path.exists():
            conn = sqlite3.connect(str(db_path))
            cursor = conn.cursor()
            cursor.execute("SELECT 1")
            conn.close()
            checks["database"] = True
    except:
        pass
    
    all_ready = all(checks.values())
    
    return {
        "ready": all_ready,
        "checks": checks,
        "timestamp": datetime.now().isoformat()
    }
