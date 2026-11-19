import jwt
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from clap_ops_service.api.v1.dependencies import get_current_admin
from clap_ops_service.api.v1.schemas.auth import (
    CurrentAdminResponse,
    FleetMembershipResponse,
    LoginRequest,
    TokenResponse,
)
from clap_ops_service.database import get_db
from clap_ops_service.database.models import Admin, Fleet, FleetMembership
from clap_ops_service.services.auth.auth_service import AuthService
from clap_ops_service.services.auth.jwt import revoke_token

auth_router = APIRouter(prefix="/auth", tags=["auth"])
security = HTTPBearer()


@auth_router.post(
    "/login",
    response_model=TokenResponse,
    status_code=status.HTTP_200_OK,
)
def login(
    login_request: LoginRequest,
    db: Session = Depends(get_db),
) -> TokenResponse:
    try:
        return AuthService(db, Admin).authenticate_user(
            login_request.email,
            login_request.password,
        )
    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(error),
            headers={"WWW-Authenticate": "Bearer"},
        ) from error


@auth_router.get("/me", response_model=CurrentAdminResponse)
def get_current_admin_profile(
    db: Session = Depends(get_db),
    current_admin: Admin = Depends(get_current_admin),
) -> CurrentAdminResponse:
    memberships = (
        db.query(FleetMembership, Fleet)
        .join(Fleet, Fleet.id == FleetMembership.fleet_id)
        .filter(FleetMembership.admin_id == current_admin.id)
        .order_by(Fleet.name)
        .all()
    )
    return CurrentAdminResponse(
        id=current_admin.id,
        email=current_admin.email,
        is_superadmin=current_admin.is_superadmin,
        fleets=[
            FleetMembershipResponse(
                id=fleet.id,
                name=fleet.name,
                role=membership.role,
            )
            for membership, fleet in memberships
        ],
    )


@auth_router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> None:
    try:
        revoke_token(credentials.credentials)
    except jwt.InvalidTokenError as error:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        ) from error
