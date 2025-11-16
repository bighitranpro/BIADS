"""
Settings API - System Configuration Management
"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime
import json
import os

from core.database import get_db

router = APIRouter(prefix="/api/settings", tags=["settings"])

# Settings Model
class SystemSettings(BaseModel):
    # General Settings
    app_name: str = "Bi Ads Multi Tool PRO"
    app_version: str = "3.0.0"
    language: str = "vi"
    theme: str = "dark"
    
    # Task Settings
    default_delay: int = 10  # seconds
    default_retry: int = 3
    default_timeout: int = 30  # seconds
    max_concurrent_tasks: int = 5
    
    # Proxy Settings
    auto_assign_proxy: bool = True
    rotate_proxy_on_error: bool = True
    check_proxy_before_use: bool = True
    
    # Telegram Settings
    telegram_enabled: bool = False
    telegram_bot_token: Optional[str] = None
    telegram_chat_id: Optional[str] = None
    telegram_notify_on_success: bool = True
    telegram_notify_on_error: bool = True
    telegram_notify_on_start: bool = False
    
    # Facebook API Settings
    facebook_app_id: Optional[str] = None
    facebook_app_secret: Optional[str] = None
    facebook_api_version: str = "v18.0"
    
    # Security Settings
    enable_2fa: bool = False
    session_timeout: int = 3600  # seconds
    auto_logout: bool = False
    
    # Automation Settings
    auto_start_tasks: bool = False
    auto_restart_failed_tasks: bool = False
    save_logs_to_file: bool = True
    max_log_entries: int = 1000
    
    # Performance Settings
    cache_enabled: bool = True
    cache_ttl: int = 300  # seconds
    batch_size: int = 10
    
    # Advanced Settings
    debug_mode: bool = False
    verbose_logging: bool = False
    api_rate_limit: int = 100  # requests per minute


class SettingsUpdate(BaseModel):
    key: str
    value: Any


# Storage file
SETTINGS_FILE = "backend/data/settings.json"

# Ensure data directory exists
os.makedirs("backend/data", exist_ok=True)

# Default settings
DEFAULT_SETTINGS = SystemSettings().dict()


def load_settings() -> Dict[str, Any]:
    """Load settings from file"""
    try:
        if os.path.exists(SETTINGS_FILE):
            with open(SETTINGS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        return DEFAULT_SETTINGS.copy()
    except Exception as e:
        print(f"Error loading settings: {e}")
        return DEFAULT_SETTINGS.copy()


def save_settings(settings: Dict[str, Any]) -> bool:
    """Save settings to file"""
    try:
        with open(SETTINGS_FILE, 'w', encoding='utf-8') as f:
            json.dump(settings, f, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        print(f"Error saving settings: {e}")
        return False


@router.get("/")
async def get_settings():
    """Get all system settings"""
    settings = load_settings()
    return {
        "success": True,
        "settings": settings,
        "timestamp": datetime.now().isoformat()
    }


@router.get("/category/{category}")
async def get_settings_by_category(category: str):
    """Get settings by category (general, task, proxy, telegram, etc.)"""
    settings = load_settings()
    
    # Filter by category
    category_map = {
        "general": ["app_name", "app_version", "language", "theme"],
        "task": ["default_delay", "default_retry", "default_timeout", "max_concurrent_tasks"],
        "proxy": ["auto_assign_proxy", "rotate_proxy_on_error", "check_proxy_before_use"],
        "telegram": ["telegram_enabled", "telegram_bot_token", "telegram_chat_id", 
                     "telegram_notify_on_success", "telegram_notify_on_error", "telegram_notify_on_start"],
        "facebook": ["facebook_app_id", "facebook_app_secret", "facebook_api_version"],
        "security": ["enable_2fa", "session_timeout", "auto_logout"],
        "automation": ["auto_start_tasks", "auto_restart_failed_tasks", "save_logs_to_file", "max_log_entries"],
        "performance": ["cache_enabled", "cache_ttl", "batch_size"],
        "advanced": ["debug_mode", "verbose_logging", "api_rate_limit"]
    }
    
    if category not in category_map:
        raise HTTPException(status_code=404, detail=f"Category '{category}' not found")
    
    category_settings = {k: settings.get(k) for k in category_map[category]}
    
    return {
        "success": True,
        "category": category,
        "settings": category_settings
    }


@router.put("/")
async def update_settings(settings: SystemSettings):
    """Update all settings"""
    new_settings = settings.dict()
    
    if save_settings(new_settings):
        return {
            "success": True,
            "message": "Settings updated successfully",
            "settings": new_settings
        }
    else:
        raise HTTPException(status_code=500, detail="Failed to save settings")


@router.put("/update")
async def update_setting(update: SettingsUpdate):
    """Update a single setting"""
    settings = load_settings()
    
    if update.key not in settings:
        raise HTTPException(status_code=404, detail=f"Setting '{update.key}' not found")
    
    # Update the setting
    settings[update.key] = update.value
    
    if save_settings(settings):
        return {
            "success": True,
            "message": f"Setting '{update.key}' updated successfully",
            "key": update.key,
            "value": update.value
        }
    else:
        raise HTTPException(status_code=500, detail="Failed to save setting")


@router.post("/reset")
async def reset_settings():
    """Reset all settings to default"""
    if save_settings(DEFAULT_SETTINGS.copy()):
        return {
            "success": True,
            "message": "Settings reset to default",
            "settings": DEFAULT_SETTINGS
        }
    else:
        raise HTTPException(status_code=500, detail="Failed to reset settings")


@router.post("/reset/{category}")
async def reset_category_settings(category: str):
    """Reset category settings to default"""
    settings = load_settings()
    default = DEFAULT_SETTINGS.copy()
    
    category_map = {
        "general": ["app_name", "app_version", "language", "theme"],
        "task": ["default_delay", "default_retry", "default_timeout", "max_concurrent_tasks"],
        "proxy": ["auto_assign_proxy", "rotate_proxy_on_error", "check_proxy_before_use"],
        "telegram": ["telegram_enabled", "telegram_bot_token", "telegram_chat_id", 
                     "telegram_notify_on_success", "telegram_notify_on_error", "telegram_notify_on_start"],
        "facebook": ["facebook_app_id", "facebook_app_secret", "facebook_api_version"],
        "security": ["enable_2fa", "session_timeout", "auto_logout"],
        "automation": ["auto_start_tasks", "auto_restart_failed_tasks", "save_logs_to_file", "max_log_entries"],
        "performance": ["cache_enabled", "cache_ttl", "batch_size"],
        "advanced": ["debug_mode", "verbose_logging", "api_rate_limit"]
    }
    
    if category not in category_map:
        raise HTTPException(status_code=404, detail=f"Category '{category}' not found")
    
    # Reset category settings
    for key in category_map[category]:
        settings[key] = default[key]
    
    if save_settings(settings):
        return {
            "success": True,
            "message": f"Category '{category}' reset to default",
            "category": category
        }
    else:
        raise HTTPException(status_code=500, detail="Failed to reset category settings")


@router.get("/export")
async def export_settings():
    """Export settings as JSON"""
    settings = load_settings()
    return {
        "success": True,
        "settings": settings,
        "exported_at": datetime.now().isoformat(),
        "version": "3.0.0"
    }


@router.post("/import")
async def import_settings(settings: Dict[str, Any]):
    """Import settings from JSON"""
    try:
        # Validate settings structure
        SystemSettings(**settings)
        
        if save_settings(settings):
            return {
                "success": True,
                "message": "Settings imported successfully",
                "imported_keys": len(settings)
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to save imported settings")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid settings format: {str(e)}")


# Telegram Test
@router.post("/telegram/test")
async def test_telegram():
    """Test Telegram bot connection"""
    from services.telegram_bot import TelegramBot
    import os
    
    settings = load_settings()
    
    if not settings.get("telegram_enabled"):
        raise HTTPException(status_code=400, detail="Telegram is not enabled")
    
    bot_token = settings.get("telegram_bot_token")
    chat_id = settings.get("telegram_chat_id")
    
    if not bot_token or not chat_id:
        raise HTTPException(status_code=400, detail="Telegram bot token or chat ID not configured")
    
    try:
        bot = TelegramBot(bot_token=bot_token, chat_id=chat_id)
        success = bot.send_notification(
            "Test Connection",
            "🧪 This is a test message from Bi Ads Multi Tool PRO",
            "info",
            {"Status": "Testing", "Time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
        )
        
        if success:
            return {
                "success": True,
                "message": "Telegram test message sent successfully"
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to send test message")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Telegram test failed: {str(e)}")


# System Info
@router.get("/system/info")
async def get_system_info():
    """Get system information"""
    import platform
    import psutil
    
    return {
        "success": True,
        "system": {
            "platform": platform.system(),
            "platform_version": platform.version(),
            "architecture": platform.machine(),
            "processor": platform.processor(),
            "python_version": platform.python_version(),
            "cpu_count": psutil.cpu_count(),
            "cpu_percent": psutil.cpu_percent(interval=1),
            "memory_total": psutil.virtual_memory().total,
            "memory_available": psutil.virtual_memory().available,
            "memory_percent": psutil.virtual_memory().percent,
            "disk_usage": psutil.disk_usage('/').percent
        },
        "app": {
            "name": "Bi Ads Multi Tool PRO",
            "version": "3.0.0",
            "api_version": "2.0.0",
            "uptime": "Running"
        }
    }
