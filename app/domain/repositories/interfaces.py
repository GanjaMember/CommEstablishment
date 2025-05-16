from abc import ABC, abstractmethod
from typing import List, Optional
from uuid import UUID
from datetime import date, datetime

from app.domain.models.models import (
    Company, Department, Project, Task, Employee,
    Event, KnowledgeArticle, ProjectStatus,
    TaskStatus, TaskPriority, EventType, Importance
)


class CompanyRepository(ABC):
    @abstractmethod
    def save(self, company: Company) -> None:
        pass

    @abstractmethod
    def find_by_id(self, company_id: UUID) -> Optional[Company]:
        pass

    @abstractmethod
    def find_by_legal_name(self, legal_name: str) -> Optional[Company]:
        pass

    @abstractmethod
    def find_all(self) -> List[Company]:
        pass


class DepartmentRepository(ABC):
    @abstractmethod
    def save(self, department: Department) -> None:
        pass

    @abstractmethod
    def find_by_id(self, department_id: UUID) -> Optional[Department]:
        pass

    @abstractmethod
    def find_by_name(self, name: str) -> Optional[Department]:
        pass

    @abstractmethod
    def find_all(self) -> List[Department]:
        pass

    @abstractmethod
    def find_by_lead(self, lead_id: UUID) -> List[Department]:
        pass


class ProjectRepository(ABC):
    @abstractmethod
    def save(self, project: Project) -> None:
        pass

    @abstractmethod
    def find_by_id(self, project_id: UUID) -> Optional[Project]:
        pass

    @abstractmethod
    def find_by_code(self, code: str) -> Optional[Project]:
        pass

    @abstractmethod
    def find_all(self) -> List[Project]:
        pass

    @abstractmethod
    def find_by_department(self, department_id: UUID) -> List[Project]:
        pass

    @abstractmethod
    def find_by_status(self, status: ProjectStatus) -> List[Project]:
        pass

    @abstractmethod
    def find_by_employee(self, employee_id: UUID) -> List[Project]:
        pass


class TaskRepository(ABC):
    @abstractmethod
    def save(self, task: Task) -> None:
        pass

    @abstractmethod
    def find_by_id(self, task_id: UUID) -> Optional[Task]:
        pass

    @abstractmethod
    def find_all(self) -> List[Task]:
        pass

    @abstractmethod
    def find_by_project(self, project_id: UUID) -> List[Task]:
        pass

    @abstractmethod
    def find_by_status(self, status: TaskStatus) -> List[Task]:
        pass

    @abstractmethod
    def find_by_priority(self, priority: TaskPriority) -> List[Task]:
        pass

    @abstractmethod
    def find_by_employee(self, employee_id: UUID) -> List[Task]:
        pass

    @abstractmethod
    def find_due_by_date(self, due_date: date) -> List[Task]:
        pass


class EmployeeRepository(ABC):
    @abstractmethod
    def save(self, employee: Employee) -> None:
        pass

    @abstractmethod
    def find_by_id(self, employee_id: UUID) -> Optional[Employee]:
        pass

    @abstractmethod
    def find_all(self) -> List[Employee]:
        pass

    @abstractmethod
    def find_by_name(self, name_query: str) -> List[Employee]:
        pass

    @abstractmethod
    def find_by_department(self, department_id: UUID) -> List[Employee]:
        pass

    @abstractmethod
    def find_by_project(self, project_id: UUID) -> List[Employee]:
        pass

    @abstractmethod
    def find_by_email(self, email: str) -> Optional[Employee]:
        pass

    @abstractmethod
    def find_birthdays_between(
        self,
        start_date: date,
        end_date: date
    ) -> List[Employee]:
        pass


class EventRepository(ABC):
    @abstractmethod
    def save(self, event: Event) -> None:
        pass

    @abstractmethod
    def find_by_id(self, event_id: UUID) -> Optional[Event]:
        pass

    @abstractmethod
    def find_all(self) -> List[Event]:
        pass

    @abstractmethod
    def find_by_timeframe(self, start: datetime, end: datetime) -> List[Event]:
        pass

    @abstractmethod
    def find_by_type(self, event_type: EventType) -> List[Event]:
        pass

    @abstractmethod
    def find_by_participant(self, employee_id: UUID) -> List[Event]:
        pass

    @abstractmethod
    def find_upcoming(self, days_ahead: int) -> List[Event]:
        pass


class KnowledgeArticleRepository(ABC):
    @abstractmethod
    def save(self, article: KnowledgeArticle) -> None:
        pass

    @abstractmethod
    def find_by_id(self, article_id: UUID) -> Optional[KnowledgeArticle]:
        pass

    @abstractmethod
    def find_all(self) -> List[KnowledgeArticle]:
        pass

    @abstractmethod
    def find_by_title(self, title_query: str) -> List[KnowledgeArticle]:
        pass

    @abstractmethod
    def find_by_author(self, author_id: UUID) -> List[KnowledgeArticle]:
        pass

    @abstractmethod
    def find_by_tag(self, tag: str) -> List[KnowledgeArticle]:
        pass

    @abstractmethod
    def find_by_importance(
        self,
        importance: Importance
    ) -> List[KnowledgeArticle]:
        pass

    @abstractmethod
    def search(self, query: str) -> List[KnowledgeArticle]:
        pass
