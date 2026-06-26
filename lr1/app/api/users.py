from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import selectinload
from sqlmodel import Session, select

from app.api.deps import get_current_user
from app.core.database import get_session
from app.core.security import hash_password, verify_password
from app.models import Skill, TeamMember, User, UserSkill
from app.schemas import PasswordChange, UserDetailRead, UserRead, UserSkillCreate, UserSkillRead

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=UserRead)
def get_me(current_user: User = Depends(get_current_user)) -> User:
    return current_user


@router.get("", response_model=list[UserRead])
def list_users(
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
) -> list[User]:
    return list(session.exec(select(User)).all())


@router.get("/{user_id}", response_model=UserDetailRead)
def get_user(
    user_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
) -> User:
    statement = (
        select(User)
        .where(User.id == user_id)
        .options(
            selectinload(User.user_skills).selectinload(UserSkill.skill),
            selectinload(User.team_memberships).selectinload(TeamMember.user),
        )
    )
    user = session.exec(statement).first()
    if user is None:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    return user


@router.patch("/me/password")
def change_password(
    data: PasswordChange,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
) -> dict[str, str]:
    if not verify_password(data.old_password, current_user.hashed_password):
        raise HTTPException(status_code=400, detail="Неверный текущий пароль")

    current_user.hashed_password = hash_password(data.new_password)
    session.add(current_user)
    session.commit()
    return {"message": "Пароль успешно изменён"}


@router.post("/me/skills", response_model=UserSkillRead, status_code=status.HTTP_201_CREATED)
def add_my_skill(
    data: UserSkillCreate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
) -> UserSkill:
    skill = session.get(Skill, data.skill_id)
    if skill is None:
        raise HTTPException(status_code=404, detail="Навык не найден")

    existing = session.exec(
        select(UserSkill).where(
            UserSkill.user_id == current_user.id,
            UserSkill.skill_id == data.skill_id,
        )
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Навык уже добавлен")

    user_skill = UserSkill(
        user_id=current_user.id,
        skill_id=data.skill_id,
        proficiency=data.proficiency,
    )
    session.add(user_skill)
    session.commit()
    session.refresh(user_skill)

    statement = (
        select(UserSkill)
        .where(UserSkill.id == user_skill.id)
        .options(selectinload(UserSkill.skill))
    )
    return session.exec(statement).one()


@router.delete("/me/skills/{skill_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_my_skill(
    skill_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
) -> None:
    user_skill = session.exec(
        select(UserSkill).where(
            UserSkill.user_id == current_user.id,
            UserSkill.skill_id == skill_id,
        )
    ).first()
    if user_skill is None:
        raise HTTPException(status_code=404, detail="Навык не найден")

    session.delete(user_skill)
    session.commit()
