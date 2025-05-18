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
