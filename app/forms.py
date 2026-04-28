from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, PasswordField, SubmitField, TextAreaField, FloatField, SelectField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from flask_login import current_user
from app.models import User

class RegistrationForm(FlaskForm):
    username = StringField('Nazwa użytkownika', validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email(message="Wprowadź poprawny adres email.")])
    role = SelectField('Zarejestruj mnie jako:', choices=[('teacher', 'Nauczyciel'), ('student', 'Uczeń')], validators=[DataRequired()])
    password = PasswordField('Hasło', validators=[DataRequired(), Length(min=8, message="Hasło musi mieć min. 8 znaków.")])
    confirm_password = PasswordField('Potwierdź hasło', validators=[DataRequired(), EqualTo('password', message="Hasła muszą być identyczne.")])
    submit = SubmitField('Zarejestruj się')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('Ta nazwa jest zajęta.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Ten email jest już zajęty.')

    def validate_password(self, password):
        if not any(char.isdigit() for char in password.data):
            raise ValidationError('Hasło musi zawierać cyfrę.')
        if not any(char.isupper() for char in password.data):
            raise ValidationError('Hasło musi zawierać wielką literę.')

class LoginForm(FlaskForm):
    username_or_email = StringField('Email lub Nazwa użytkownika', validators=[DataRequired()])
    password = PasswordField('Hasło', validators=[DataRequired()])
    submit = SubmitField('Zaloguj')

class UpdateAccountForm(FlaskForm):
    username = StringField('Nazwa użytkownika', validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    first_name = StringField('Imię (opcjonalnie)')
    last_name = StringField('Nazwisko (opcjonalnie)')
    bio = TextAreaField('O mnie (opcjonalnie)')
    education = TextAreaField('Wykształcenie')
    profile_pic = FileField('Zmień zdjęcie profilowe', validators=[FileAllowed(['jpg', 'png', 'jpeg'])])
    cover_pic = FileField('Zmień zdjęcie w tle', validators=[FileAllowed(['jpg', 'png', 'jpeg'])])
    submit = SubmitField('Zapisz zmiany')

    def validate_username(self, username):
        if username.data != current_user.username:
            user = User.query.filter_by(username=username.data).first()
            if user:
                raise ValidationError('Ta nazwa jest zajęta.')

    def validate_email(self, email):
        if email.data != current_user.email:
            user = User.query.filter_by(email=email.data).first()
            if user:
                raise ValidationError('Ten email jest zajęty.')

class AdForm(FlaskForm):
    title = StringField('Tytuł ogłoszenia', validators=[DataRequired(), Length(max=100)])
    subject = SelectField('PRZEDMIOT', choices=[
        ('Matematyka', 'Matematyka'),
        ('Język Polski', 'Język Polski'),
        ('Język Angielski', 'Język Angielski'),
        ('Chemia', 'Chemia'),
        ('Fizyka', 'Fizyka'),
        ('Biologia', 'Biologia'),
        ('Historia', 'Historia'),
        ('Geografia', 'Geografia'),
        ('Informatyka', 'Informatyka'),
        ('Język Niemiecki', 'Język Niemiecki'),
        ('Inny', 'Inny')
    ], validators=[DataRequired()])
    description = TextAreaField('Opis', validators=[DataRequired()])
    price = FloatField('Cena za godzinę (PLN)', validators=[DataRequired()])
    submit = SubmitField('Zapisz ogłoszenie')