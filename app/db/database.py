"""
Supabase client setup.
Provides a singleton DB client injected across the app.
"""
import logging
from supabase import create_client, Client
from app.core.config import settings

logger = logging.getLogger(__name__)


class Database:
    client: Client = None


db_instance = Database()


async def connect_db() -> None:
    """Initialise Supabase client on application startup."""
    try:
        db_instance.client = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)
        logger.info("✅ Supabase client initialised.")
    except Exception as e:
        logger.error(f"❌ Supabase connection failed: {e}")
        raise


async def close_db() -> None:
    """No active persistent socket to close for Supabase REST client."""
    logger.info("🔌 Supabase shutdown complete.")


def get_database() -> Client:
    """Return the active database client instance."""
    if db_instance.client is None:
        raise RuntimeError(
            "Database not initialised. Ensure connect_db() ran during app startup."
        )
    return db_instance.client


# ── Table accessors (compat with old structure) ───────────────────

def get_users_table():
    return get_database().table("users")

def get_donors_table():
    return get_database().table("donors")

def get_receivers_table():
    return get_database().table("receivers")

def get_hospitals_table():
    return get_database().table("hospitals")

def get_organ_registrations_table():
    return get_database().table("organ_registrations")
