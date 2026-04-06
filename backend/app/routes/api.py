"""
DevFlow – REST API routes consumed by the React frontend.

Endpoints:
  POST /api/deploy        – trigger a GitHub Actions workflow
  POST /api/users         – create a Snowflake user
  GET  /api/users         – list Snowflake users
  POST /api/users/reset   – reset a Snowflake user password
  GET  /api/logs          – fetch activity logs
  POST /api/command       – run a free‑text command (like CommandBox)
  GET  /api/stats         – dashboard summary stats
  POST /api/aws/lambda    – invoke a Lambda function
  GET  /api/aws/ec2       – list EC2 instances
"""

from __future__ import annotations

import logging
from typing import Any

from fastapi import APIRouter, Depends, Body, Path
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.logs import Log
from app.services import github_service, snowflake_service, aws_service
from app.utils.parser import parse_command

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api", tags=["api"])


# ─────────────────────────── helpers ───────────────────────────

def _log(db: Session, action: str, status: str, detail: str = "", source: str = "api") -> Log:
    """Persist an audit log entry."""
    entry = Log(action=action, status=status, detail=detail, source=source)
    db.add(entry)
    db.commit()
    db.refresh(entry)
    return entry


def _route_action(parsed: dict[str, Any]) -> dict[str, Any]:
    """Dispatch a parsed command to the corresponding service."""
    action = parsed["action"]
    params = parsed.get("params", {})

    if action == "help":
        return {"status": "success", "message": parsed.get("message", "")}    
    if action == "error":
        return {"status": "error", "message": parsed.get("message", "Unknown command")}
    if action == "deploy":
        return github_service.trigger_workflow(ref=params.get("ref", "main"))
    if action == "create_user":
        return snowflake_service.create_user(params["username"], params.get("role", "PUBLIC"))
    if action == "reset_password":
        return snowflake_service.reset_password(params["username"])
    if action == "delete_user":
        return snowflake_service.delete_user(params["username"])
    if action == "list_users":
        return snowflake_service.list_users()
    if action == "invoke_lambda":
        return aws_service.invoke_lambda(function_name=params.get("function_name"))
    if action == "list_ec2":
        return aws_service.list_ec2_instances()
    if action in ("start_ec2", "stop_ec2"):
        ec2_action = "start" if action == "start_ec2" else "stop"
        return aws_service.manage_ec2(params["instance_id"], ec2_action)

    return {"status": "error", "message": f"Unknown action: {action}"}


# ─────────────────────────── endpoints ─────────────────────────

@router.post("/deploy")
def deploy(
    target: str = Body("backend", embed=True),
    ref: str = Body("main", embed=True),
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    """Trigger a GitHub Actions deployment workflow."""
    result = github_service.trigger_workflow(ref=ref)
    _log(db, action=f"deploy:{target}", status=result["status"], detail=result.get("message", ""))
    return result


@router.post("/users")
def create_user(
    username: str = Body(..., embed=True),
    role: str = Body("PUBLIC", embed=True),
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    """Create a Snowflake user with the given role."""
    result = snowflake_service.create_user(username, role)
    _log(db, action=f"create_user:{username}", status=result["status"], detail=result.get("message", ""))
    return result


@router.get("/users")
def list_users() -> dict[str, Any]:
    """List all Snowflake users."""
    return snowflake_service.list_users()


@router.post("/users/reset")
def reset_password(
    username: str = Body(..., embed=True),
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    """Reset a Snowflake user's password."""
    result = snowflake_service.reset_password(username)
    _log(db, action=f"reset_password:{username}", status=result["status"], detail=result.get("message", ""))
    return result


@router.delete("/users/{username}")
def delete_user(
    username: str = Path(..., min_length=1),
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    """Delete a Snowflake user."""
    result = snowflake_service.delete_user(username)
    _log(db, action=f"delete_user:{username}", status=result["status"], detail=result.get("message", ""))
    return result


@router.get("/logs")
def get_logs(limit: int = 50, db: Session = Depends(get_db)) -> list[dict[str, Any]]:
    """Fetch the most recent activity log entries."""
    logs = db.query(Log).order_by(Log.timestamp.desc()).limit(limit).all()
    return [log.to_dict() for log in logs]


@router.delete("/logs/{log_id}")
def delete_log(
    log_id: int,
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    """Delete an activity log entry by ID."""
    log = db.get(Log, log_id)
    if not log:
        return {"status": "error", "message": "Log entry not found."}

    db.delete(log)
    db.commit()
    return {"status": "success", "message": f"✅ Log entry {log_id} deleted."}


@router.delete("/logs")
def delete_old_logs(
    days: int = 30,
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    """Delete activity log entries older than the specified number of days."""
    from datetime import datetime, timedelta
    
    cutoff = datetime.utcnow() - timedelta(days=days)
    deleted_count = db.query(Log).filter(Log.timestamp < cutoff).delete()
    db.commit()
    
    return {
        "status": "success", 
        "message": f"✅ Deleted {deleted_count} log entries older than {days} days."
    }


@router.post("/command")
def run_command(
    command: str = Body(..., embed=True),
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    """Parse and execute a free‑text command (powers the CommandBox)."""
    parsed = parse_command(command)
    result = _route_action(parsed)
    _log(
        db,
        action=parsed.get("raw", command),
        status=result.get("status", "unknown"),
        detail=result.get("message", ""),
    )
    return {"parsed": parsed, **result}


@router.get("/stats")
def dashboard_stats(db: Session = Depends(get_db)) -> dict[str, Any]:
    """Return aggregated stats for the Dashboard page."""
    total_logs = db.query(Log).count()
    total_deploys = db.query(Log).filter(Log.action.like("deploy%")).count()
    total_users_created = db.query(Log).filter(Log.action.like("create_user%")).count()
    recent = db.query(Log).order_by(Log.timestamp.desc()).limit(5).all()
    return {
        "total_actions": total_logs,
        "total_deployments": total_deploys,
        "total_users_created": total_users_created,
        "recent_logs": [l.to_dict() for l in recent],
    }


@router.post("/aws/lambda")
def invoke_lambda(
    function_name: str = Body(None, embed=True),
    payload: dict = Body(None, embed=True),
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    """Invoke an AWS Lambda function."""
    result = aws_service.invoke_lambda(function_name=function_name, payload=payload)
    _log(db, action=f"invoke_lambda:{function_name}", status=result["status"], detail=result.get("message", ""))
    return result


@router.get("/aws/ec2")
def list_ec2() -> dict[str, Any]:
    """List EC2 instances."""
    return aws_service.list_ec2_instances()
