from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_babel import Babel, _
from flask_sqlalchemy import SQLAlchemy

from .config import Config


def get_locale():
    lang = request.cookies.get('lang', 'en')  # Используем язык из куки или "en" по умолчанию
    return lang


app = Flask(__name__)
app.config.from_object(Config)

db = SQLAlchemy(app)
babel = Babel(app, locale_selector=lambda: get_locale())