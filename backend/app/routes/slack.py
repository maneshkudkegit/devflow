"""
DevFlow – Slack slash-command integration.
"""

from __future__ import annotations

import logging
import time
from typing import Any

import requests
from fastapi import APIRouter, BackgroundTasks, Request
from fastapi.responses import JSONResponse

from app.core.database import SessionLocal
from app.models.logs import Log
from app.utils.parser import parse_command
from app.services import github_service, snowflake_service, aws_service

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/slack", tags=["slack"])


# =========================
# COMMAND ROUTER
# =========================
def _route_action(parsed: dict[str, Any]) -> dict[str, Any]:
    action = parsed.get("action", "unknown")
    params = parsed.get("params", {})

    if action == "deploy":
        return github_service.trigger_workflow(ref=params.get("ref", "main"))

    if action == "create_user":
        return snowflake_service.create_user(
            params["username"], params.get("role", "PUBLIC")
        )

    if action == "delete_user":
        return snowflake_service.delete_user(params["username"])

    if action == "reset_password":
        return snowflake_service.reset_password(params["username"])

    if action == "list_users":
        return snowflake_service.list_users()

    if action == "invoke_lambda":
        return aws_service.invoke_lambda(
            function_name=params.get("function_name")
        )

    if action == "list_ec2":
        return aws_service.list_ec2_instances()

    if action in ("start_ec2", "stop_ec2"):
        ec2_action = "start" if action == "start_ec2" else "stop"
        return aws_service.manage_ec2(params["instance_id"], ec2_action)

    if action in ("help", "error"):
        return {
            "status": action,
            "message": parsed.get("message", "Processed"),
        }

    return {
        "status": "error",
        "message": f"❌ Unknown command: `{parsed.get('raw', '')}`",
    }


# =========================
# ASYNC PROCESSOR
# =========================
def _process_slack_command_async(
    response_url: str,
    text: str,
    user_name: str,
    command: str,
) -> None:
    db = SessionLocal()

    try:
        parsed = parse_command(text)
        result = _route_action(parsed)

        # Save log
        entry = Log(
            action=parsed.get("raw", text),
            status=result.get("status", "unknown"),
            detail=result.get("message", ""),
            source="slack",
        )
        db.add(entry)
        db.commit()

        response_text = result.get("message", str(result))

        payload = {
            "response_type": "in_channel"
            if parsed.get("action") not in ("help", "error")
            else "ephemeral",
            "text": f"*DevFlow* ({user_name}):\n`{command} {text}`\n\n{response_text}",
        }

        if response_url:
            for attempt in range(1, 4):
                try:
                    resp = requests.post(
                        response_url,
                        json=payload,
                        headers={"Content-Type": "application/json"},
                        timeout=10,
                    )

                    logger.info(
                        "Slack response status: %s | body: %s",
                        resp.status_code,
                        resp.text,
                    )

                    resp.raise_for_status()
                    logger.info("✅ Async Slack response sent")
                    break

                except requests.RequestException as e:
                    logger.warning("Retry %d failed: %s", attempt, e)
                    time.sleep(2 ** attempt)

    except Exception as e:
        logger.exception("❌ Slack async error")

        error_payload = {
            "response_type": "ephemeral",
            "text": f"❌ DevFlow Error:\n{str(e)}",
        }

        if response_url:
            try:
                requests.post(
                    response_url,
                    json=error_payload,
                    headers={"Content-Type": "application/json"},
                    timeout=5,
                )
            except Exception:
                pass

    finally:
        db.close()


# =========================
# MAIN SLACK ENDPOINT (FIXED)
# =========================
@router.post("/commands")
async def slack_command(request: Request, background_tasks: BackgroundTasks):
    form = await request.form()
    data = dict(form)

    # 🔥 DEBUG (keep this for now)
    logger.info("🔥 FULL SLACK PAYLOAD: %s", data)

    text = data.get("text", "")
    user_name = data.get("user_name", "unknown")
    command = data.get("command", "/devflow")
    response_url = data.get("response_url", "")

    background_tasks.add_task(
        _process_slack_command_async,
        response_url=response_url,
        text=text,
        user_name=user_name,
        command=command,
    )

    # ✅ Immediate Slack response (visible instantly)
    return JSONResponse(
        content={
            "response_type": "in_channel",
            "text": f"⏳ Processing `{command} {text}`...",
        }
    )