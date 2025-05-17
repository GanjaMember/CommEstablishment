from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField
from wtforms.validators import DataRequired

class CompanyForm(FlaskForm):
    name = StringField("Название", validators=[DataRequired()])
    description = TextAreaField("Описание", validators=[DataRequired()])
    submit = SubmitField("Создать компанию")