from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import selectinload
from sqlmodel import Session, select

from app.api.deps import get_current_user
from app.core.database import get_session
from app.models import Hackathon, Team, TeamMember, TeamRole, User
from app.schemas import (
    TeamCreate,
    TeamDetailRead,
    TeamMemberCreate,
    TeamMemberRead,
    TeamRead,
    TeamUpdate,
)

router = APIRouter(prefix="/teams", tags=["teams"])


@router.get("", response_model=list[TeamRead])
def list_teams(session: Session = Depends(get_session)) -> list[Team]:
    return list(session.exec(select(Team)).all())


@router.get("/{team_id}", response_model=TeamDetailRead)
def get_team(team_id: int, session: Session = Depends(get_session)) -> Team:
    statement = (
        select(Team)
        .where(Team.id == team_id)
        .options(
            selectinload(Team.hackathon),
            selectinload(Team.captain),
            selectinload(Team.members).selectinload(TeamMember.user),
        )
    )
    team = session.exec(statement).first()
    if team is None:
        raise HTTPException(status_code=404, detail="Команда не найдена")
    return team


@router.post("", response_model=TeamRead, status_code=status.HTTP_201_CREATED)
def create_team(
    data: TeamCreate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
) -> Team:
    hackathon = session.get(Hackathon, data.hackathon_id)
    if hackathon is None:
        raise HTTPException(status_code=404, detail="Хакатон не найден")

    team = Team(**data.model_dump())
    session.add(team)
    session.commit()
    session.refresh(team)

    # капитан автоматически становится участником
    member = TeamMember(
        team_id=team.id,
        user_id=team.captain_id,
        role=TeamRole.captain,
    )
    session.add(member)
    session.commit()

    return team


@router.patch("/{team_id}", response_model=TeamRead)
def update_team(
    team_id: int,
    data: TeamUpdate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
) -> Team:
    team = session.get(Team, team_id)
    if team is None:
        raise HTTPException(status_code=404, detail="Команда не найдена")
    if team.captain_id != current_user.id:
        raise HTTPException(status_code=403, detail="Только капитан может редактировать")

    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(team, key, value)

    session.add(team)
    session.commit()
    session.refresh(team)
    return team


@router.delete("/{team_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_team(
    team_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
) -> None:
    team = session.get(Team, team_id)
    if team is None:
        raise HTTPException(status_code=404, detail="Команда не найдена")
    if team.captain_id != current_user.id:
        raise HTTPException(status_code=403, detail="Только капитан может удалить")

    session.delete(team)
    session.commit()


@router.post(
    "/{team_id}/members",
    response_model=TeamMemberRead,
    status_code=status.HTTP_201_CREATED,
)
def add_member(
    team_id: int,
    data: TeamMemberCreate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
) -> TeamMember:
    team = session.get(Team, team_id)
    if team is None:
        raise HTTPException(status_code=404, detail="Команда не найдена")
    if team.captain_id != current_user.id:
        raise HTTPException(status_code=403, detail="Только капитан может добавлять участников")

    user = session.get(User, data.user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="Пользователь не найден")

    existing = session.exec(
        select(TeamMember).where(
            TeamMember.team_id == team_id,
            TeamMember.user_id == data.user_id,
        )
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Пользователь уже в команде")

    member = TeamMember(team_id=team_id, user_id=data.user_id, role=data.role)
    session.add(member)
    session.commit()
    session.refresh(member)

    # подгружаем user для ответа
    statement = (
        select(TeamMember)
        .where(TeamMember.id == member.id)
        .options(selectinload(TeamMember.user))
    )
    return session.exec(statement).one()


@router.delete("/{team_id}/members/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_member(
    team_id: int,
    user_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
) -> None:
    team = session.get(Team, team_id)
    if team is None:
        raise HTTPException(status_code=404, detail="Команда не найдена")
    if team.captain_id != current_user.id:
        raise HTTPException(status_code=403, detail="Только капитан может удалять участников")

    member = session.exec(
        select(TeamMember).where(
            TeamMember.team_id == team_id,
            TeamMember.user_id == user_id,
        )
    ).first()
    if member is None:
        raise HTTPException(status_code=404, detail="Участник не найден")

    session.delete(member)
    session.commit()
