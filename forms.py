"""
forms.py — Web Forms for BeehiveOfAI
======================================
"""

from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed, FileRequired
from wtforms import StringField, PasswordField, SelectField, TextAreaField, FloatField, IntegerField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo, Length, NumberRange, Optional


class RegisterForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=80)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password', message='Passwords must match')])
    phone = StringField('Phone Number (e.g. +972544752626)',
                        validators=[DataRequired(), Length(min=10, max=20)])
    role = SelectField('I want to be a:', choices=[
        ('worker', '🐝 Worker Bee — Earn money by processing AI tasks'),
        ('queen', '👑 Queen Bee — Lead a team of Worker Bees'),
        ('beekeeper', '🏢 Beekeeper — Submit AI tasks for my company')
    ], validators=[DataRequired()])
    submit = SubmitField('Create Account')


class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')


class CreateHiveForm(FlaskForm):
    name = StringField('Hive Name', validators=[DataRequired(), Length(min=3, max=100)])
    description = TextAreaField('Description', validators=[DataRequired(), Length(min=10, max=1000)])
    model_family = SelectField('AI Model Family', choices=[
        ('deepseek', 'DeepSeek (General Reasoning)'),
        ('qwen', 'Qwen (Coding & General)'),
        ('glm', 'GLM (General & Multilingual)'),
        ('llama', 'Llama (General Purpose)'),
        ('other', 'Other')
    ], validators=[DataRequired()])
    worker_model = StringField('Worker Model (e.g. deepseek-r1:70b)', validators=[DataRequired()])
    queen_model = StringField('Queen Model (e.g. deepseek-r1:671b)', validators=[DataRequired()])
    specialty = SelectField('Specialty', choices=[
        ('general', '🧠 General Reasoning'),
        ('coding', '💻 Coding & Technical'),
        ('research', '🔬 Research & Analysis'),
        ('creative', '🎨 Creative & Content')
    ], validators=[DataRequired()])
    price_per_job = FloatField('Price per Job ($)', validators=[DataRequired(), NumberRange(min=0.01, max=100.0)], default=0.50)
    max_workers = IntegerField('Maximum Workers', validators=[DataRequired(), NumberRange(min=2, max=100)], default=20)
    submit = SubmitField('Create Hive')


class SubmitJobForm(FlaskForm):
    nectar = TextAreaField('Your Task (Nectar)', validators=[DataRequired(), Length(min=20, max=10000)],
                           render_kw={"rows": 8, "placeholder": "Describe the AI task you want the Hive to process..."})
    submit = SubmitField('🍯 Submit Task to Hive')


class SubmitMultimediaForm(FlaskForm):
    """Upload a JPEG/MP3/MP4 and ask the Hive to analyze it.
    The file is stored on the BeehiveOfAI server; Worker Bees fetch it over HTTP
    from /uploads/<filename> and run the recursive sub-sampling pipeline locally.
    """
    media_type = SelectField('Media Type', choices=[
        ('photo', '🖼️ Photo (JPEG)'),
        ('sound', '🎙️ Sound (MP3)'),
        ('video', '🎬 Video (MP4)'),
    ], validators=[DataRequired()])
    media_file = FileField('File (JPEG / MP3 / MP4)', validators=[
        FileRequired(),
        FileAllowed(['jpg', 'jpeg', 'mp3', 'mp4'], 'JPEG, MP3, or MP4 only'),
    ])
    submit = SubmitField('🍯 Submit Multimedia Task')


class UpdatePhoneForm(FlaskForm):
    phone = StringField('Phone Number (e.g. +972544752626)',
                        validators=[DataRequired(), Length(min=10, max=20)])
    submit = SubmitField('Save & Send Verification Code')


class VerifyPhoneForm(FlaskForm):
    digit1 = StringField('', validators=[DataRequired(), Length(min=1, max=1)])
    digit2 = StringField('', validators=[DataRequired(), Length(min=1, max=1)])
    digit3 = StringField('', validators=[DataRequired(), Length(min=1, max=1)])
    digit4 = StringField('', validators=[DataRequired(), Length(min=1, max=1)])
    digit5 = StringField('', validators=[DataRequired(), Length(min=1, max=1)])
    digit6 = StringField('', validators=[DataRequired(), Length(min=1, max=1)])
    submit = SubmitField('Verify')


class RatingForm(FlaskForm):
    score = SelectField('Rating', choices=[
        ('5', '⭐⭐⭐⭐⭐ Excellent'),
        ('4', '⭐⭐⭐⭐ Good'),
        ('3', '⭐⭐⭐ Average'),
        ('2', '⭐⭐ Poor'),
        ('1', '⭐ Terrible')
    ], validators=[DataRequired()])
    comment = TextAreaField('Comment (optional)', validators=[Optional(), Length(max=500)])
    submit = SubmitField('Submit Rating')
