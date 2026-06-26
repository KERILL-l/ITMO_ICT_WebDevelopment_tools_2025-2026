from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import selectinload
from sqlmodel import Session, select

from app.api.deps import get_current_user
from app.core.database import get_session
from app.models import Skill, User, UserSkill
from app.schemas import SkillCreate, SkillDetailRead, SkillRead, SkillUpdate

router = APIRouter(prefix="/skills", tags=["skills"])


@router.get("", response_model=list[SkillRead])
def list_skills(session: Session = Depends(get_session)) -> list[Skill]:
    return list(session.exec(select(Skill)).all())


@router.get("/{skill_id}", response_model=SkillDetailRead)
def get_skill(skill_id: int, session: Session = Depends(get_session)) -> Skill:
    statement = (
        select(Skill)
        .where(Skill.id == skill_id)
        .options(selectinload(Skill.user_skills).selectinload(UserSkill.user))
    )
    skill = session.exec(statement).first()
    if skill is None:
        raise HTTPException(status_code=404, detail="Навык не найден")
    return skill


@router.post("", response_model=SkillRead, status_code=status.HTTP_201_CREATED)
def create_skill(
    data: SkillCreate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
) -> Skill:
    existing = session.exec(select(Skill).where(Skill.name == data.name)).first()
    if existing:
        raise HTTPException(status_code=400, detail="Навык с таким именем уже есть")

    skill = Skill(**data.model_dump())
    session.add(skill)
    session.commit()
    session.refresh(skill)
    return skill


@router.patch("/{skill_id}", response_model=SkillRead)
def update_skill(
    skill_id: int,
    data: SkillUpdate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
) -> Skill:
    skill = session.get(Skill, skill_id)
    if skill is None:
        raise HTTPException(status_code=404, detail="Навык не найден")

    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(skill, key, value)

    session.add(skill)
    session.commit()
    session.refresh(skill)
    return skill


@router.delete("/{skill_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_skill(
    skill_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
) -> None:
    skill = session.get(Skill, skill_id)
    if skill is None:
        raise HTTPException(status_code=404, detail="Навык не найден")

    session.delete(skill)
    session.commit()
