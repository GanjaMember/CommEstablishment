from datetime import datetime, date
from typing import List, Optional
from uuid import UUID, uuid4

from sqlalchemy import (
    Column, String, Text, Boolean, DateTime, Date, Enum,
    Integer, ForeignKey, Table, UniqueConstraint
)
from sqlalchemy.dialects.postgresql import UUID as PgUUID
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

from app.domain.models.models import (
    ProjectStatus, TaskStatus, TaskPriority, 
    AvailabilityType, EventType, RSVPStatus, Importance
)

Base = declarative_base()

# Association tables
department_employee = Table(
    'department_employee', Base.metadata,
    Column('department_id', PgUUID(as_uuid=True), ForeignKey('departments.id')),
    Column('employee_id', PgUUID(as_uuid=True), ForeignKey('employees.id'))
)

project_employee = Table(
    'project_employee', Base.metadata,
    Column('project_id', PgUUID(as_uuid=True), ForeignKey('projects.id')),
    Column('employee_id', PgUUID(as_uuid=True), ForeignKey('employees.id'))
)

task_employee = Table(
    'task_employee', Base.metadata,
    Column('task_id', PgUUID(as_uuid=True), ForeignKey('tasks.id')),
    Column('employee_id', PgUUID(as_uuid=True), ForeignKey('employees.id'))
)

article_tag = Table(
    'article_tag', Base.metadata,
    Column('article_id', PgUUID(as_uuid=True), ForeignKey('knowledge_articles.id')),
    Column('tag', String(50))
)


class CompanyModel(Base):
    __tablename__ = 'companies'
    
    id = Column(PgUUID(as_uuid=True), primary_key=True, default=uuid4)
    display_name = Column(String(100), nullable=False)
    legal_name = Column(String(100), nullable=False, unique=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    
    departments = relationship("DepartmentModel", back_populates="company")
    employees = relationship("EmployeeModel", back_populates="company")
    projects = relationship("ProjectModel", back_populates="company")
    events = relationship("EventModel", back_populates="company")
    knowledge_articles = relationship("KnowledgeArticleModel", back_populates="company")


class DepartmentModel(Base):
    __tablename__ = 'departments'
    
    id = Column(PgUUID(as_uuid=True), primary_key=True, default=uuid4)
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    lead_id = Column(PgUUID(as_uuid=True), ForeignKey('employees.id'), nullable=True)
    company_id = Column(PgUUID(as_uuid=True), ForeignKey('companies.id'), nullable=False)
    
    company = relationship("CompanyModel", back_populates="departments")
    lead = relationship("EmployeeModel", foreign_keys=[lead_id])
    employees = relationship("EmployeeModel", secondary=department_employee, back_populates="departments")
    projects = relationship("ProjectModel", back_populates="responsible_dept")


class EmployeeModel(Base):
    __tablename__ = 'employees'
    
    id = Column(PgUUID(as_uuid=True), primary_key=True, default=uuid4)
    first_name = Column(String(50), nullable=False)
    middle_name = Column(String(50), nullable=True)
    last_name = Column(String(50), nullable=False)
    email = Column(String(100), nullable=False, unique=True)
    phone = Column(String(20), nullable=True)
    position_title = Column(String(100), nullable=False)
    position_grade = Column(String(50), nullable=False)
    hired_at = Column(Date, nullable=False)
    birth_date = Column(Date, nullable=False)
    is_remote = Column(Boolean, default=False)
    company_id = Column(PgUUID(as_uuid=True), ForeignKey('companies.id'), nullable=False)
    
    company = relationship("CompanyModel", back_populates="employees")
    departments = relationship("DepartmentModel", secondary=department_employee, back_populates="employees")
    projects = relationship("ProjectModel", secondary=project_employee, back_populates="employees")
    tasks = relationship("TaskModel", secondary=task_employee, back_populates="employees")
    authored_articles = relationship("KnowledgeArticleModel", back_populates="author")
    event_participations = relationship("EventParticipantModel", back_populates="employee")
    availability_slots = relationship("AvailabilitySlotModel", back_populates="employee")
    
    __table_args__ = (
        UniqueConstraint('first_name', 'last_name', 'email', name='uix_employee_name_email'),
    )


class AvailabilitySlotModel(Base):
    __tablename__ = 'availability_slots'
    
    id = Column(PgUUID(as_uuid=True), primary_key=True, default=uuid4)
    employee_id = Column(PgUUID(as_uuid=True), ForeignKey('employees.id'), nullable=False)
    start = Column(DateTime, nullable=False)
    end = Column(DateTime, nullable=False)
    slot_type = Column(Enum(AvailabilityType), nullable=False, default=AvailabilityType.AVAILABLE)
    
    employee = relationship("EmployeeModel", back_populates="availability_slots")


class ProjectModel(Base):
    __tablename__ = 'projects'
    
    id = Column(PgUUID(as_uuid=True), primary_key=True, default=uuid4)
    code = Column(String(20), nullable=False, unique=True)
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=False)
    status = Column(Enum(ProjectStatus), nullable=False, default=ProjectStatus.IN_PROGRESS)
    started_at = Column(Date, nullable=True)
    finished_at = Column(Date, nullable=True)
    responsible_dept_id = Column(PgUUID(as_uuid=True), ForeignKey('departments.id'), nullable=False)
    company_id = Column(PgUUID(as_uuid=True), ForeignKey('companies.id'), nullable=False)
    
    responsible_dept = relationship("DepartmentModel", back_populates="projects")
    company = relationship("CompanyModel", back_populates="projects")
    employees = relationship("EmployeeModel", secondary=project_employee, back_populates="projects")
    tasks = relationship("TaskModel", back_populates="project")


class TaskModel(Base):
    __tablename__ = 'tasks'

    id = Column(PgUUID(as_uuid=True), primary_key=True, default=uuid4)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=False)
    priority = Column(
        Enum(TaskPriority),
        nullable=False,
        default=TaskPriority.MEDIUM
    )
    status = Column(Enum(TaskStatus), nullable=False, default=TaskStatus.TODO)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    planned_start = Column(Date, nullable=True)
    due_date = Column(Date, nullable=True)
    project_id = Column(
        PgUUID(as_uuid=True),
        ForeignKey('projects.id'),
        nullable=False
    )

    project = relationship("ProjectModel", back_populates="tasks")
    employees = relationship(
        "EmployeeModel",
        secondary=task_employee,
        back_populates="tasks"
    )


class EventModel(Base):
    __tablename__ = 'events'

    id = Column(PgUUID(as_uuid=True), primary_key=True, default=uuid4)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    start_at = Column(DateTime, nullable=False)
    end_at = Column(DateTime, nullable=False)
    event_type = Column(Enum(EventType), nullable=False, default=EventType.OTHER)
    company_id = Column(
        PgUUID(as_uuid=True),
        ForeignKey('companies.id'),
        nullable=False
    )

    company = relationship("CompanyModel", back_populates="events")
    participants = relationship(
        "EventParticipantModel",
        back_populates="event",
        cascade="all, delete-orphan"
    )


class EventParticipantModel(Base):
    __tablename__ = 'event_participants'

    id = Column(PgUUID(as_uuid=True), primary_key=True, default=uuid4)
    event_id = Column(
        PgUUID(as_uuid=True),
        ForeignKey('events.id'),
        nullable=False
    )
    employee_id = Column(
        PgUUID(as_uuid=True),
        ForeignKey('employees.id'),
        nullable=False
    )
    rsvp = Column(Enum(RSVPStatus), nullable=False, default=RSVPStatus.YES)

    event = relationship("EventModel", back_populates="participants")
    employee = relationship(
        "EmployeeModel",
        back_populates="event_participations"
    )

    __table_args__ = (
        UniqueConstraint(
            'event_id',
            'employee_id',
            name='uix_event_participant'
        ),
    )


class KnowledgeArticleModel(Base):
    __tablename__ = 'knowledge_articles'

    id = Column(PgUUID(as_uuid=True), primary_key=True, default=uuid4)
    title = Column(String(200), nullable=False)
    body = Column(Text, nullable=False)
    importance = Column(
        Enum(Importance),
        nullable=False,
        default=Importance.NORMAL
    )
    created_at = Column(
        DateTime,
        nullable=False,
        default=datetime.utcnow
    )
    author_id = Column(
        PgUUID(as_uuid=True),
        ForeignKey('employees.id'),
        nullable=False
    )
    company_id = Column(
        PgUUID(as_uuid=True),
        ForeignKey('companies.id'),
        nullable=False
    )

    author = relationship("EmployeeModel", back_populates="authored_articles")
    company = relationship("CompanyModel", back_populates="knowledge_articles")
    # Using association proxy for tags
    tags = relationship(
        "ArticleTagModel",
        back_populates="article",
        cascade="all, delete-orphan"
    )


class ArticleTagModel(Base):
    __tablename__ = 'article_tags'

    article_id = Column(
        PgUUID(as_uuid=True),
        ForeignKey('knowledge_articles.id'),
        primary_key=True
    )
    tag = Column(String(50), primary_key=True)

    article = relationship("KnowledgeArticleModel", back_populates="tags")
