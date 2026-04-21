import logging
from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud import (
    create_patient,
    get_patient_active,
    list_patients,
    soft_delete_patient,
    update_patient,
)
from app.database import get_db
from app.schemas import ApiEnvelope, PatientCreate, PatientRead, PatientUpdate

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/patients", tags=["patients"])


@router.get("", response_model=ApiEnvelope)
async def get_patients(
    last_name: str | None = Query(None),
    date_of_birth: date | None = Query(None),
    phone_number: str | None = Query(None),
    session: AsyncSession = Depends(get_db),
) -> ApiEnvelope:
    rows = await list_patients(
        session,
        last_name=last_name,
        date_of_birth=date_of_birth,
        phone_number=phone_number,
    )
    data = [PatientRead.model_validate(r).model_dump(mode="json") for r in rows]
    return ApiEnvelope(data=data, error=None)


@router.get("/{patient_id}", response_model=ApiEnvelope)
async def get_patient(
    patient_id: str,
    session: AsyncSession = Depends(get_db),
) -> ApiEnvelope:
    patient = await get_patient_active(session, patient_id)
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    return ApiEnvelope(
        data=PatientRead.model_validate(patient).model_dump(mode="json"),
        error=None,
    )


@router.post("", response_model=ApiEnvelope, status_code=201)
async def post_patient(
    body: PatientCreate,
    session: AsyncSession = Depends(get_db),
) -> ApiEnvelope:
    logger.info(
        "Creating patient from API: %s",
        body.model_dump(mode="json"),
    )
    try:
        patient = await create_patient(session, body)
    except ValueError as e:
        raise HTTPException(status_code=409, detail=str(e)) from e
    out = PatientRead.model_validate(patient).model_dump(mode="json")
    logger.info("Patient created: patient_id=%s", patient.patient_id)
    return ApiEnvelope(data=out, error=None)


@router.put("/{patient_id}", response_model=ApiEnvelope)
async def put_patient(
    patient_id: str,
    body: PatientUpdate,
    session: AsyncSession = Depends(get_db),
) -> ApiEnvelope:
    if not body.model_fields_set:
        raise HTTPException(status_code=400, detail="No fields to update")
    patient = await get_patient_active(session, patient_id)
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    try:
        updated = await update_patient(session, patient, body)
    except ValueError as e:
        raise HTTPException(status_code=409, detail=str(e)) from e
    return ApiEnvelope(
        data=PatientRead.model_validate(updated).model_dump(mode="json"),
        error=None,
    )


@router.delete("/{patient_id}", response_model=ApiEnvelope)
async def delete_patient(
    patient_id: str,
    session: AsyncSession = Depends(get_db),
) -> ApiEnvelope:
    patient = await get_patient_active(session, patient_id)
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    await soft_delete_patient(session, patient)
    return ApiEnvelope(
        data={"patient_id": patient_id, "deleted": True},
        error=None,
    )
