"""
DevFlow – GitHub Actions service.
Triggers workflow dispatch events via the GitHub REST API v3.
"""

from __future__ import annotations

import logging
from typing import Any

import requests

from app.core.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

GITHUB_API = "https://api.github.com"


def _headers() -> dict[str, str]:
    """Build authorization headers for GitHub API calls."""
    return {
        "Accept": "application/vnd.github+json",
        "Authorization": f"Bearer {settings.GITHUB_TOKEN}",
        "X-GitHub-Api-Version": "2022-11-28",
    }


def trigger_workflow(
    ref: str = "main",
    inputs: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """
    Trigger a GitHub Actions workflow via the *workflow_dispatch* event.

    Args:
        ref: Git ref (branch/tag) to run the workflow on.
        inputs: Optional key‑value inputs passed to the workflow.

    Returns:
        A dict with ``status`` and ``message`` keys.
    """
    if not settings.GITHUB_TOKEN:
        logger.warning("GITHUB_TOKEN not configured – returning mock response")
        return {
            "status": "success",
            "message": f"[MOCK] Workflow '{settings.GITHUB_WORKFLOW_ID}' triggered on ref={ref}",
        }

    url = (
        f"{GITHUB_API}/repos/{settings.GITHUB_OWNER}/{settings.GITHUB_REPO}"
        f"/actions/workflows/{settings.GITHUB_WORKFLOW_ID}/dispatches"
    )
    payload: dict[str, Any] = {"ref": ref}
    if inputs:
        payload["inputs"] = inputs

    try:
        resp = requests.post(url, json=payload, headers=_headers(), timeout=15)
        if resp.status_code == 204:
            logger.info("GitHub workflow dispatched successfully")
            return {
                "status": "success",
                "message": f"Workflow '{settings.GITHUB_WORKFLOW_ID}' triggered on ref={ref}",
            }
        logger.error("GitHub API error %s: %s", resp.status_code, resp.text)
        return {
            "status": "error",
            "message": f"GitHub API returned {resp.status_code}: {resp.text}",
        }
    except requests.RequestException as exc:
        logger.exception("GitHub request failed")
        return {"status": "error", "message": str(exc)}


def list_workflow_runs(per_page: int = 10) -> dict[str, Any]:
    """
    Fetch recent workflow runs for the configured repository.

    Returns:
        A dict with ``status`` and ``runs`` keys.
    """
    if not settings.GITHUB_TOKEN:
        return {
            "status": "success",
            "runs": [
                {"id": 1, "name": "Deploy Backend", "status": "completed", "conclusion": "success"},
                {"id": 2, "name": "Deploy Frontend", "status": "completed", "conclusion": "success"},
                {"id": 3, "name": "Run Tests", "status": "in_progress", "conclusion": None},
            ],
        }

    url = (
        f"{GITHUB_API}/repos/{settings.GITHUB_OWNER}/{settings.GITHUB_REPO}"
        f"/actions/runs?per_page={per_page}"
    )
    try:
        resp = requests.get(url, headers=_headers(), timeout=15)
        resp.raise_for_status()
        data = resp.json()
        runs = [
            {
                "id": r["id"],
                "name": r["name"],
                "status": r["status"],
                "conclusion": r["conclusion"],
            }
            for r in data.get("workflow_runs", [])
        ]
        return {"status": "success", "runs": runs}
    except requests.RequestException as exc:
        logger.exception("Failed to list workflow runs")
        return {"status": "error", "runs": [], "message": str(exc)}
