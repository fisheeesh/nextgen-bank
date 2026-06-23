from datetime import date

from pydantic import field_validator
from pydantic_extra_types.country import CountryShortName
from pydantic_extra_types.phone_numbers import PhoneNumber
from sqlmodel import Field, SQLModel

from ..auth.schema import RoleChoicesSchema
from .enums import (
    EmploymentStatusEnum,
    GenderEnum,
    IdentificationTypeEnum,
    MaritalStatusEnum,
    SalutaionEnum,
)
from .utils import validate_id_dates


class ProfileBaseSchema(SQLModel):
    title: SalutaionEnum
    gender: GenderEnum
    date_of_birth: date
    country_of_birth: CountryShortName
    place_of_birth: str
    marital_status: MaritalStatusEnum
    means_of_identification: IdentificationTypeEnum
    id_issue_date: date
    id_expiry_date: date
    passport_number: str
    nationality: str
    phone_number: PhoneNumber
    address: str
    city: str
    country: str
    employement_status: EmploymentStatusEnum
    employer_name: str
    employer_address: str
    employer_city: str | None = Field(default=None)
    employer_country: CountryShortName
    annual_income: float
    date_of_employment: date
    profile_photo_url: str | None = Field(default=None)
    id_photo_url: str | None = Field(default=None)
    signature_photo_url: str | None = Field(default=None)


class ProfileCreateSchema(ProfileBaseSchema):
    @field_validator("id_expiry_date")
    def validate_id_dates(cls, v, values):
        if "id_issue_date" in values.data:
            validate_id_dates(values.data["id_issue_date"], v)
        return v


class ProfileUpdateSchema(ProfileBaseSchema):
    title: SalutaionEnum | None = None
    gender: GenderEnum | None = None
    date_of_birth: date | None = None
    country_of_birth: CountryShortName | None = None
    place_of_birth: str | None = None
    marital_status: MaritalStatusEnum | None = None
    means_of_identification: IdentificationTypeEnum | None = None
    id_issue_date: date | None = None
    id_expiry_date: date | None = None
    passport_number: str | None = None
    nationality: str | None = None
    phone_number: PhoneNumber | None = None
    address: str | None = None
    city: str | None = None
    country: str | None = None
    employement_status: EmploymentStatusEnum | None = None
    employer_name: str | None = None
    employer_address: str | None = None
    employer_city: str | None = None
    employer_country: CountryShortName | None = None
    annual_income: float | None = None
    date_of_employment: date | None = None

    @field_validator("id_expiry_date")
    def validate_id_dates(cls, v: date | None, values) -> date | None:
        if v is not None and "id_issue_date" in values.data:
            validate_id_dates(values.data["id_issue_date"], v)
        return v


class ProfileResponseSchema(SQLModel):
    username: str
    first_name: str
    middle_name: str
    last_name: str
    email: str
    id_no: str
    role: RoleChoicesSchema
    profile: ProfileBaseSchema | None

    # ? help us convert the database objects to a response object
    class Config:
        from_attributes = True


class PaginatedProfileResponseSchema(SQLModel):
    profiles: list[ProfileResponseSchema]
    total: int
    skip: int
    limit: int
