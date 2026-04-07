"""
DevFlow – Command parser.
Converts natural‑language‑style text commands into structured action dicts
that can be routed to the appropriate service.

Supported patterns:
  deploy <target>
  create_user username=<username> role=<role>
  delete_user username=<username>
  reset_password username=<username>
  invoke_lambda [<function_name>]
  list_users
  list_ec2
  start_ec2 <instance_id>
  stop_ec2 <instance_id>
  help
"""

from __future__ import annotations

import logging
from typing import Any

logger = logging.getLogger(__name__)


def parse_command(raw: str) -> dict[str, Any]:
    """
    Parse a raw command string and return a structured action dict.

    Args:
        raw: Free‑text command string, e.g. ``"deploy backend"`` or ``"create_user username=test"``.

    Returns:
        A dict with at least ``action`` and ``params`` keys.
        On parse failure the ``action`` is ``"unknown"``.
    """
    raw = raw.strip()
    
    # Remove the /devflow prefix if present (from slash commands or manual input)
    if raw.startswith("/devflow"):
        raw = raw[8:].strip()
        if not raw:
            help_text = (
                "🛠️ *DevFlow Commands*\n"
                "• `/devflow help` - Show this menu\n"
                "• `/devflow create_user username=<name> role=<role>` - Create a Snowflake user\n"
                "• `/devflow delete_user username=<name>` - Delete a Snowflake user\n"
                "• `/devflow reset_password username=<name>` - Reset a Snowflake user's password\n"
                "• `/devflow list_users` - List Snowflake users\n"
                "• `/devflow invoke_lambda [function_name]` - Invoke AWS Lambda\n"
                "• `/devflow list_ec2` - List AWS EC2 instances\n"
                "• `/devflow start_ec2 <instance_id>` - Start EC2 instance\n"
                "• `/devflow stop_ec2 <instance_id>` - Stop EC2 instance\n"
            )
            return {"action": "help", "params": {}, "message": help_text, "raw": raw}

    tokens = raw.split()
    if not tokens:
        return {"action": "unknown", "params": {}, "raw": raw}

    verb = tokens[0].lower()

    kwargs = {}
    pos_args = []
    for arg in tokens[1:]:
        if "=" in arg:
            k, v = arg.split("=", 1)
            kwargs[k] = v
        else:
            pos_args.append(arg)

    # ── Help ──
    if verb == "help":
        help_text = (
            "🛠️ *DevFlow Commands*\n"
            "• `/devflow help` - Show this menu\n"
            "• `/devflow create_user username=<name> role=<role>` - Create a Snowflake user\n"
            "• `/devflow delete_user username=<name>` - Delete a Snowflake user\n"
            "• `/devflow reset_password username=<name>` - Reset a Snowflake user's password\n"
            "• `/devflow list_users` - List Snowflake users\n"
            "• `/devflow invoke_lambda [function_name]` - Invoke AWS Lambda\n"
            "• `/devflow list_ec2` - List AWS EC2 instances\n"
            "• `/devflow start_ec2 <instance_id>` - Start EC2 instance\n"
            "• `/devflow stop_ec2 <instance_id>` - Stop EC2 instance\n"
            "\nType `/devflow` or `/devflow help` anytime for quick guidance."
        )
        return {"action": "help", "params": {}, "message": help_text, "raw": raw}

    # ── Deploy ──
    if verb == "deploy":
        target = kwargs.get("target") or (pos_args[0] if len(pos_args) > 0 else "backend")
        ref = kwargs.get("ref") or (pos_args[1] if len(pos_args) > 1 else "main")
        return {
            "action": "deploy",
            "params": {"target": target, "ref": ref},
            "raw": raw,
        }

    # ── Snowflake: create user ──
    if verb == "create_user":
        username = kwargs.get("username") or (pos_args[0] if len(pos_args) > 0 else "")
        if not username:
            return {"action": "error", "message": "❌ Missing parameter: `username` is required for `create_user`"}
        role = kwargs.get("role") or (pos_args[1] if len(pos_args) > 1 else "PUBLIC")
        return {
            "action": "create_user",
            "params": {"username": username, "role": role},
            "raw": raw,
        }

    # ── Snowflake: delete user ──
    if verb == "delete_user":
        username = kwargs.get("username") or (pos_args[0] if len(pos_args) > 0 else "")
        if not username:
            return {"action": "error", "message": "❌ Missing parameter: `username` is required for `delete_user`"}
        return {
            "action": "delete_user",
            "params": {"username": username},
            "raw": raw,
        }

    # ── Snowflake: reset password ──
    if verb == "reset_password":
        username = kwargs.get("username") or (pos_args[0] if len(pos_args) > 0 else "")
        if not username:
            return {"action": "error", "message": "❌ Missing parameter: `username` is required for `reset_password`"}
        return {
            "action": "reset_password",
            "params": {"username": username},
            "raw": raw,
        }

    # ── Snowflake: list users ──
    if verb == "list_users":
        return {"action": "list_users", "params": {}, "raw": raw}

    # ── AWS Lambda ──
    if verb == "invoke_lambda":
        fn = kwargs.get("function_name") or (pos_args[0] if len(pos_args) > 0 else None)
        return {
            "action": "invoke_lambda",
            "params": {"function_name": fn},
            "raw": raw,
        }

    # ── AWS EC2 ──
    if verb == "list_ec2":
        return {"action": "list_ec2", "params": {}, "raw": raw}

    if verb in ("start_ec2", "stop_ec2"):
        instance_id = kwargs.get("instance_id") or (pos_args[0] if len(pos_args) > 0 else "")
        if not instance_id:
            return {
                "action": "error",
                "message": "❌ Missing parameter: `instance_id` is required for `start_ec2` and `stop_ec2`",
                "raw": raw,
            }
        return {
            "action": verb,
            "params": {"instance_id": instance_id},
            "raw": raw,
        }

    # ── Fallback ──
    logger.warning("Unrecognised command: %s", raw)
    return {"action": "unknown", "params": {}, "raw": raw, "message": f"❌ Unrecognised command: `{raw}`. Type `/devflow help` to see available commands."}
