from flask import Flask
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

from settings import Config

app = Flask(__name__, static_folder='static')
app.config.from_object(Config)
app.json.ensure_ascii = False
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# Новый импорт — api_views.
from . import api_views, error_handlers, views
