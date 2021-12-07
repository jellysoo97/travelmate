from models import UserData
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, IntegerField, TextAreaField, SelectField, BooleanField
from wtforms.validators import DataRequired, EqualTo
from flask import Flask, request, render_template, redirect, session


class SignUp(FlaskForm):
    userId = StringField('userId', validators=[DataRequired(message='필숫값입니다.')])
    userPw = PasswordField('userPw', validators=[DataRequired(message='필숫값입니다.')])
    repassword = PasswordField('repassword', validators=[DataRequired(message='비밀번호를 재입력하세요'), EqualTo('userPw')])
    userMajor = StringField('useMajor', validators=[DataRequired(message='필숫값입니다.')])
    userLang = StringField('userLang', validators=[DataRequired(message='필숫값입니다.')])


class Login(FlaskForm):
    userId = StringField('userId', validators=[DataRequired()])
    userPw = PasswordField('userPw', validators=[DataRequired()])

class Condition(FlaskForm):
    travelDes = SelectField('travelDes', validators=[DataRequired()])
    travelNum = SelectField('travelNum', validators=[DataRequired()], choices=[])
    travelLang = SelectField('travelLang', validators=[DataRequired()])

class CreateTeam(FlaskForm):
    userNum = IntegerField('userNum', validators=[DataRequired()])
    teamName = StringField('teamNum', validators=[DataRequired()])
    teamIntro = TextAreaField('teamIntro', validators=[DataRequired()])
    teamTo = SelectField('teamTo', validators=[DataRequired()])
    teamNumGoal = SelectField('teamNumGoal', validators=[DataRequired()], choices=[])
    teamAddress = StringField('teamAddress', validators=[DataRequired()])

class AddTeam(FlaskForm):
    userNum = BooleanField('userNum', validators=[DataRequired()])
    teamCode = BooleanField('teamCode', validators=[DataRequired()])

class Satisfy(FlaskForm):
    input_sat = SelectField('userSat', validators=[DataRequired()], choices=[])

