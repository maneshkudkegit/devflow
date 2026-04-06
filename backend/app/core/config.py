"""
DevFlow – Core configuration loaded from environment variables.
Uses pydantic‑settings so every value is validated on startup.
"""

from __future__ import annotations

import os
from functools import lru_cache

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application‑wide settings sourced from *.env* file or OS env."""

    # ── Slack ──
    SLACK_BOT_TOKEN: str = ""
    SLACK_SIGNING_SECRET: str = ""

    # ── GitHub ──
    GITHUB_TOKEN: str = ""
    GITHUB_OWNER: str = ""
    GITHUB_REPO: str = ""
    GITHUB_WORKFLOW_ID: str = "deploy.yml"

    # ── Snowflake ──
    SNOWFLAKE_ACCOUNT: str = ""
    SNOWFLAKE_USER: str = ""
    SNOWFLAKE_PASSWORD: str = ""
    SNOWFLAKE_WAREHOUSE: str = "COMPUTE_WH"
    SNOWFLAKE_DATABASE: str = ""
    SNOWFLAKE_ROLE: str = "ACCOUNTADMIN"

    # ── AWS ──
    AWS_ACCESS_KEY_ID: str = ""
    AWS_SECRET_ACCESS_KEY: str = ""
    AWS_REGION: str = "us-east-1"
    AWS_LAMBDA_FUNCTION: str = ""

    # ── Database ──
    DATABASE_URL: str = "sqlite:///./devflow.db"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache()
def get_settings() -> Settings:
    """Return cached settings instance (singleton pattern)."""
    return Settings()
