from typing import Optional
from loguru import logger

try:
    from supabase import create_client, Client
    SUPABASE_AVAILABLE = True
except ImportError:
    logger.warning("Supabase client not available - install with 'poetry add supabase'")
    SUPABASE_AVAILABLE = False
    Client = None

from app.core.config import settings

supabase: Optional[Client] = None

if SUPABASE_AVAILABLE and settings.SUPABASE_URL and settings.SUPABASE_KEY:
    try:
        supabase = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)
        logger.info("Supabase client initialized")
    except Exception as e:
        logger.warning(f"Failed to initialize Supabase client: {e}")
else:
    logger.warning("Supabase client disabled - missing URL/KEY configuration")