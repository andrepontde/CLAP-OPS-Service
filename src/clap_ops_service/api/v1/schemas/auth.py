from uuid import UUID

from pydantic import BaseModel, EmailStr, Field


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=255)


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class FleetMembershipResponse(BaseModel):
    id: UUID
    name: str
    role: str = Field(pattern="^(MANAGER|MEMBER)$")


class CurrentAdminResponse(BaseModel):
    id: UUID
    email: EmailStr
    is_superadmin: bool
    fleets: list[FleetMembershipResponse]
