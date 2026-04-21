"""
Webhook and tool-style endpoints for Vapi / voice agents.

Prefer POST /patients from tools; this route accepts nested payloads some stacks send.
See PROMPTS.md (save_patient tool shape).
"""

import json
import logging
from typing import Any

from fastapi import APIRouter, Body, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud import create_patient
from app.database import get_db
from app.schemas import ApiEnvelope, PatientCreate, PatientRead

logger = logging.getLogger(__name__)

router = APIRouter(tags=["webhook"])


def _extract_patient_dict(body: dict[str, Any]) -> dict[str, Any]:
    if "patient" in body and isinstance(body["patient"], dict):
        return body["patient"]
    if "arguments" in body and isinstance(body["arguments"], dict):
        return body["arguments"]
    msg = body.get("message")
    if isinstance(msg, dict):
        tool_calls = msg.get("toolCalls") or msg.get("toolCallList")
        if isinstance(tool_calls, list) and tool_calls:
            first = tool_calls[0]
            if isinstance(first, dict):
                fn = first.get("function") or first.get("toolCall")
                if isinstance(fn, dict) and isinstance(fn.get("arguments"), dict):
                    return fn["arguments"]
                args = first.get("arguments")
                if isinstance(args, dict):
                    return args
                if isinstance(args, str):
                    try:
                        parsed = json.loads(args)
                        if isinstance(parsed, dict):
                            return parsed
                    except json.JSONDecodeError:
                        pass
    return body


@router.post("/webhook", response_model=ApiEnvelope, status_code=201)
async def webhook_save_patient(
    body: dict[str, Any] = Body(...),
    session: AsyncSession = Depends(get_db),
) -> ApiEnvelope:
    """
    Accept a raw JSON body; normalize to PatientCreate when possible.
    Logs the incoming body for Vapi debugging (no secrets expected in patient fields).
    """
    logger.info("Webhook POST /webhook received keys: %s", list(body.keys()))
    payload = _extract_patient_dict(body)
    try:
        create = PatientCreate.model_validate(payload)
    except Exception as e:
        logger.warning("Webhook payload could not be validated as patient: %s", e)
        raise HTTPException(
            status_code=422,
            detail="Body must match patient fields (see POST /patients schema)",
        ) from e

    logger.info("Webhook creating patient: %s", create.model_dump(mode="json"))
    try:
        patient = await create_patient(session, create)
    except ValueError as e:
        raise HTTPException(status_code=409, detail=str(e)) from e

    out = PatientRead.model_validate(patient).model_dump(mode="json")
    logger.info("Webhook patient created: patient_id=%s", patient.patient_id)
    return ApiEnvelope(data=out, error=None)
