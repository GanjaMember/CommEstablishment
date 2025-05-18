from flask_wtf import FlaskForm
from wtforms import (
    StringField,
    TextAreaField,
    SelectField,
    SelectMultipleField,
    DateField,
    SubmitField,
)
from wtforms.validators import DataRequired


class CompanyForm(FlaskForm):
    name = StringField("Название", validators=[DataRequired()])
    description = TextAreaField("Описание", validators=[DataRequired()])
    submit = SubmitField("Создать компанию")


class ChatForm(FlaskForm):
    name = StringField("Название", validators=[DataRequired()])
    employees = SelectMultipleField("Сотрудники", choices=[], coerce=int)
    submit = SubmitField("Создать группу")


class DepartmentForm(FlaskForm):
    name = StringField("Название", validators=[DataRequired()])
    description = TextAreaField("Описание", validators=[DataRequired()])
    submit = SubmitField("Создать отдел")


class ProjectForm(FlaskForm):
    name = StringField("Название", validators=[DataRequired()])
    description = TextAreaField("Описание", validators=[DataRequired()])
    responsible_department_id = SelectField(
        "Ответственный отдел", choices=[], coerce=int, validators=[DataRequired()]
    )
    employees = SelectMultipleField("Сотрудники", choices=[], coerce=int)
    submit = SubmitField("Создать проект")


class EmployeeForm(FlaskForm):
    surname = StringField("Фамилия", validators=[DataRequired()])
    name = StringField("Имя", validators=[DataRequired()])
    patronymic = StringField("Отчество", validators=[])
    hire_date = DateField(
        "Дата приема на работу", format="%Y-%m-%d", validators=[DataRequired()]
    )
    birth_date = DateField(
        "Дата рождения", format="%Y-%m-%d", validators=[DataRequired()]
    )
    contact = StringField("Контактные данные", validators=[DataRequired()])
    email = StringField("Email", validators=[DataRequired()])
    submit = SubmitField("Создать сотрудника")


class DepartmentIdForm(FlaskForm):
    department_id = SelectField(
        "Отдел", 
        choices=[(0, "Все отделы")], 
        coerce=int, 
        validators=[DataRequired()]
    )
    submit = SubmitField("Выбрать отдел")


class ProjectIdForm(FlaskForm):
    project_id = SelectField(
        "Проект", 
        choices=[(0, "Все проекты")], 
        coerce=int, 
        validators=[DataRequired()]
    )
    submit = SubmitField("Выбрать проект")


class TaskForm(FlaskForm):
    name = StringField("Название", validators=[DataRequired()])
    description = TextAreaField("Описание", validators=[DataRequired()])
    start_date = DateField(
        "Дата начала", format="%Y-%m-%d", validators=[DataRequired()]
    )
    due_date = DateField(
        "Дата окончания", format="%Y-%m-%d", validators=[DataRequired()]
    )
    priority = SelectField(
        "Приоритет",
        choices=[
            (1, "Низкий"),
            (2, "Средний"),
            (3, "Высокий"),
        ],
        validators=[DataRequired()],
    )
    project_id = SelectField(
        "Проект", choices=[], coerce=int, validators=[DataRequired()]
    )
    employees = SelectMultipleField("Сотрудники", choices=[], coerce=int)
    submit = SubmitField("Создать задачу")