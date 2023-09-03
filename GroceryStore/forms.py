from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, FloatField, IntegerField, SelectField, DateField
from wtforms.validators import DataRequired, Length, Email, EqualTo, Optional

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    is_admin = BooleanField('Register as Admin')
    submit = SubmitField('Sign Up')

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Log In')

class AdminLoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Log In')

class CategoryForm(FlaskForm):
    name = StringField('Category Name', validators=[DataRequired(), Length(max=50)])
    submit = SubmitField('Submit')

class ProductForm(FlaskForm):
    name = StringField('Product Name', validators=[DataRequired(), Length(max=100)])
    manufacture_date = DateField('Manufacture Date', validators=[Optional()])
    expiry_date = DateField('Expiry Date', validators=[Optional()])
    rate_per_unit = FloatField('Rate per Unit', validators=[DataRequired()])
    category = SelectField('Category', coerce=int, choices=[])
    units = IntegerField('Number of Units', validators=[DataRequired()])
    submit = SubmitField('Submit')

class ProductSearchForm(FlaskForm):
    category = SelectField('Category', coerce=int, choices=[])
    min_price = FloatField('Min Price')
    max_price = FloatField('Max Price')
    start_date = DateField('Manufacture Date')
    end_date = DateField('Expiry Date')