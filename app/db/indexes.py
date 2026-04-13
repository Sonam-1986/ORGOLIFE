"""
MongoDB index definitions for query optimization.
Called once at startup after DB connection is established.
"""
import logging
from pymongo import ASCENDING, DESCENDING, TEXT
from app.db.database import get_database

logger = logging.getLogger(__name__)


async def create_indexes() -> None:
    """Create all necessary indexes across collections."""
    db = get_database()

    # ── users ────────────────────────────────────────────────────
    await db["users"].create_index(
        [("email", ASCENDING)], unique=True, name="idx_users_email_unique"
    )
    await db["users"].create_index([("role", ASCENDING)], name="idx_users_role")

    # ── donors ───────────────────────────────────────────────────
    await db["donors"].create_index(
        [("user_id", ASCENDING)], unique=True, name="idx_donors_user_id"
    )
    await db["donors"].create_index([("status", ASCENDING)], name="idx_donors_status")
    await db["donors"].create_index([("verified", ASCENDING)], name="idx_donors_verified")

    # ── organ_registrations ──────────────────────────────────────
    await db["organ_registrations"].create_index(
        [("donor_id", ASCENDING)], name="idx_organ_donor_id"
    )
    await db["organ_registrations"].create_index(
        [("organ_name", ASCENDING), ("blood_group", ASCENDING)],
        name="idx_organ_search"
    )
    await db["organ_registrations"].create_index(
        [("state", ASCENDING), ("city", ASCENDING)],
        name="idx_organ_location"
    )
    # Compound index for receiver search filter
    await db["organ_registrations"].create_index(
        [
            ("organ_name", ASCENDING),
            ("blood_group", ASCENDING),
            ("state", ASCENDING),
            ("city", ASCENDING),
        ],
        name="idx_organ_compound_search"
    )

    # ── receivers ────────────────────────────────────────────────
    await db["receivers"].create_index(
        [("user_id", ASCENDING)], unique=True, name="idx_receivers_user_id"
    )

    # ── hospitals ────────────────────────────────────────────────
    await db["hospitals"].create_index(
        [("name", TEXT)], name="idx_hospitals_name_text"
    )
    await db["hospitals"].create_index(
        [("admin_user_id", ASCENDING)], name="idx_hospitals_admin"
    )

    logger.info("✅ MongoDB indexes created successfully.")
