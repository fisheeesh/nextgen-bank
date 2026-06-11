from typing import TYPE_CHECKING
import uuid
from datetime import datetime, timezone

from pydantic import computed_field
from sqlalchemy import func, text
from sqlalchemy.dialects import postgresql as pg
from sqlmodel import Column, Field, Relationship

from .schema import BaseUserSchema, RoleChoicesSchema

if TYPE_CHECKING:
    from ..user_profile.models import Profile


class User(BaseUserSchema, table=True):
    id: uuid.UUID = Field(
        sa_column=Column(
            pg.UUID(as_uuid=True),
            primary_key=True,
        ),
        default_factory=uuid.uuid4,
    )
    hashed_password: str
    failed_login_attempts: int = Field(default=0, sa_type=pg.SMALLINT)
    last_failed_login: datetime | None = Field(
        default=None, sa_column=Column(pg.TIMESTAMP(timezone=True))
    )
    otp: str = Field(max_length=6, default="")
    otp_expiry_time: datetime | None = Field(
        default=None, sa_column=Column(pg.TIMESTAMP(timezone=True))
    )
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column=Column(
            pg.TIMESTAMP(timezone=True),
            nullable=False,
            server_default=text("CURRENT_TIMESTAMP"),
        ),
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column=Column(
            pg.TIMESTAMP(timezone=True),
            nullable=False,
            onupdate=func.current_timestamp(),
        ),
    )

    profile: "Profile" = Relationship(
        back_populates="user",
        sa_relationship_kwargs={
            # ? This tells use the relationship is 1 to 1 relationship
            # ? If we dun specify, sqlmodel will asuume one to many
            "uselist": False,
            # ? for eager loading
            "lazy": "selectin",
        },
    )

    # $ set some fields that are not going to be stored in the database, but computed on other fields
    @computed_field
    @property
    def full_name(self) -> str:
        full_name = f"{self.first_name} {self.middle_name + ' ' if self.middle_name else ''}{self.last_name}"
        return full_name.title().strip()

    def has_role(self, role: RoleChoicesSchema) -> bool:
        return self.role.value == role.value
