from datetime import datetime, date, timedelta
from typing import List, Optional, Set, Dict, Any
from uuid import UUID

from sqlalchemy import and_, or_, func
from sqlalchemy.orm import Session, joinedload

from app.domain.models.models import (
    Company, Department, Employee, Project, Task, Event, 
    KnowledgeArticle, EventParticipant, ProjectStatus, 
    TaskStatus, TaskPriority, EventType, Importance, 
    PersonName, ContactInfo, Role, AvailabilitySlot, AvailabilityType, RSVPStatus
)
from app.domain.repositories.interfaces import (
    CompanyRepository, DepartmentRepository, EmployeeRepository,
    ProjectRepository, TaskRepository, EventRepository, 
    KnowledgeArticleRepository
)
from app.infrastructure.database.models import (
    CompanyModel, DepartmentModel, EmployeeModel, ProjectModel, 
    TaskModel, EventModel, KnowledgeArticleModel, EventParticipantModel, 
    AvailabilitySlotModel, ArticleTagModel
)


class SQLAlchemyCompanyRepository(CompanyRepository):
    def __init__(self, session: Session):
        self.session = session
    
    def save(self, company: Company) -> None:
        # Check if company already exists
        company_model = self.session.query(CompanyModel).filter(
            CompanyModel.id == company.id
        ).first()
        
        if not company_model:
            # Create new company
            company_model = CompanyModel(
                id=company.id,
                display_name=company.display_name,
                legal_name=company.legal_name,
                created_at=company.created_at
            )
            self.session.add(company_model)
        else:
            # Update existing company
            company_model.display_name = company.display_name
            company_model.legal_name = company.legal_name
        
        self.session.commit()
    
    def find_by_id(self, company_id: UUID) -> Optional[Company]:
        company_model = self.session.query(CompanyModel).filter(
            CompanyModel.id == company_id
        ).first()
        
        if not company_model:
            return None
        
        return self._to_domain_entity(company_model)
    
    def find_by_legal_name(self, legal_name: str) -> Optional[Company]:
        company_model = self.session.query(CompanyModel).filter(
            CompanyModel.legal_name == legal_name
        ).first()
        
        if not company_model:
            return None
        
        return self._to_domain_entity(company_model)
    
    def find_all(self) -> List[Company]:
        company_models = self.session.query(CompanyModel).all()
        return [self._to_domain_entity(model) for model in company_models]
    
    def _to_domain_entity(self, model: CompanyModel) -> Company:
        return Company(
            display_name=model.display_name,
            legal_name=model.legal_name,
            id=model.id,
            created_at=model.created_at
        )


class SQLAlchemyDepartmentRepository(DepartmentRepository):
    def __init__(self, session: Session):
        self.session = session
    
    def save(self, department: Department) -> None:
        # Check if department already exists
        dept_model = self.session.query(DepartmentModel).filter(
            DepartmentModel.id == department.id
        ).first()
        
        if not dept_model:
            # Create new department
            dept_model = DepartmentModel(
                id=department.id,
                name=department.name,
                description=department.description,
                lead_id=department.lead.id if department.lead else None
            )
            self.session.add(dept_model)
        else:
            # Update existing department
            dept_model.name = department.name
            dept_model.description = department.description
            dept_model.lead_id = department.lead.id if department.lead else None
        
        self.session.commit()
    
    def find_by_id(self, department_id: UUID) -> Optional[Department]:
        dept_model = self.session.query(DepartmentModel).filter(
            DepartmentModel.id == department_id
        ).options(
            joinedload(DepartmentModel.lead)
        ).first()
        
        if not dept_model:
            return None
        
        return self._to_domain_entity(dept_model)
    
    def find_by_name(self, name: str) -> Optional[Department]:
        dept_model = self.session.query(DepartmentModel).filter(
            DepartmentModel.name == name
        ).options(
            joinedload(DepartmentModel.lead)
        ).first()
        
        if not dept_model:
            return None
        
        return self._to_domain_entity(dept_model)
    
    def find_all(self) -> List[Department]:
        dept_models = self.session.query(DepartmentModel).options(
            joinedload(DepartmentModel.lead)
        ).all()
        return [self._to_domain_entity(model) for model in dept_models]
    
    def find_by_lead(self, lead_id: UUID) -> List[Department]:
        dept_models = self.session.query(DepartmentModel).filter(
            DepartmentModel.lead_id == lead_id
        ).options(
            joinedload(DepartmentModel.lead)
        ).all()
        return [self._to_domain_entity(model) for model in dept_models]
    
    def _to_domain_entity(self, model: DepartmentModel) -> Department:
        # This will need to be expanded to handle the lead and other relationships
        lead = None
        if model.lead:
            lead = Employee(
                name=PersonName(
                    first=model.lead.first_name,
                    middle=model.lead.middle_name,
                    last=model.lead.last_name
                ),
                contacts=ContactInfo(
                    email=model.lead.email,
                    phone=model.lead.phone
                ),
                position=Role(
                    title=model.lead.position_title,
                    grade=model.lead.position_grade
                ),
                hired_at=model.lead.hired_at,
                birth_date=model.lead.birth_date,
                is_remote=model.lead.is_remote,
                id=model.lead.id
            )
        
        return Department(
            name=model.name,
            id=model.id,
            description=model.description,
            lead=lead
        )


class SQLAlchemyEmployeeRepository(EmployeeRepository):
    def __init__(self, session: Session):
        self.session = session
    
    def save(self, employee: Employee) -> None:
        # Check if employee already exists
        employee_model = self.session.query(EmployeeModel).filter(
            EmployeeModel.id == employee.id
        ).first()
        
        if not employee_model:
            # Create new employee
            employee_model = EmployeeModel(
                id=employee.id,
                first_name=employee.name.first,
                middle_name=employee.name.middle,
                last_name=employee.name.last,
                email=employee.contacts.email,
                phone=employee.contacts.phone,
                position_title=employee.position.title,
                position_grade=employee.position.grade,
                hired_at=employee.hired_at,
                birth_date=employee.birth_date,
                is_remote=employee.is_remote
            )
            self.session.add(employee_model)
        else:
            # Update existing employee
            employee_model.first_name = employee.name.first
            employee_model.middle_name = employee.name.middle
            employee_model.last_name = employee.name.last
            employee_model.email = employee.contacts.email
            employee_model.phone = employee.contacts.phone
            employee_model.position_title = employee.position.title
            employee_model.position_grade = employee.position.grade
            employee_model.hired_at = employee.hired_at
            employee_model.birth_date = employee.birth_date
            employee_model.is_remote = employee.is_remote
        
        # Handle availability slots
        if employee.availability:
            # Delete existing slots and recreate
            self.session.query(AvailabilitySlotModel).filter(
                AvailabilitySlotModel.employee_id == employee.id
            ).delete()
            
            for slot in employee.availability:
                slot_model = AvailabilitySlotModel(
                    employee_id=employee.id,
                    start=slot.start,
                    end=slot.end,
                    slot_type=slot.slot_type
                )
                self.session.add(slot_model)
        
        self.session.commit()
    
    def find_by_id(self, employee_id: UUID) -> Optional[Employee]:
        employee_model = self.session.query(EmployeeModel).filter(
            EmployeeModel.id == employee_id
        ).options(
            joinedload(EmployeeModel.availability_slots)
        ).first()
        
        if not employee_model:
            return None
        
        return self._to_domain_entity(employee_model)
    
    def find_all(self) -> List[Employee]:
        employee_models = self.session.query(EmployeeModel).options(
            joinedload(EmployeeModel.availability_slots)
        ).all()
        return [self._to_domain_entity(model) for model in employee_models]
    
    def find_by_name(self, name_query: str) -> List[Employee]:
        q = f"%{name_query}%"
        employee_models = self.session.query(EmployeeModel).filter(
            or_(
                EmployeeModel.first_name.ilike(q),
                EmployeeModel.middle_name.ilike(q),
                EmployeeModel.last_name.ilike(q)
            )
        ).options(
            joinedload(EmployeeModel.availability_slots)
        ).all()
        return [self._to_domain_entity(model) for model in employee_models]
    
    def find_by_department(self, department_id: UUID) -> List[Employee]:
        employee_models = self.session.query(EmployeeModel).join(
            EmployeeModel.departments
        ).filter(
            DepartmentModel.id == department_id
        ).options(
            joinedload(EmployeeModel.availability_slots)
        ).all()
        return [self._to_domain_entity(model) for model in employee_models]
    
    def find_by_project(self, project_id: UUID) -> List[Employee]:
        employee_models = self.session.query(EmployeeModel).join(
            EmployeeModel.projects
        ).filter(
            ProjectModel.id == project_id
        ).options(
            joinedload(EmployeeModel.availability_slots)
        ).all()
        return [self._to_domain_entity(model) for model in employee_models]
    
    def find_by_email(self, email: str) -> Optional[Employee]:
        employee_model = self.session.query(EmployeeModel).filter(
            EmployeeModel.email == email
        ).options(
            joinedload(EmployeeModel.availability_slots)
        ).first()
        
        if not employee_model:
            return None
        
        return self._to_domain_entity(employee_model)
    
    def find_birthdays_between(
        self,
        start_date: date,
        end_date: date
    ) -> List[Employee]:
        # This is a bit tricky because we need to compare just month and day
        employee_models = self.session.query(EmployeeModel).all()
        
        # Filter in Python (not ideal for large datasets but works for our case)
        result = []
        for emp in employee_models:
            bday = emp.birth_date
            current_year_bday = date(start_date.year, bday.month, bday.day)
            if start_date <= current_year_bday <= end_date:
                result.append(self._to_domain_entity(emp))
        
        return result
    
    def _to_domain_entity(self, model: EmployeeModel) -> Employee:
        availability = []
        for slot in model.availability_slots:
            availability.append(AvailabilitySlot(
                start=slot.start,
                end=slot.end,
                slot_type=slot.slot_type
            ))
        
        return Employee(
            name=PersonName(
                first=model.first_name,
                middle=model.middle_name,
                last=model.last_name
            ),
            contacts=ContactInfo(
                email=model.email,
                phone=model.phone
            ),
            position=Role(
                title=model.position_title,
                grade=model.position_grade
            ),
            hired_at=model.hired_at,
            birth_date=model.birth_date,
            is_remote=model.is_remote,
            id=model.id,
            availability=availability
        )


class SQLAlchemyProjectRepository(ProjectRepository):
    def __init__(self, session: Session):
        self.session = session
        self.department_repo = SQLAlchemyDepartmentRepository(session)
    
    def save(self, project: Project) -> None:
        # Check if project already exists
        project_model = self.session.query(ProjectModel).filter(
            ProjectModel.id == project.id
        ).first()
        
        if not project_model:
            # Create new project
            project_model = ProjectModel(
                id=project.id,
                code=project.code,
                name=project.name,
                description=project.description,
                status=project.status,
                started_at=project.started_at,
                finished_at=project.finished_at,
                responsible_dept_id=project.responsible_dept.id
            )
            self.session.add(project_model)
        else:
            # Update existing project
            project_model.code = project.code
            project_model.name = project.name
            project_model.description = project.description
            project_model.status = project.status
            project_model.started_at = project.started_at
            project_model.finished_at = project.finished_at
            project_model.responsible_dept_id = project.responsible_dept.id
        
        self.session.commit()
    
    def find_by_id(self, project_id: UUID) -> Optional[Project]:
        project_model = self.session.query(ProjectModel).filter(
            ProjectModel.id == project_id
        ).options(
            joinedload(ProjectModel.responsible_dept)
        ).first()
        
        if not project_model:
            return None
        
        return self._to_domain_entity(project_model)
    
    def find_by_code(self, code: str) -> Optional[Project]:
        project_model = self.session.query(ProjectModel).filter(
            ProjectModel.code == code
        ).options(
            joinedload(ProjectModel.responsible_dept)
        ).first()
        
        if not project_model:
            return None
        
        return self._to_domain_entity(project_model)
    
    def find_all(self) -> List[Project]:
        project_models = self.session.query(ProjectModel).options(
            joinedload(ProjectModel.responsible_dept)
        ).all()
        return [self._to_domain_entity(model) for model in project_models]
    
    def find_by_department(self, department_id: UUID) -> List[Project]:
        project_models = self.session.query(ProjectModel).filter(
            ProjectModel.responsible_dept_id == department_id
        ).options(
            joinedload(ProjectModel.responsible_dept)
        ).all()
        return [self._to_domain_entity(model) for model in project_models]
    
    def find_by_status(self, status: ProjectStatus) -> List[Project]:
        project_models = self.session.query(ProjectModel).filter(
            ProjectModel.status == status
        ).options(
            joinedload(ProjectModel.responsible_dept)
        ).all()
        return [self._to_domain_entity(model) for model in project_models]
    
    def find_by_employee(self, employee_id: UUID) -> List[Project]:
        project_models = self.session.query(ProjectModel).join(
            ProjectModel.employees
        ).filter(
            EmployeeModel.id == employee_id
        ).options(
            joinedload(ProjectModel.responsible_dept)
        ).all()
        return [self._to_domain_entity(model) for model in project_models]
    
    def _to_domain_entity(self, model: ProjectModel) -> Project:
        dept = self.department_repo.find_by_id(model.responsible_dept_id)
        
        return Project(
            code=model.code,
            name=model.name,
            description=model.description,
            responsible_dept=dept,
            status=model.status,
            id=model.id,
            started_at=model.started_at,
            finished_at=model.finished_at
        )


class SQLAlchemyTaskRepository(TaskRepository):
    def __init__(self, session: Session):
        self.session = session
        self.project_repo = SQLAlchemyProjectRepository(session)
    
    def save(self, task: Task) -> None:
        # Check if task already exists
        task_model = self.session.query(TaskModel).filter(
            TaskModel.id == task.id
        ).first()
        
        if not task_model:
            # Create new task
            task_model = TaskModel(
                id=task.id,
                title=task.title,
                description=task.description,
                priority=task.priority,
                status=task.status,
                created_at=task.created_at,
                planned_start=task.planned_start,
                due_date=task.due_date,
                project_id=task.project.id
            )
            self.session.add(task_model)
        else:
            # Update existing task
            task_model.title = task.title
            task_model.description = task.description
            task_model.priority = task.priority
            task_model.status = task.status
            task_model.planned_start = task.planned_start
            task_model.due_date = task.due_date
            task_model.project_id = task.project.id
        
        self.session.commit()
    
    def find_by_id(self, task_id: UUID) -> Optional[Task]:
        task_model = self.session.query(TaskModel).filter(
            TaskModel.id == task_id
        ).options(
            joinedload(TaskModel.project)
        ).first()
        
        if not task_model:
            return None
        
        return self._to_domain_entity(task_model)
    
    def find_all(self) -> List[Task]:
        task_models = self.session.query(TaskModel).options(
            joinedload(TaskModel.project)
        ).all()
        return [self._to_domain_entity(model) for model in task_models]
    
    def find_by_project(self, project_id: UUID) -> List[Task]:
        task_models = self.session.query(TaskModel).filter(
            TaskModel.project_id == project_id
        ).options(
            joinedload(TaskModel.project)
        ).all()
        return [self._to_domain_entity(model) for model in task_models]
    
    def find_by_status(self, status: TaskStatus) -> List[Task]:
        task_models = self.session.query(TaskModel).filter(
            TaskModel.status == status
        ).options(
            joinedload(TaskModel.project)
        ).all()
        return [self._to_domain_entity(model) for model in task_models]
    
    def find_by_priority(self, priority: TaskPriority) -> List[Task]:
        task_models = self.session.query(TaskModel).filter(
            TaskModel.priority == priority
        ).options(
            joinedload(TaskModel.project)
        ).all()
        return [self._to_domain_entity(model) for model in task_models]
    
    def find_by_employee(self, employee_id: UUID) -> List[Task]:
        task_models = self.session.query(TaskModel).join(
            TaskModel.employees
        ).filter(
            EmployeeModel.id == employee_id
        ).options(
            joinedload(TaskModel.project)
        ).all()
        return [self._to_domain_entity(model) for model in task_models]
    
    def find_due_by_date(self, due_date: date) -> List[Task]:
        task_models = self.session.query(TaskModel).filter(
            TaskModel.due_date == due_date
        ).options(
            joinedload(TaskModel.project)
        ).all()
        return [self._to_domain_entity(model) for model in task_models]
    
    def _to_domain_entity(self, model: TaskModel) -> Task:
        project = self.project_repo.find_by_id(model.project_id)
        
        return Task(
            title=model.title,
            description=model.description,
            project=project,
            priority=model.priority,
            status=model.status,
            id=model.id,
            created_at=model.created_at,
            planned_start=model.planned_start,
            due_date=model.due_date
        )


class SQLAlchemyEventRepository(EventRepository):
    def __init__(self, session: Session):
        self.session = session
        self.employee_repo = SQLAlchemyEmployeeRepository(session)
    
    def save(self, event: Event) -> None:
        # Check if event already exists
        event_model = self.session.query(EventModel).filter(
            EventModel.id == event.id
        ).first()
        
        if not event_model:
            # Create new event
            event_model = EventModel(
                id=event.id,
                title=event.title,
                description=event.description,
                start_at=event.start_at,
                end_at=event.end_at,
                event_type=event.event_type
            )
            self.session.add(event_model)
        else:
            # Update existing event
            event_model.title = event.title
            event_model.description = event.description
            event_model.start_at = event.start_at
            event_model.end_at = event.end_at
            event_model.event_type = event.event_type
        
        # Handle participants
        if event.participants:
            # Delete existing participants and recreate
            self.session.query(EventParticipantModel).filter(
                EventParticipantModel.event_id == event.id
            ).delete()
            
            for participant in event.participants:
                participant_model = EventParticipantModel(
                    event_id=event.id,
                    employee_id=participant.employee.id,
                    rsvp=participant.rsvp
                )
                self.session.add(participant_model)
        
        self.session.commit()
    
    def find_by_id(self, event_id: UUID) -> Optional[Event]:
        event_model = self.session.query(EventModel).filter(
            EventModel.id == event_id
        ).options(
            joinedload(EventModel.participants).joinedload(EventParticipantModel.employee)
        ).first()
        
        if not event_model:
            return None
        
        return self._to_domain_entity(event_model)
    
    def find_all(self) -> List[Event]:
        event_models = self.session.query(EventModel).options(
            joinedload(EventModel.participants).joinedload(EventParticipantModel.employee)
        ).all()
        return [self._to_domain_entity(model) for model in event_models]
    
    def find_by_timeframe(self, start: datetime, end: datetime) -> List[Event]:
        event_models = self.session.query(EventModel).filter(
            EventModel.start_at >= start,
            EventModel.end_at <= end
        ).options(
            joinedload(EventModel.participants).joinedload(EventParticipantModel.employee)
        ).all()
        return [self._to_domain_entity(model) for model in event_models]
    
    def find_by_type(self, event_type: EventType) -> List[Event]:
        event_models = self.session.query(EventModel).filter(
            EventModel.event_type == event_type
        ).options(
            joinedload(EventModel.participants).joinedload(EventParticipantModel.employee)
        ).all()
        return [self._to_domain_entity(model) for model in event_models]
    
    def find_by_participant(self, employee_id: UUID) -> List[Event]:
        event_models = self.session.query(EventModel).join(
            EventModel.participants
        ).filter(
            EventParticipantModel.employee_id == employee_id
        ).options(
            joinedload(EventModel.participants).joinedload(EventParticipantModel.employee)
        ).all()
        return [self._to_domain_entity(model) for model in event_models]
    
    def find_upcoming(self, days_ahead: int) -> List[Event]:
        now = datetime.utcnow()
        horizon = now + timedelta(days=days_ahead)
        
        event_models = self.session.query(EventModel).filter(
            EventModel.start_at >= now,
            EventModel.start_at <= horizon
        ).options(
            joinedload(EventModel.participants).joinedload(EventParticipantModel.employee)
        ).all()
        return [self._to_domain_entity(model) for model in event_models]
    
    def _to_domain_entity(self, model: EventModel) -> Event:
        participants = []
        for p in model.participants:
            employee = self.employee_repo.find_by_id(p.employee_id)
            participants.append(EventParticipant(
                employee=employee,
                rsvp=p.rsvp
            ))
        
        event = Event(
            title=model.title,
            description=model.description,
            start_at=model.start_at,
            end_at=model.end_at,
            event_type=model.event_type,
            id=model.id
        )
        event.participants = participants
        return event


class SQLAlchemyKnowledgeArticleRepository(KnowledgeArticleRepository):
    def __init__(self, session: Session):
        self.session = session
        self.employee_repo = SQLAlchemyEmployeeRepository(session)
    
    def save(self, article: KnowledgeArticle) -> None:
        # Check if article already exists
        article_model = self.session.query(KnowledgeArticleModel).filter(
            KnowledgeArticleModel.id == article.id
        ).first()
        
        if not article_model:
            # Create new article
            article_model = KnowledgeArticleModel(
                id=article.id,
                title=article.title,
                body=article.body,
                importance=article.importance,
                created_at=article.created_at,
                author_id=article.author.id
            )
            self.session.add(article_model)
        else:
            # Update existing article
            article_model.title = article.title
            article_model.body = article.body
            article_model.importance = article.importance
            article_model.author_id = article.author.id
        
        # Handle tags
        if article.tags:
            # Delete existing tags and recreate
            self.session.query(ArticleTagModel).filter(
                ArticleTagModel.article_id == article.id
            ).delete()
            
            for tag in article.tags:
                tag_model = ArticleTagModel(
                    article_id=article.id,
                    tag=tag
                )
                self.session.add(tag_model)
        
        self.session.commit()
    
    def find_by_id(self, article_id: UUID) -> Optional[KnowledgeArticle]:
        article_model = self.session.query(KnowledgeArticleModel).filter(
            KnowledgeArticleModel.id == article_id
        ).options(
            joinedload(KnowledgeArticleModel.author),
            joinedload(KnowledgeArticleModel.tags)
        ).first()
        
        if not article_model:
            return None
        
        return self._to_domain_entity(article_model)
    
    def find_all(self) -> List[KnowledgeArticle]:
        article_models = self.session.query(KnowledgeArticleModel).options(
            joinedload(KnowledgeArticleModel.author),
            joinedload(KnowledgeArticleModel.tags)
        ).all()
        return [self._to_domain_entity(model) for model in article_models]
    
    def find_by_title(self, title_query: str) -> List[KnowledgeArticle]:
        q = f"%{title_query}%"
        article_models = self.session.query(KnowledgeArticleModel).filter(
            KnowledgeArticleModel.title.ilike(q)
        ).options(
            joinedload(KnowledgeArticleModel.author),
            joinedload(KnowledgeArticleModel.tags)
        ).all()
        return [self._to_domain_entity(model) for model in article_models]
    
    def find_by_author(self, author_id: UUID) -> List[KnowledgeArticle]:
        article_models = self.session.query(KnowledgeArticleModel).filter(
            KnowledgeArticleModel.author_id == author_id
        ).options(
            joinedload(KnowledgeArticleModel.author),
            joinedload(KnowledgeArticleModel.tags)
        ).all()
        return [self._to_domain_entity(model) for model in article_models]
    
    def find_by_tag(self, tag: str) -> List[KnowledgeArticle]:
        article_models = self.session.query(KnowledgeArticleModel).join(
            KnowledgeArticleModel.tags
        ).filter(
            ArticleTagModel.tag == tag
        ).options(
            joinedload(KnowledgeArticleModel.author),
            joinedload(KnowledgeArticleModel.tags)
        ).all()
        return [self._to_domain_entity(model) for model in article_models]
    
    def find_by_importance(self, importance: Importance) -> List[KnowledgeArticle]:
        article_models = self.session.query(KnowledgeArticleModel).filter(
            KnowledgeArticleModel.importance == importance
        ).options(
            joinedload(KnowledgeArticleModel.author),
            joinedload(KnowledgeArticleModel.tags)
        ).all()
        return [self._to_domain_entity(model) for model in article_models]
    
    def search(self, query: str) -> List[KnowledgeArticle]:
        q = f"%{query}%"
        article_models = self.session.query(KnowledgeArticleModel).filter(
            or_(
                KnowledgeArticleModel.title.ilike(q),
                KnowledgeArticleModel.body.ilike(q)
            )
        ).options(
            joinedload(KnowledgeArticleModel.author),
            joinedload(KnowledgeArticleModel.tags)
        ).all()
        return [self._to_domain_entity(model) for model in article_models]
    
    def _to_domain_entity(self, model: KnowledgeArticleModel) -> KnowledgeArticle:
        author = self.employee_repo.find_by_id(model.author_id)
        
        tags = set()
        for tag_model in model.tags:
            tags.add(tag_model.tag)
        
        return KnowledgeArticle(
            title=model.title,
            body=model.body,
            author=author,
            importance=model.importance,
            id=model.id,
            created_at=model.created_at,
            tags=tags
        )