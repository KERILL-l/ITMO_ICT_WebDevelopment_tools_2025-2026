from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import selectinload
from sqlmodel import Session, select

from app.api.deps import get_current_user
from app.core.database import get_session
from app.models import Hackathon, User
from app.schemas import HackathonCreate, HackathonDetailRead, HackathonRead, HackathonUpdate

router = APIRouter(prefix="/hackathons", tags=["hackathons"])


@router.get("", response_model=list[HackathonRead])
def list_hackathons(session: Session = Depends(get_session)) -> list[Hackathon]:
    return list(session.exec(select(Hackathon)).all())


@router.get("/{hackathon_id}", response_model=HackathonDetailRead)
def get_hackathon(hackathon_id: int, session: Session = Depends(get_session)) -> Hackathon:
    statement = (
        select(Hackathon)
        .where(Hackathon.id == hackathon_id)
        .options(
            selectinload(Hackathon.organizer),
            selectinload(Hackathon.teams),
        )
    )
    hackathon = session.exec(statement).first()
    if hackathon is None:
        raise HTTPException(status_code=404, detail="Хакатон не найден")
    return hackathon


@router.post("", response_model=HackathonRead, status_code=status.HTTP_201_CREATED)
def create_hackathon(
    data: HackathonCreate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
) -> Hackathon:
    hackathon = Hackathon(**data.model_dump(), organizer_id=current_user.id)
    session.add(hackathon)
    session.commit()
    session.refresh(hackathon)
    return hackathon


@router.patch("/{hackathon_id}", response_model=HackathonRead)
def update_hackathon(
    hackathon_id: int,
    data: HackathonUpdate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
) -> Hackathon:
    hackathon = session.get(Hackathon, hackathon_id)
    if hackathon is None:
        raise HTTPException(status_code=404, detail="Хакатон не найден")
    if hackathon.organizer_id != current_user.id:
        raise HTTPException(status_code=403, detail="Только организатор может редактировать")

    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(hackathon, key, value)

    session.add(hackathon)
    session.commit()
    session.refresh(hackathon)
    return hackathon


@router.delete("/{hackathon_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_hackathon(
    hackathon_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
) -> None:
    hackathon = session.get(Hackathon, hackathon_id)
    if hackathon is None:
        raise HTTPException(status_code=404, detail="Хакатон не найден")
    if hackathon.organizer_id != current_user.id:
        raise HTTPException(status_code=403, detail="Только организатор может удалить")

    session.delete(hackathon)
    session.commit()
