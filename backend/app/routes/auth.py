from fastapi import APIRouter, Depends, HTTPException, status

from app.controllers import auth as auth_controller
from app.database.validation import (
    GoogleAuthData,
    LoginData,
    RefreshTokenData,
    RegisterData,
)
from app.middleware.auth import get_current_user
from app.services.auth import EmailAlreadyExistsError


router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
)


@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register(
    data: RegisterData,
):
    try:
        return await auth_controller.register(
            name=data.name,
            email=data.email,
            password=data.password,
        )
    except EmailAlreadyExistsError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="An account with this email already exists.",
        ) from exc


@router.post("/login")
async def login(
    data: LoginData,
):
    return await auth_controller.login(
        email=data.email,
        password=data.password,
    )


@router.post("/google")
async def google_login(
    data: GoogleAuthData,
):
    return await auth_controller.google_login(
        credential=data.credential,
    )


@router.post("/refresh")
async def refresh(
    data: RefreshTokenData,
):
    return await auth_controller.refresh(
        refresh_token=data.refresh_token,
    )


@router.post("/logout")
async def logout(
    data: RefreshTokenData,
):
    return await auth_controller.logout(
        refresh_token=data.refresh_token,
    )


@router.get("/me")
async def get_me(
    current_user=Depends(get_current_user),
):
    return await auth_controller.get_me(
        current_user,
    )