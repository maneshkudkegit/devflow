"""
DevFlow – AWS service.
Invokes Lambda functions and optionally manages EC2 instances.
"""

from __future__ import annotations

import json
import logging
from typing import Any

from app.core.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


def _get_lambda_client():
    """Return a boto3 Lambda client, or None if credentials are missing."""
    if (
        not settings.AWS_ACCESS_KEY_ID
        or settings.AWS_ACCESS_KEY_ID.startswith("your")
        or not settings.AWS_SECRET_ACCESS_KEY
        or settings.AWS_SECRET_ACCESS_KEY.startswith("your")
    ):
        logger.warning("AWS credentials not configured – running in mock mode")
        return None

    import boto3  # type: ignore[import-untyped]

    return boto3.client(
        "lambda",
        region_name=settings.AWS_REGION,
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
    )


def _get_ec2_client():
    """Return a boto3 EC2 client, or None if credentials are missing."""
    if (
        not settings.AWS_ACCESS_KEY_ID
        or settings.AWS_ACCESS_KEY_ID.startswith("your")
        or not settings.AWS_SECRET_ACCESS_KEY
        or settings.AWS_SECRET_ACCESS_KEY.startswith("your")
    ):
        return None

    import boto3

    return boto3.client(
        "ec2",
        region_name=settings.AWS_REGION,
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
    )


def invoke_lambda(
    function_name: str | None = None,
    payload: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """
    Invoke an AWS Lambda function synchronously.

    Args:
        function_name: Lambda function name (defaults to env config).
        payload: JSON‑serialisable payload dict.

    Returns:
        Dict with ``status`` and ``response`` keys.
    """
    fn = function_name or settings.AWS_LAMBDA_FUNCTION
    client = _get_lambda_client()

    if client is None:
        return {
            "status": "success",
            "message": f"[MOCK] Lambda '{fn}' invoked",
            "response": {"statusCode": 200, "body": "mock response"},
        }

    try:
        resp = client.invoke(
            FunctionName=fn,
            InvocationType="RequestResponse",
            Payload=json.dumps(payload or {}),
        )
        body = json.loads(resp["Payload"].read())
        logger.info("Lambda %s invoked successfully", fn)
        return {"status": "success", "message": f"Lambda '{fn}' invoked", "response": body}
    except Exception as exc:
        logger.exception("Lambda invocation failed")
        return {"status": "error", "message": str(exc)}


def list_ec2_instances() -> dict[str, Any]:
    """List EC2 instances (or return mock data)."""
    client = _get_ec2_client()

    if client is None:
        return {
            "status": "success",
            "instances": [
                {"id": "i-0abc1234", "type": "t3.micro", "state": "running"},
                {"id": "i-0def5678", "type": "t3.small", "state": "stopped"},
            ],
        }

    try:
        resp = client.describe_instances()
        instances = []
        for res in resp["Reservations"]:
            for inst in res["Instances"]:
                instances.append(
                    {
                        "id": inst["InstanceId"],
                        "type": inst["InstanceType"],
                        "state": inst["State"]["Name"],
                    }
                )
        return {"status": "success", "instances": instances}
    except Exception as exc:
        logger.exception("EC2 list failed")
        return {"status": "error", "instances": [], "message": str(exc)}


def manage_ec2(instance_id: str, action: str) -> dict[str, Any]:
    """
    Start or stop an EC2 instance.

    Args:
        instance_id: The EC2 instance ID.
        action: ``start`` or ``stop``.
    """
    client = _get_ec2_client()

    if client is None:
        return {
            "status": "success",
            "message": f"[MOCK] EC2 {instance_id} → {action}",
        }

    try:
        if action == "start":
            client.start_instances(InstanceIds=[instance_id])
        elif action == "stop":
            client.stop_instances(InstanceIds=[instance_id])
        else:
            return {"status": "error", "message": f"Unknown EC2 action: {action}"}
        return {"status": "success", "message": f"EC2 {instance_id} → {action}"}
    except Exception as exc:
        logger.exception("EC2 manage failed")
        return {"status": "error", "message": str(exc)}
