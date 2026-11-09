from datetime import date
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SelectField, IntegerField, FloatField, DateField, TextAreaField
from wtforms.validators import DataRequired, Email, Length, EqualTo, Optional, NumberRange
from models import CATEGORIES

class LoginForm(FlaskForm):
    username = StringField('Username or Email', validators=[DataRequired(), Length(min=3, max=120)])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Keep me signed in')

class RegisterForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=64)])
    email = StringField('Email Address', validators=[DataRequired(), Email(), Length(max=120)])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6, message='Password must be at least 6 characters')])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password', message='Passwords must match')])
    company_name = StringField('Company Name', validators=[Optional(), Length(max=120)], default='Aura Enterprise')
    seed_sample_data = BooleanField('Preload Interactive Enterprise Sales Dataset', default=True)

class TransactionForm(FlaskForm):
    product_name = StringField('Product / Service Name', validators=[DataRequired(), Length(max=150)])
    category = SelectField('Category', choices=[(c, c) for c in CATEGORIES], validators=[DataRequired()])
    quantity = IntegerField('Quantity', default=1, validators=[DataRequired(), NumberRange(min=1, message='Quantity must be at least 1')])
    unit_price = FloatField('Unit Price', validators=[DataRequired(), NumberRange(min=0.01, message='Unit price must be positive')])
    transaction_date = DateField('Transaction Date', default=date.today, validators=[DataRequired()])
    customer_name = StringField('Client / Customer', validators=[Optional(), Length(max=120)], default='Enterprise Client')
    status = SelectField('Status', choices=[('Completed', 'Completed'), ('Pending', 'Pending'), ('Processing', 'Processing')], default='Completed')
    description = TextAreaField('Description / Notes', validators=[Optional(), Length(max=1000)])

class ProfileForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=64)])
    email = StringField('Email Address', validators=[DataRequired(), Email(), Length(max=120)])
    company_name = StringField('Company / Organization', validators=[Optional(), Length(max=120)])
    currency = SelectField('Currency', choices=[
        ('₹', 'Indian Rupee (₹)'),
        ('$', 'USD ($)'),
        ('€', 'EUR (€)'),
        ('£', 'GBP (£)'),
        ('¥', 'JPY (¥)'),
        ('C$', 'CAD ($)'),
        ('A$', 'AUD ($)')
    ], default='₹')
    premium_threshold = FloatField('High-Value Sales Threshold', validators=[DataRequired(), NumberRange(min=1.0, message='Threshold must be positive')])
    theme_accent = SelectField('Accent Glow', choices=[
        ('cyan', 'Electric Cyan (Default)'),
        ('purple', 'Cyber Purple'),
        ('blue', 'Neon Blue'),
        ('emerald', 'Quantum Emerald')
    ], default='cyan')
    new_password = PasswordField('New Password (optional)', validators=[Optional(), Length(min=6)])
