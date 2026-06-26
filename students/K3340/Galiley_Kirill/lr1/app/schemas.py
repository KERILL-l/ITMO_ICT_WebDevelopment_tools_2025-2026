from datetime import datetime

from pydantic import BaseModel, EmailStr

from app.models import Proficiency, TeamRole


class UserRegister(BaseModel):
    email: EmailStr
    username: str
    password: str


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class PasswordChange(BaseModel):
    old_password: str
    new_password: str


class UserSkillCreate(BaseModel):
    skill_id: int
    proficiency: Proficiency = Proficiency.beginner


# --- User ---


class UserCreate(BaseModel):
    email: EmailStr
    username: str
    password: str


class UserRead(BaseModel):
    id: int
    email: EmailStr
    username: str
    created_at: datetime

    model_config = {"from_attributes": True}


class UserSkillRead(BaseModel):
    id: int
    proficiency: Proficiency
    skill: "SkillRead"

    model_config = {"from_attributes": True}


class UserDetailRead(UserRead):
    user_skills: list[UserSkillRead] = []
    team_memberships: list["TeamMemberRead"] = []


# --- Skill ---


class SkillCreate(BaseModel):
    name: str
    description: str = ""


class SkillUpdate(BaseModel):
    name: str | None = None
    description: str | None = None


class SkillRead(BaseModel):
    id: int
    name: str
    description: str

    model_config = {"from_attributes": True}


class UserSkillBrief(BaseModel):
    id: int
    proficiency: Proficiency
    user: UserRead

    model_config = {"from_attributes": True}


class SkillDetailRead(SkillRead):
    user_skills: list[UserSkillBrief] = []


# --- Hackathon ---


class HackathonCreate(BaseModel):
    title: str
    description: str = ""
    start_date: datetime
    end_date: datetime


class HackathonUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    start_date: datetime | None = None
    end_date: datetime | None = None


class HackathonRead(BaseModel):
    id: int
    title: str
    description: str
    start_date: datetime
    end_date: datetime
    organizer_id: int

    model_config = {"from_attributes": True}


class TeamBrief(BaseModel):
    id: int
    name: str
    hackathon_id: int
    captain_id: int

    model_config = {"from_attributes": True}


class HackathonDetailRead(HackathonRead):
    organizer: UserRead
    teams: list[TeamBrief] = []


# --- Team ---


class TeamCreate(BaseModel):
    name: str
    hackathon_id: int
    captain_id: int


class TeamUpdate(BaseModel):
    name: str | None = None
    captain_id: int | None = None


class TeamRead(BaseModel):
    id: int
    name: str
    hackathon_id: int
    captain_id: int

    model_config = {"from_attributes": True}


class TeamMemberCreate(BaseModel):
    user_id: int
    role: TeamRole = TeamRole.member


class TeamMemberRead(BaseModel):
    id: int
    team_id: int
    user_id: int
    role: TeamRole
    joined_at: datetime
    user: UserRead

    model_config = {"from_attributes": True}


class HackathonBrief(BaseModel):
    id: int
    title: str

    model_config = {"from_attributes": True}


class TeamDetailRead(TeamRead):
    hackathon: HackathonBrief
    captain: UserRead
    members: list[TeamMemberRead] = []


UserDetailRead.model_rebuild()
UserSkillRead.model_rebuild()
SkillDetailRead.model_rebuild()
HackathonDetailRead.model_rebuild()
TeamDetailRead.model_rebuild()
