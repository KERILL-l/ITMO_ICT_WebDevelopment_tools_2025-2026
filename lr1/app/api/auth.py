from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select

from app.core.database import get_session
from app.core.security import (
    create_access_token,
    hash_password,
    verify_password,
)
from app.models import User
from app.schemas import Token, UserLogin, UserRead, UserRegister

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=UserRead, status_code=status.HTTP_201_CREATED)
def register(data: UserRegister, session: Session = Depends(get_session)) -> User:
    existing = session.exec(
        select(User).where((User.email == data.email) | (User.username == data.username))
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email или username уже заняты")

    user = User(
        email=data.email,
        username=data.username,
        hashed_password=hash_password(data.password),
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


@router.post("/login", response_model=Token)
def login(data: UserLogin, session: Session = Depends(get_session)) -> Token:
    user = session.exec(select(User).where(User.email == data.email)).first()
    if user is None or not verify_password(data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Неверный email или пароль")

    token = create_access_token(user.id)
    return Token(access_token=token)
