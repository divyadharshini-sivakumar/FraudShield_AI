from fastapi import APIRouter, Depends, Header, HTTPException
from firebase_admin import auth
from sqlalchemy.orm import Session

from app.core.firebase_admin import firebase_app
from app.db.session import get_db
from app.db.user_model import AppUser


router = APIRouter()


@router.post("/auth/login")
def firebase_login(
    authorization: str = Header(...),
    db: Session = Depends(get_db),
):
    if not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=401,
            detail="Invalid authorization header",
        )

    id_token = authorization.replace("Bearer ", "", 1).strip()

    try:
        decoded_token = auth.verify_id_token(
            id_token,
            app=firebase_app,
        )
    except Exception:
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired Firebase token",
        )

    firebase_uid = decoded_token.get("uid")
    email = decoded_token.get("email")
    name = decoded_token.get("name") or email

    if not firebase_uid or not email:
        raise HTTPException(
            status_code=400,
            detail="Firebase account information is incomplete",
        )

    user = (
        db.query(AppUser)
        .filter(AppUser.firebase_uid == firebase_uid)
        .first()
    )

    if not user:
        user = AppUser(
            firebase_uid=firebase_uid,
            name=name,
            email=email,
            role="customer",
            is_active=True,
        )

        db.add(user)
        db.commit()
        db.refresh(user)

    if not user.is_active:
        raise HTTPException(
            status_code=403,
            detail="This user account has been disabled",
        )

    return {
        "id": user.id,
        "firebase_uid": user.firebase_uid,
        "name": user.name,
        "email": user.email,
        "role": user.role,
        "is_active": user.is_active,
    }