import uuid
from datetime import date, datetime

from sqlalchemy import Date, DateTime, Index, String, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class Patient(Base):
    __tablename__ = "patients"
    __table_args__ = (
        Index("ix_patients_last_name", "last_name"),
        Index("ix_patients_phone_number", "phone_number"),
    )

    patient_id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    first_name: Mapped[str] = mapped_column(String(50))
    last_name: Mapped[str] = mapped_column(String(50))
    date_of_birth: Mapped[date] = mapped_column(Date)
    sex: Mapped[str] = mapped_column(String(32))
    phone_number: Mapped[str] = mapped_column(String(20))
    email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    address_line_1: Mapped[str] = mapped_column(String(200))
    address_line_2: Mapped[str | None] = mapped_column(String(200), nullable=True)
    city: Mapped[str] = mapped_column(String(100))
    state: Mapped[str] = mapped_column(String(2))
    zip_code: Mapped[str] = mapped_column(String(10))
    insurance_provider: Mapped[str | None] = mapped_column(String(200), nullable=True)
    insurance_member_id: Mapped[str | None] = mapped_column(String(100), nullable=True)
    preferred_language: Mapped[str] = mapped_column(String(50), default="English")
    emergency_contact_name: Mapped[str | None] = mapped_column(String(100), nullable=True)
    emergency_contact_phone: Mapped[str | None] = mapped_column(String(20), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
