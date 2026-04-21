import re
from datetime import date, datetime, timezone
from enum import Enum
from typing import Any, Self

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator, model_validator

US_STATE_CODES = frozenset(
    {
        "AL",
        "AK",
        "AZ",
        "AR",
        "CA",
        "CO",
        "CT",
        "DE",
        "FL",
        "GA",
        "HI",
        "ID",
        "IL",
        "IN",
        "IA",
        "KS",
        "KY",
        "LA",
        "ME",
        "MD",
        "MA",
        "MI",
        "MN",
        "MS",
        "MO",
        "MT",
        "NE",
        "NV",
        "NH",
        "NJ",
        "NM",
        "NY",
        "NC",
        "ND",
        "OH",
        "OK",
        "OR",
        "PA",
        "RI",
        "SC",
        "SD",
        "TN",
        "TX",
        "UT",
        "VT",
        "VA",
        "WA",
        "WV",
        "WI",
        "WY",
        "DC",
    }
)

NAME_PATTERN = re.compile(r"^[A-Za-z\u00C0-\u024F\s'\-.]+$")


class Sex(str, Enum):
    male = "Male"
    female = "Female"
    other = "Other"
    decline = "Decline to Answer"


def normalize_us_phone(value: str) -> str:
    digits = re.sub(r"\D", "", value)
    if len(digits) == 11 and digits.startswith("1"):
        digits = digits[1:]
    if len(digits) != 10:
        raise ValueError("Phone must be a valid U.S. 10-digit number")
    return digits


class PatientCreate(BaseModel):
    first_name: str = Field(..., min_length=1, max_length=50)
    last_name: str = Field(..., min_length=1, max_length=50)
    date_of_birth: date
    sex: Sex
    phone_number: str
    email: EmailStr | None = None

    @field_validator("email", mode="before")
    @classmethod
    def empty_email(cls, v: Any) -> Any:
        if v == "":
            return None
        return v
    address_line_1: str = Field(..., min_length=1, max_length=200)
    address_line_2: str | None = Field(None, max_length=200)
    city: str = Field(..., min_length=1, max_length=100)
    state: str = Field(..., min_length=2, max_length=2)
    zip_code: str
    insurance_provider: str | None = Field(None, max_length=200)
    insurance_member_id: str | None = Field(None, max_length=100)
    preferred_language: str | None = Field(None, max_length=50)
    emergency_contact_name: str | None = Field(None, max_length=100)
    emergency_contact_phone: str | None = None

    @field_validator("first_name", "last_name")
    @classmethod
    def validate_name_chars(cls, v: str) -> str:
        v = v.strip()
        if not NAME_PATTERN.fullmatch(v):
            raise ValueError(
                "Name may only contain letters, spaces, hyphens, apostrophes, and periods"
            )
        return v

    @field_validator("date_of_birth")
    @classmethod
    def dob_not_future(cls, v: date) -> date:
        if v > date.today():
            raise ValueError("Date of birth cannot be in the future")
        return v

    @field_validator("phone_number")
    @classmethod
    def phone_normalized(cls, v: str) -> str:
        return normalize_us_phone(v)

    @field_validator("state")
    @classmethod
    def state_us_abbrev(cls, v: str) -> str:
        u = v.strip().upper()
        if u not in US_STATE_CODES:
            raise ValueError("state must be a valid 2-letter U.S. state or DC abbreviation")
        return u

    @field_validator("zip_code")
    @classmethod
    def zip_us(cls, v: str) -> str:
        s = v.strip()
        if not re.fullmatch(r"\d{5}(-\d{4})?", s):
            raise ValueError("zip_code must be 5 digits or ZIP+4 (12345-6789)")
        return s

    @field_validator("insurance_member_id")
    @classmethod
    def insurance_id_alnum(cls, v: str | None) -> str | None:
        if v is None or v == "":
            return None
        if not re.fullmatch(r"[A-Za-z0-9]+", v):
            raise ValueError("insurance_member_id must be alphanumeric")
        return v

    @field_validator("emergency_contact_phone")
    @classmethod
    def emergency_phone(cls, v: str | None) -> str | None:
        if v is None or v == "":
            return None
        return normalize_us_phone(v)

    @field_validator("preferred_language")
    @classmethod
    def default_language(cls, v: str | None) -> str:
        if v is None or (isinstance(v, str) and not v.strip()):
            return "English"
        return v.strip()


class PatientUpdate(BaseModel):
    first_name: str | None = Field(None, min_length=1, max_length=50)
    last_name: str | None = Field(None, min_length=1, max_length=50)
    date_of_birth: date | None = None
    sex: Sex | None = None
    phone_number: str | None = None
    email: EmailStr | None = None

    @field_validator("email", mode="before")
    @classmethod
    def empty_email(cls, v: Any) -> Any:
        if v == "":
            return None
        return v
    address_line_1: str | None = Field(None, min_length=1, max_length=200)
    address_line_2: str | None = Field(None, max_length=200)
    city: str | None = Field(None, min_length=1, max_length=100)
    state: str | None = Field(None, min_length=2, max_length=2)
    zip_code: str | None = None
    insurance_provider: str | None = Field(None, max_length=200)
    insurance_member_id: str | None = Field(None, max_length=100)
    preferred_language: str | None = Field(None, max_length=50)
    emergency_contact_name: str | None = Field(None, max_length=100)
    emergency_contact_phone: str | None = None

    @field_validator("first_name", "last_name")
    @classmethod
    def validate_name_chars(cls, v: str | None) -> str | None:
        if v is None:
            return None
        v = v.strip()
        if not NAME_PATTERN.fullmatch(v):
            raise ValueError(
                "Name may only contain letters, spaces, hyphens, apostrophes, and periods"
            )
        return v

    @field_validator("date_of_birth")
    @classmethod
    def dob_not_future(cls, v: date | None) -> date | None:
        if v is None:
            return None
        if v > date.today():
            raise ValueError("Date of birth cannot be in the future")
        return v

    @field_validator("phone_number")
    @classmethod
    def phone_normalized(cls, v: str | None) -> str | None:
        if v is None:
            return None
        return normalize_us_phone(v)

    @field_validator("state")
    @classmethod
    def state_us_abbrev(cls, v: str | None) -> str | None:
        if v is None:
            return None
        u = v.strip().upper()
        if u not in US_STATE_CODES:
            raise ValueError("state must be a valid 2-letter U.S. state or DC abbreviation")
        return u

    @field_validator("zip_code")
    @classmethod
    def zip_us(cls, v: str | None) -> str | None:
        if v is None:
            return None
        s = v.strip()
        if not re.fullmatch(r"\d{5}(-\d{4})?", s):
            raise ValueError("zip_code must be 5 digits or ZIP+4 (12345-6789)")
        return s

    @field_validator("insurance_member_id")
    @classmethod
    def insurance_id_alnum(cls, v: str | None) -> str | None:
        if v is None or v == "":
            return None
        if not re.fullmatch(r"[A-Za-z0-9]+", v):
            raise ValueError("insurance_member_id must be alphanumeric")
        return v

    @field_validator("emergency_contact_phone")
    @classmethod
    def emergency_phone(cls, v: str | None) -> str | None:
        if v is None or v == "":
            return None
        return normalize_us_phone(v)

    @model_validator(mode="after")
    def reject_null_required_columns(self) -> Self:
        required_if_set = (
            "first_name",
            "last_name",
            "date_of_birth",
            "sex",
            "phone_number",
            "address_line_1",
            "city",
            "state",
            "zip_code",
            "preferred_language",
        )
        for key in required_if_set:
            if key in self.model_fields_set and getattr(self, key) is None:
                raise ValueError(f"{key} cannot be cleared; omit the field to keep existing value")
        return self


class PatientRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    patient_id: str
    first_name: str
    last_name: str
    date_of_birth: date
    sex: str
    phone_number: str
    email: str | None
    address_line_1: str
    address_line_2: str | None
    city: str
    state: str
    zip_code: str
    insurance_provider: str | None
    insurance_member_id: str | None
    preferred_language: str
    emergency_contact_name: str | None
    emergency_contact_phone: str | None
    created_at: datetime
    updated_at: datetime
    deleted_at: datetime | None


class ApiEnvelope(BaseModel):
    data: Any | None = None
    error: dict[str, Any] | None = None
