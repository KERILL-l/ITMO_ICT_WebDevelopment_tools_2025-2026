from datetime import datetime
from enum import Enum

from sqlmodel import Field, Relationship, SQLModel


class TeamRole(str, Enum):
    captain = "captain"
    member = "member"


class Proficiency(str, Enum):
    beginner = "beginner"
    intermediate = "intermediate"
    expert = "expert"


class User(SQLModel, table=True):
    __tablename__ = "users"

    id: int | None = Field(default=None, primary_key=True)
    email: str = Field(unique=True, index=True)
    username: str = Field(unique=True, index=True)
    hashed_password: str
    created_at: datetime = Field(default_factory=datetime.utcnow)

    organized_hackathons: list["Hackathon"] = Relationship(back_populates="organizer")
    captain_teams: list["Team"] = Relationship(back_populates="captain")
    team_memberships: list["TeamMember"] = Relationship(back_populates="user")
    user_skills: list["UserSkill"] = Relationship(back_populates="user")


class Hackathon(SQLModel, table=True):
    __tablename__ = "hackathons"

    id: int | None = Field(default=None, primary_key=True)
    title: str
    description: str = ""
    start_date: datetime
    end_date: datetime
    organizer_id: int = Field(foreign_key="users.id")

    organizer: User | None = Relationship(back_populates="organized_hackathons")
    teams: list["Team"] = Relationship(back_populates="hackathon")


class Team(SQLModel, table=True):
    __tablename__ = "teams"

    id: int | None = Field(default=None, primary_key=True)
    name: str
    hackathon_id: int = Field(foreign_key="hackathons.id")
    captain_id: int = Field(foreign_key="users.id")

    hackathon: Hackathon | None = Relationship(back_populates="teams")
    captain: User | None = Relationship(back_populates="captain_teams")
    members: list["TeamMember"] = Relationship(back_populates="team")


class TeamMember(SQLModel, table=True):
    __tablename__ = "team_members"

    id: int | None = Field(default=None, primary_key=True)
    team_id: int = Field(foreign_key="teams.id")
    user_id: int = Field(foreign_key="users.id")
    role: TeamRole = Field(default=TeamRole.member)
    joined_at: datetime = Field(default_factory=datetime.utcnow)

    team: Team | None = Relationship(back_populates="members")
    user: User | None = Relationship(back_populates="team_memberships")


class Skill(SQLModel, table=True):
    __tablename__ = "skills"

    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(unique=True, index=True)
    description: str = ""

    user_skills: list["UserSkill"] = Relationship(back_populates="skill")


class UserSkill(SQLModel, table=True):
    __tablename__ = "user_skills"

    id: int | None = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id")
    skill_id: int = Field(foreign_key="skills.id")
    proficiency: Proficiency = Field(default=Proficiency.beginner)

    user: User | None = Relationship(back_populates="user_skills")
    skill: Skill | None = Relationship(back_populates="user_skills")
