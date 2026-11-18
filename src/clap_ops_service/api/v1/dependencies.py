from typing import Annotated
from uuid import UUID

import jwt
from fastapi import Depends, Header, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from clap_ops_service.database import get_db
from clap_ops_service.database.models import Admin, Fleet, FleetMembership
from clap_ops_service.services.auth.jwt import decode_access_token

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/v1/auth/login")


def get_current_admin(
    token: Annotated[str, Depends(oauth2_scheme)],
    db: Session = Depends(get_db),
) -> Admin:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = decode_access_token(token)
        admin_id = int(payload["sub"])
    except (jwt.InvalidTokenError, KeyError, TypeError, ValueError) as error:
        raise credentials_exception from error

    admin = db.query(Admin).filter(Admin.id == admin_id).first()
    if admin is None:
        raise credentials_exception
    return admin


def get_authorized_fleet(
    fleet_id: Annotated[UUID, Header(alias="X-Fleet-ID")],
    db: Session = Depends(get_db),
    current_admin: Admin = Depends(get_current_admin),
) -> Fleet:
    fleet = db.query(Fleet).filter(Fleet.id == fleet_id).first()
    if fleet is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Fleet not found",
        )

    if current_admin.is_superadmin:
        return fleet

    membership = (
        db.query(FleetMembership)
        .filter(
            FleetMembership.admin_id == current_admin.id,
            FleetMembership.fleet_id == fleet.id,
        )
        .first()
    )
    if membership is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have access to this fleet",
        )
    return fleet
