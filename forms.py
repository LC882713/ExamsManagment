from flask_wtf import FlaskForm
from wtforms import *
from wtforms.validators import *

class RegistrationForm(Form):
    firstName = StringField('First Name', [validators.Length(min=1, max=50)])
    lastName = StringField('Last Name', [validators.Length(min=1, max=50)])
    email = StringField('Email Address', [validators.Email(message="This field is required")])
    password = PasswordField('Password', [validators.Length(min=6, max=50)])
    role = SelectField('Role', choices=[('professor', 'Professor'), ('student', 'Student')])
    gender = RadioField('Gender', choices=[('female', 'Female'), ('male', 'Male'), ('other', 'Other')])
    submit = SubmitField('Create Account')
    
class LoginForm(FlaskForm):
    email = StringField('Email', [Email(message="This field is required")], render_kw={"placeholder": "Email"})
    password = PasswordField('Password', [DataRequired(message="This field is required")], render_kw={"placeholder": "Password"})
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')
    
class ExamForm(FlaskForm):
    examName = StringField('Name:', validators=[DataRequired(message="This field is required")])
    credits = StringField('Credits:', validators=[DataRequired(message="This field is required")])
    num_tests = IntegerField('Number of composed tests:', validators=[InputRequired(message="This field is required"), NumberRange(min=1, max=6)])
    submit = SubmitField('Submit Exam')

class justTestForm(FlaskForm):
    id_exam=IntegerField('id_exam')
    type = SelectField('Type',choices=[('Written', 'Written'),('Oral', 'Oral'),('Project', 'Project')])
    bonus = IntegerField('Bonus (between 0 and 3)', render_kw={"min": "0", "max": "3"})
    grade_weight=IntegerField('Percentage of the grade weight (from 10 to 100)*', render_kw={"min": "10", "max": "100"})
    name = StringField('Test Name')
    submit = SubmitField('Create')
    
class TestForm(FlaskForm):
    id_exams=IntegerField('id_exams', validators=[DataRequired()])
    type = SelectField('Type',choices=[('Written', 'Written'),('Oral', 'Oral'),('Project', 'Project')])
    bonus = IntegerField('Bonus (between 0 and 3)', render_kw={"min": "0", "max": "3"})
    grade_weight=IntegerField('Percentage of the grade weight (from 10 to 100)*', render_kw={"min": "10", "max": "100"})
    name = StringField('Test Name')
    submit = SubmitField('Create')

class TestCreatedForm (FlaskForm):
    id_test = IntegerField('Test ID')
    name = StringField('Test Name')
    type = SelectField('Type',choices=[('Written', 'Written'),('Oral', 'Oral'),('Project', 'Project')])
    bonus = IntegerField('Bonus (between 0 and 3)', render_kw={"min": "0", "max": "3"})
    grade_weight=IntegerField('Percentage of the grade weight (from 10 to 100)*', render_kw={"min": "10", "max": "100"})
    date = DateField('Select the Date', validators=[DataRequired(message="This field is required")], format='%Y-%m-%d')
    submit = SubmitField('Submit')


class DateExamForm(FlaskForm):
    selected_date = DateField('Select the Date', validators=[DataRequired(message="This field is required")], format='%Y-%m-%d')
    id_tests = IntegerField('id_tests')
    submit = SubmitField('Set this date')

class GradeForm(FlaskForm):
    id_subscribes=IntegerField('id_subscribes')
    score = IntegerField('Score', validators=[InputRequired(), NumberRange(min=1, max=30)])
    submit = SubmitField('Insert Score')

class SubscribeForm(FlaskForm):
    id = IntegerField('Student ID')
    id_tests = IntegerField('Test ID')
    id_sessions = IntegerField('Test ID')
    verb_date = DateField('Verb Date')
    submit = SubmitField('Subscribe')


class GradeAcceptForm(FlaskForm):
    CHOICES = [('accept', 'Accept'), ('reject', 'Reject')]
    register = SelectField('Accept or Reject', choices=CHOICES)
    submit = SubmitField('Submit', render_kw={"class": "btn btn-primary"})

class listsubscribe(FlaskForm):
    id_registrations = IntegerField('Registrations Id')
    submit = SubmitField('Delete')
    
class registerExamGrade(FlaskForm):
    id_exam = IntegerField('Exam Id')
    id_students = IntegerField('Student Id')
    total_grade = IntegerField('Total grade')
    submit = SubmitField('Register')