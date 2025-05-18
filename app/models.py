from enum import Enum
from datetime import datetime, date

from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash


db = SQLAlchemy()

# --- ENUMS ---


class Status(str, Enum):
    TODO = "todo"
    IN_PROGRESS = "in_progress"
    REVIEW = "review"
    DONE = "done"


class EventType(str, Enum):
    CORPORATE = "corporate"
    BIRTHDAY = "birthday"
    TEAM_BUILDING = "team_building"
    OTHER = "other"


# --- M2M ASSOCIATION TABLES ---

department_employee = db.Table(
    "department_employee",
    db.Column("department_id", db.ForeignKey("department.id"), primary_key=True),
    db.Column("employee_id", db.ForeignKey("employee.id"), primary_key=True),
    db.Column("is_lead", db.Boolean, default=False, nullable=False),
)

project_employee = db.Table(
    "project_employee",
    db.Column("project_id", db.ForeignKey("project.id"), primary_key=True),
    db.Column("employee_id", db.ForeignKey("employee.id"), primary_key=True),
)

task_employee = db.Table(
    "task_employee",
    db.Column("task_id", db.ForeignKey("task.id"), primary_key=True),
    db.Column("employee_id", db.ForeignKey("employee.id"), primary_key=True),
)

event_attendee = db.Table(
    "event_attendee",
    db.Column("event_id", db.ForeignKey("hr_event.id"), primary_key=True),
    db.Column("employee_id", db.ForeignKey("employee.id"), primary_key=True),
)

chat_employee = db.Table(
    "chat_employee",
    db.Column("chat_id", db.ForeignKey("chat.id"), primary_key=True),
    db.Column("employee_id", db.ForeignKey("employee.id"), primary_key=True),
)

# --- BASE MODEL (add created/updated columns) ---


class TimestampMixin(object):
    created_at = db.Column(
        db.DateTime(timezone=True), default=datetime.utcnow, nullable=False
    )
    updated_at = db.Column(
        db.DateTime(timezone=True),
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )


# --- MAIN ENTITIES ---


class Company(TimestampMixin, db.Model):
    __tablename__ = "company"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(200), unique=True, index=True, nullable=False)
    description = db.Column(db.Text, nullable=True)

    # relations
    departments = db.relationship("Department", back_populates="company")
    projects = db.relationship("Project", back_populates="company")
    employees = db.relationship("Employee", back_populates="company")
    knowledge_base = db.relationship(
        "KnowledgeBase", back_populates="company", uselist=False
    )

    @property
    def index(self) -> str:
        return "".join(i[0] for i in self.name.title().split()) + '-' + str(self.id)


class Chat(TimestampMixin, db.Model):
    __tablename__ = "chat"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(200), unique=True, index=True, nullable=False)

    # relations
    employees = db.relationship(
        "Employee", secondary="chat_employee", back_populates="chats"
    )
    messages = db.relationship("Message", back_populates="chat", lazy="dynamic")

    @property
    def index(self) -> str:
        return "".join(i[0] for i in self.name.title().split()) + '-' + str(self.id)

    @property
    def participant_count(self) -> int:
        return len(self.employees)


class Department(TimestampMixin, db.Model):
    __tablename__ = "department"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text, nullable=True)

    company_id = db.Column(db.Integer, db.ForeignKey("company.id"), nullable=False)
    company = db.relationship("Company", back_populates="departments")

    employees = db.relationship(
        "Employee", secondary=department_employee, back_populates="departments"
    )
    projects = db.relationship("Project", back_populates="responsible_dept")

    __table_args__ = (
        db.UniqueConstraint("company_id", "name", name="uq_department_name"),
    )

    @property
    def index(self) -> str:
        return "".join(i[0] for i in self.name.title().split()) + '-' + str(self.id)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "company_id": self.company_id,
            "employees": [emp.id for emp in self.employees],
            "projects": [proj.id for proj in self.projects],
        }

    def __str__(self):
        return f"Department {self.to_dict()}"

class Role(TimestampMixin, db.Model):
    __tablename__ = "role"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False)
    grade = db.Column(db.String(50), nullable=True)
    description = db.Column(db.Text, nullable=True)

    employees = db.relationship("Employee", back_populates="role")


class Employee(TimestampMixin, db.Model):
    __tablename__ = "employee"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    surname = db.Column(db.String(100), index=True, nullable=False)
    name = db.Column(db.String(100), index=True, nullable=False)
    patronymic = db.Column(db.String(100), nullable=True)

    hire_date = db.Column(db.Date, nullable=False)
    birth_date = db.Column(db.Date, nullable=True)
    contacts = db.Column(db.Text, nullable=True)
    email = db.Column(db.String(100), unique=True, index=True, nullable=False)

    company_id = db.Column(db.Integer, db.ForeignKey("company.id"), nullable=False)
    role_id = db.Column(db.Integer, db.ForeignKey("role.id"), nullable=True)

    company = db.relationship("Company", back_populates="employees")
    role = db.relationship("Role", back_populates="employees")
    
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=True)
    user = db.relationship("User", back_populates="employee")

    departments = db.relationship(
        "Department", secondary=department_employee, back_populates="employees"
    )
    projects = db.relationship(
        "Project", secondary=project_employee, back_populates="employees"
    )
    tasks = db.relationship("Task", secondary=task_employee, back_populates="employees")
    records_created = db.relationship("KBRecord", back_populates="creator")
    events = db.relationship(
        "HREvent", secondary=event_attendee, back_populates="attendees"
    )
    chats = db.relationship(
        "Chat", secondary="chat_employee", back_populates="employees"
    )
    sent_messages = db.relationship("Message", back_populates="sender", lazy="dynamic")

    __table_args__ = (
        db.Index("ix_employee_fullname", "surname", "name", "patronymic"),
    )

    @property
    def full_name(self) -> str:
        parts = [self.surname, self.name]
        if self.patronymic:
            parts.append(self.patronymic)
        return " ".join(parts)

    @property
    def index(self) -> str:
        return "".join(i[0] for i in self.full_name.title().split())

    def to_dict(self):
        return {
            "id": self.id,
            "surname": self.surname,
            "name": self.name,
            "patronymic": self.patronymic,
            "full_name": self.full_name,
            "hire_date": self.hire_date.isoformat() if self.hire_date else None,
            "birth_date": self.birth_date.isoformat() if self.birth_date else None,
            "contacts": self.contacts,
            "email": self.email,
            "company_id": self.company_id,
            "role_id": self.role_id,
            "departments": [dept.id for dept in self.departments],
            "projects": [proj.id for proj in self.projects],
            "tasks": [task.id for task in self.tasks],
            "events": [event.id for event in self.events],
            "chats": [chat.id for chat in self.chats],
        }

    def __str__(self):
        return f"Employee {self.to_dict()}"

class Project(TimestampMixin, db.Model):
    __tablename__ = "project"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(200), index=True, nullable=False)
    description = db.Column(db.Text, nullable=True)
    status = db.Column(db.Enum(Status), default=Status.IN_PROGRESS, nullable=False)

    company_id = db.Column(db.Integer, db.ForeignKey("company.id"), nullable=False)
    responsible_dept_id = db.Column(
        db.Integer, db.ForeignKey("department.id"), nullable=True
    )

    company = db.relationship("Company", back_populates="projects")
    responsible_dept = db.relationship("Department", back_populates="projects")

    employees = db.relationship(
        "Employee", secondary=project_employee, back_populates="projects"
    )
    tasks = db.relationship("Task", back_populates="project")

    @property
    def index(self) -> str:
        return "".join(i[0] for i in self.name.title().split()) + '-' + str(self.id)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "status": self.status.value if self.status else None,
            "company_id": self.company_id,
            "responsible_dept_id": self.responsible_dept_id,
            "employees": [emp.id for emp in self.employees],
            "tasks": [task.id for task in self.tasks],
        }
    
    def __str__(self):
        return f"Project {self.to_dict()}"

class Task(TimestampMixin, db.Model):
    __tablename__ = "task"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(250), index=True, nullable=False)
    description = db.Column(db.Text, nullable=True)
    start_date = db.Column(db.Date, nullable=True)
    due_date = db.Column(db.Date, nullable=True)
    priority = db.Column(db.Integer, nullable=True)
    status = db.Column(db.Enum(Status), default=Status.IN_PROGRESS, nullable=False)

    project_id = db.Column(db.Integer, db.ForeignKey("project.id"), nullable=True)

    project = db.relationship("Project", back_populates="tasks")
    employees = db.relationship(
        "Employee", secondary=task_employee, back_populates="tasks"
    )

    __table_args__ = (db.Index("ix_task_status_due", "status", "due_date"),)

    @property
    def index(self) -> str:
        return "".join(i[0] for i in self.name.title().split()) + '-' + str(self.id)
    
    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "start_date": self.start_date.isoformat() if self.start_date else None,
            "due_date": self.due_date.isoformat() if self.due_date else None,
            "priority": self.priority,
            "status": self.status.value if self.status else None,
            "project_id": self.project_id,
            "employees": [emp.id for emp in self.employees],
        }
    
    def __str__(self):
        return f"Task {self.to_dict()}"

class KnowledgeBase(TimestampMixin, db.Model):
    __tablename__ = "knowledge_base"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    company_id = db.Column(
        db.Integer, db.ForeignKey("company.id"), unique=True, nullable=False
    )

    company = db.relationship("Company", back_populates="knowledge_base")
    records = db.relationship("KBRecord", back_populates="kb")


class KBRecord(TimestampMixin, db.Model):
    __tablename__ = "kb_record"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    kb_id = db.Column(db.Integer, db.ForeignKey("knowledge_base.id"), nullable=False)
    creator_id = db.Column(db.Integer, db.ForeignKey("employee.id"), nullable=True)
    content = db.Column(db.Text, nullable=False)
    importance = db.Column(db.Integer, default=0, nullable=False)  # 0..100

    kb = db.relationship("KnowledgeBase", back_populates="records")
    creator = db.relationship("Employee", back_populates="records_created")


class HREvent(TimestampMixin, db.Model):
    __tablename__ = "hr_event"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(250), nullable=False)
    description = db.Column(db.Text, nullable=True)
    starts_at = db.Column(db.DateTime(timezone=True), nullable=False)
    ends_at = db.Column(db.DateTime(timezone=True), nullable=False)
    type = db.Column(db.Enum(EventType), nullable=False)
    location = db.Column(db.String(200), nullable=True)

    organizer_id = db.Column(db.Integer, db.ForeignKey("employee.id"), nullable=True)
    organizer = db.relationship("Employee")

    attendees = db.relationship(
        "Employee", secondary=event_attendee, back_populates="events"
    )


class Message(TimestampMixin, db.Model):
    __tablename__ = "message"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    content = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime(timezone=True), default=datetime.utcnow, nullable=False)

    chat_id = db.Column(db.Integer, db.ForeignKey("chat.id"), nullable=False)
    sender_id = db.Column(db.Integer, db.ForeignKey("employee.id"), nullable=True)

    chat = db.relationship("Chat", back_populates="messages")
    sender = db.relationship("Employee", back_populates="sent_messages")


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    employee = db.relationship("Employee", back_populates="user", uselist=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)