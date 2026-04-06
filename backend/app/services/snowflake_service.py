"""
DevFlow – Snowflake user management service.
Creates, deletes users, assigns roles, and resets passwords.
"""

from __future__ import annotations

import logging
import secrets
from typing import Any

from app.core.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


def _get_connection():
    """
    Open a Snowflake connection using credentials from settings.
    Returns None when credentials are not configured (mock mode).
    """
    if not settings.SNOWFLAKE_ACCOUNT or not settings.SNOWFLAKE_USER:
        logger.warning("Snowflake credentials not configured – running in mock mode")
        return None

    try:
        import snowflake.connector  # type: ignore[import-untyped]

        conn = snowflake.connector.connect(
            account=settings.SNOWFLAKE_ACCOUNT,
            user=settings.SNOWFLAKE_USER,
            password=settings.SNOWFLAKE_PASSWORD,
            warehouse=settings.SNOWFLAKE_WAREHOUSE,
            database=settings.SNOWFLAKE_DATABASE,
            role=settings.SNOWFLAKE_ROLE,
        )
        return conn
    except Exception as exc:
        logger.exception("Snowflake connection failed")
        raise RuntimeError(f"Snowflake connection error: {exc}") from exc


def create_user(username: str, role: str = "PUBLIC") -> dict[str, Any]:
    """
    Create a new Snowflake user and grant a role.
    """
    try:
        conn = _get_connection()
    except RuntimeError as exc:
        logger.exception("Snowflake connection failed")
        return {"status": "error", "message": f"❌ Snowflake connection failed: {exc}"}

    if conn is None:
        return {
            "status": "success",
            "message": f"✅ [MOCK] User *{username}* is created successfully",
        }

    try:
        cur = conn.cursor()
        # Use separate statements to avoid IF NOT EXISTS properties syntax errors
        cur.execute(f"CREATE USER IF NOT EXISTS {username}")
        temp_pass = f"D3vF10w_{secrets.token_urlsafe(8)}1aA!@9"
        cur.execute(f"ALTER USER {username} SET PASSWORD='{temp_pass}' MUST_CHANGE_PASSWORD=TRUE")
        cur.execute(f"GRANT ROLE {role} TO USER {username}")
        conn.close()
        logger.info("Snowflake user %s created with role %s", username, role)
        return {
            "status": "success",
            "message": f"✅ User *{username}* is created successfully",
        }
    except Exception as exc:
        logger.exception("Snowflake create_user failed")
        return {"status": "error", "message": f"❌ Error creating user: {exc}"}


def delete_user(username: str) -> dict[str, Any]:
    """
    Delete a Snowflake user.
    """
    try:
        conn = _get_connection()
    except RuntimeError as exc:
        logger.exception("Snowflake connection failed")
        return {"status": "error", "message": f"❌ Snowflake connection failed: {exc}"}

    if conn is None:
        return {
            "status": "success",
            "message": f"✅ [MOCK] User *{username}* deleted",
        }

    try:
        cur = conn.cursor()
        cur.execute(f"DROP USER IF EXISTS {username}")
        conn.close()
        logger.info("Snowflake user %s deleted", username)
        return {
            "status": "success",
            "message": f"✅ User *{username}* deleted",
        }
    except Exception as exc:
        logger.exception("Snowflake delete_user failed")
        return {"status": "error", "message": f"❌ Error deleting user: {exc}"}


def reset_password(username: str) -> dict[str, Any]:
    """
    Reset a Snowflake user's password to a temporary value.
    """
    try:
        conn = _get_connection()
    except RuntimeError as exc:
        logger.exception("Snowflake connection failed")
        return {"status": "error", "message": f"❌ Snowflake connection failed: {exc}"}

    if conn is None:
        return {
            "status": "success",
            "message": f"✅ [MOCK] Password reset for user *{username}*",
        }

    try:
        cur = conn.cursor()
        temp_pass = f"TempR3s3t_{secrets.token_urlsafe(8)}1aA!@9"
        cur.execute(f"ALTER USER {username} SET PASSWORD='{temp_pass}' MUST_CHANGE_PASSWORD=TRUE")
        conn.close()
        logger.info("Password reset for Snowflake user %s", username)
        return {
            "status": "success",
            "message": f"✅ Password reset for user *{username}*. User must change on next login.",
        }
    except Exception as exc:
        logger.exception("Snowflake reset_password failed")
        return {"status": "error", "message": f"❌ Error resetting password: {exc}"}


def list_users() -> dict[str, Any]:
    """
    List Snowflake users. Returns mock data when credentials are absent.
    """
    try:
        conn = _get_connection()
    except Exception as exc:
        logger.exception("Snowflake list_users failed")
        return {"status": "error", "users": [], "message": f"❌ Snowflake list_users failed: {exc}"}

    if conn is None:
        return {
            "status": "success",
            "users": [
                {"name": "john", "role": "ANALYST", "status": "active"},
                {"name": "jane", "role": "ENGINEER", "status": "active"},
                {"name": "admin", "role": "ACCOUNTADMIN", "status": "active"},
            ],
        }

    try:
        cur = conn.cursor()
        cur.execute("SHOW USERS")
        rows = cur.fetchall()
        users = [{"name": r[0], "role": r[5] if len(r) > 5 else "N/A", "status": "active"} for r in rows]
        conn.close()
        return {"status": "success", "users": users}
    except Exception as exc:
        logger.exception("Snowflake list_users failed")
        return {"status": "error", "users": [], "message": f"❌ Error listing users: {exc}"}
