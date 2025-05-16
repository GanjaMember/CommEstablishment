# Full implementation with hashable entities

from dataclasses import dataclass, field
from typing import List, Set, Optional
from uuid import UUID, uuid4
from datetime import datetime, date, timedelta
from enum import Enum, auto


# ---------- Enumerations ---------- #
class ProjectStatus(Enum):
    PLANNED = auto()
    IN_PROGRESS = auto()
    REVIEW = auto()
    DONE = auto()
    ARCHIVED = auto()


class TaskStatus(Enum):
    TODO = auto()
    IN_PROGRESS = auto()
    REVIEW = auto()
    DONE = auto()


class TaskPriority(Enum):
    LOW = auto()
    MEDIUM = auto()
    HIGH = auto()
    CRITICAL = auto()


class AvailabilityType(Enum):
    AVAILABLE = auto()
    PTO = auto()
    SICK = auto()
    OFFLINE = auto()


class EventType(Enum):
    BIRTHDAY = auto()
    HACKATHON = auto()
    TEAM_BUILDING = auto()
    GAME = auto()
    OTHER = auto()


class RSVPStatus(Enum):
    YES = auto()
    MAYBE = auto()
    NO = auto()
    WAITLIST = auto()


class Importance(Enum):
    LOW = auto()
    NORMAL = auto()
    HIGH = auto()
    CRITICAL = auto()


# ---------- Value Objects ---------- #
@dataclass(frozen=True)
class PersonName:
    first: str
    last: str
    middle: Optional[str] = None

    def full(self) -> str:
        return " ".join(filter(None, [self.first, self.middle, self.last]))


@dataclass(frozen=True)
class ContactInfo:
    email: str
    phone: Optional[str] = None


@dataclass(frozen=True)
class Role:
    title: str
    grade: str


@dataclass(frozen=True)
class AvailabilitySlot:
    start: datetime
    end: datetime
    slot_type: AvailabilityType = AvailabilityType.AVAILABLE


# ---------- Hashable mixin ---------- #
class _Hashable:
    id: UUID

    def __hash__(self):
        return hash(self.id)

    def __eq__(self, other):
        return isinstance(other, self.__class__) and self.id == other.id


# ---------- Entities ---------- #
@dataclass(eq=False)
class Department(_Hashable):
    name: str
    id: UUID = field(default_factory=uuid4)
    description: Optional[str] = None
    lead: Optional["Employee"] = None
    employees: Set["Employee"] = field(default_factory=set, repr=False)
    projects: Set["Project"] = field(default_factory=set, repr=False)


@dataclass(eq=False)
class Project(_Hashable):
    code: str
    name: str
    description: str
    responsible_dept: Department
    status: ProjectStatus = ProjectStatus.IN_PROGRESS
    id: UUID = field(default_factory=uuid4)
    employees: Set["Employee"] = field(default_factory=set, repr=False)
    tasks: Set["Task"] = field(default_factory=set, repr=False)
    started_at: Optional[date] = None
    finished_at: Optional[date] = None

    def add_employee(self, employee: "Employee"):
        self.employees.add(employee)
        employee.projects.add(self)


@dataclass(eq=False)
class Task(_Hashable):
    title: str
    description: str
    project: Project
    priority: TaskPriority = TaskPriority.MEDIUM
    status: TaskStatus = TaskStatus.TODO
    id: UUID = field(default_factory=uuid4)
    created_at: datetime = field(default_factory=datetime.utcnow)
    planned_start: Optional[date] = None
    due_date: Optional[date] = None
    employees: Set["Employee"] = field(default_factory=set, repr=False)

    def assign(self, employee: "Employee"):
        self.employees.add(employee)
        employee.tasks.add(self)


@dataclass(eq=False)
class Employee(_Hashable):
    name: PersonName
    contacts: ContactInfo
    position: Role
    hired_at: date
    birth_date: date
    is_remote: bool = False
    id: UUID = field(default_factory=uuid4)
    departments: Set[Department] = field(default_factory=set, repr=False)
    projects: Set[Project] = field(default_factory=set, repr=False)
    tasks: Set[Task] = field(default_factory=set, repr=False)
    availability: List[AvailabilitySlot] = field(default_factory=list, repr=False)

    def __str__(self):
        return f"{self.name.full()} ({self.position.title}, {self.position.grade})"


@dataclass
class EventParticipant:
    employee: Employee
    rsvp: RSVPStatus = RSVPStatus.YES


@dataclass(eq=False)
class Event(_Hashable):
    title: str
    start_at: datetime
    end_at: datetime
    event_type: EventType = EventType.OTHER
    description: Optional[str] = None
    id: UUID = field(default_factory=uuid4)
    participants: List[EventParticipant] = field(default_factory=list, repr=False)

    def add_participant(self, employee: Employee, rsvp: RSVPStatus = RSVPStatus.YES):
        self.participants.append(EventParticipant(employee, rsvp))


@dataclass(eq=False)
class KnowledgeArticle(_Hashable):
    title: str
    body: str
    author: Employee
    importance: Importance = Importance.NORMAL
    id: UUID = field(default_factory=uuid4)
    tags: Set[str] = field(default_factory=set)
    created_at: datetime = field(default_factory=datetime.utcnow)


# ---------- Aggregate Root ---------- #
@dataclass
class Company:
    display_name: str
    legal_name: str
    id: UUID = field(default_factory=uuid4)
    created_at: datetime = field(default_factory=datetime.utcnow)
    departments: List[Department] = field(default_factory=list, repr=False)
    employees: List[Employee] = field(default_factory=list, repr=False)
    projects: List[Project] = field(default_factory=list, repr=False)
    events: List[Event] = field(default_factory=list, repr=False)
    knowledge_base: List[KnowledgeArticle] = field(default_factory=list, repr=False)

    # --- Commands --- #
    def add_department(self, dept: Department):
        self.departments.append(dept)

    def add_employee(self, emp: Employee, dept: Department):
        self.employees.append(emp)
        dept.employees.add(emp)
        emp.departments.add(dept)

    def add_project(self, project: Project):
        self.projects.append(project)
        project.responsible_dept.projects.add(project)

    def add_event(self, event: Event):
        self.events.append(event)

    def add_article(self, article: KnowledgeArticle):
        self.knowledge_base.append(article)

    # --- Queries --- #
    def find_employees_by_name(self, query: str) -> List[Employee]:
        q = query.lower()
        return [e for e in self.employees if q in e.name.full().lower()]

    def find_employees_by_department(self, dept_name: str) -> List[Employee]:
        for d in self.departments:
            if d.name.lower() == dept_name.lower():
                return list(d.employees)
        return []

    def find_employees_by_project(self, project_code: str) -> List[Employee]:
        for p in self.projects:
            if p.code.lower() == project_code.lower():
                return list(p.employees)
        return []

    def upcoming_events(self, days_ahead: int = 30) -> List[Event]:
        now = datetime.utcnow()
        horizon = now + timedelta(days=days_ahead)
        return [e for e in self.events if now <= e.start_at <= horizon]

    def employee_birthdays_next(self, days_ahead: int = 30) -> List[Employee]:
        today = date.today()
        horizon = today + timedelta(days=days_ahead)
        result = []
        for e in self.employees:
            bday = e.birth_date.replace(year=today.year)
            if today <= bday <= horizon:
                result.append(e)
        return result


# ---------- Demo ---------- #
'''def demo():
    acme = Company(display_name="Acme Mobile", legal_name="Acme LLC")

    # Departments
    eng = Department(name="Engineering")
    hr = Department(name="HR")
    acme.add_department(eng)
    acme.add_department(hr)

    # Employees
    alice = Employee(
        name=PersonName("Alice", "Smith"),
        contacts=ContactInfo(email="alice@acme.com"),
        position=Role("iOS Engineer", "Middle"),
        hired_at=date(2021, 6, 1),
        birth_date=date(1995, 5, 20),
        is_remote=True,
    )
    bob = Employee(
        name=PersonName("Bob", "Kim"),
        contacts=ContactInfo(email="bob@acme.com"),
        position=Role("Android Engineer", "Senior"),
        hired_at=date(2019, 3, 14),
        birth_date=date(1990, 8, 11),
    )
    acme.add_employee(alice, eng)
    acme.add_employee(bob, eng)

    # Project
    mob = Project(
        code="MOB1",
        name="Corporate Mobile Platform",
        description="Next-gen employee app",
        responsible_dept=eng,
        started_at=date(2023, 9, 1),
    )
    acme.add_project(mob)
    mob.add_employee(alice)
    mob.add_employee(bob)

    # Task
    task = Task(
        title="Prototype chat bot",
        description="AI integration POC",
        project=mob,
        priority=TaskPriority.HIGH,
        status=TaskStatus.IN_PROGRESS,
        due_date=date(2024, 6, 30),
    )
    task.assign(alice)
    mob.tasks.add(task)

    # Event
    hackathon = Event(
        title="Mobile Hackathon",
        start_at=datetime.utcnow() + timedelta(days=7),
        end_at=datetime.utcnow() + timedelta(days=7, hours=8),
        event_type=EventType.HACKATHON,
    )
    hackathon.add_participant(alice)
    hackathon.add_participant(bob)
    acme.add_event(hackathon)

    # Knowledge Base
    article = KnowledgeArticle(
        title="CI/CD for Flutter",
        body="Steps...",
        author=alice,
        importance=Importance.HIGH,
        tags={"flutter", "ci"},
    )
    acme.add_article(article)

    # --- Queries --- #
    print("Find by name 'ali':", [str(e) for e in acme.find_employees_by_name("ali")])
    print("Engineering dept:", [str(e) for e in acme.find_employees_by_department("Engineering")])
    print("Project MOB1:", [str(e) for e in acme.find_employees_by_project("MOB1")])
    print("Upcoming events:", [e.title for e in acme.upcoming_events()])
    print("Birthdays next 60d:", [str(e) for e in acme.employee_birthdays_next(60)])


demo()'''