from datetime import date, datetime, timezone
from enum import Enum

from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Patient
from app.schemas import PatientCreate, PatientUpdate, normalize_us_phone


async def get_patient_active(session: AsyncSession, patient_id: str) -> Patient | None:
    r = await session.execute(
        select(Patient).where(
            Patient.patient_id == patient_id,
            Patient.deleted_at.is_(None),
        )
    )
    return r.scalar_one_or_none()


async def get_active_by_phone(session: AsyncSession, phone: str) -> Patient | None:
    r = await session.execute(
        select(Patient).where(
            Patient.phone_number == phone,
            Patient.deleted_at.is_(None),
        )
    )
    return r.scalar_one_or_none()


async def list_patients(
    session: AsyncSession,
    *,
    last_name: str | None = None,
    date_of_birth: date | None = None,
    phone_number: str | None = None,
) -> list[Patient]:
    q = select(Patient).where(Patient.deleted_at.is_(None))
    if last_name is not None:
        q = q.where(func.lower(Patient.last_name) == last_name.strip().lower())
    if date_of_birth is not None:
        q = q.where(Patient.date_of_birth == date_of_birth)
    if phone_number is not None:
        normalized = normalize_us_phone(phone_number)
        q = q.where(Patient.phone_number == normalized)
    r = await session.execute(q.order_by(Patient.created_at.desc()))
    return list(r.scalars().all())


async def create_patient(session: AsyncSession, data: PatientCreate) -> Patient:
    existing = await get_active_by_phone(session, data.phone_number)
    if existing:
        raise ValueError("An active patient with this phone number already exists")

    patient = Patient(
        first_name=data.first_name,
        last_name=data.last_name,
        date_of_birth=data.date_of_birth,
        sex=data.sex.value,
        phone_number=data.phone_number,
        email=data.email,
        address_line_1=data.address_line_1,
        address_line_2=data.address_line_2,
        city=data.city,
        state=data.state,
        zip_code=data.zip_code,
        insurance_provider=data.insurance_provider,
        insurance_member_id=data.insurance_member_id,
        preferred_language=data.preferred_language or "English",
        emergency_contact_name=data.emergency_contact_name,
        emergency_contact_phone=data.emergency_contact_phone,
    )
    session.add(patient)
    await session.flush()
    await session.refresh(patient)
    return patient


async def update_patient(
    session: AsyncSession, patient: Patient, data: PatientUpdate
) -> Patient:
    payload = data.model_dump(exclude_unset=True)
    if not payload:
        return patient

    if "phone_number" in payload:
        other = await session.execute(
            select(Patient).where(
                and_(
                    Patient.phone_number == payload["phone_number"],
                    Patient.deleted_at.is_(None),
                    Patient.patient_id != patient.patient_id,
                )
            )
        )
        if other.scalar_one_or_none():
            raise ValueError("Another active patient already uses this phone number")

    for key, value in payload.items():
        if isinstance(value, Enum):
            value = value.value
        setattr(patient, key, value)

    patient.updated_at = datetime.now(timezone.utc)
    await session.flush()
    await session.refresh(patient)
    return patient


async def soft_delete_patient(session: AsyncSession, patient: Patient) -> Patient:
    patient.deleted_at = datetime.now(timezone.utc)
    patient.updated_at = patient.deleted_at
    await session.flush()
    await session.refresh(patient)
    return patient
