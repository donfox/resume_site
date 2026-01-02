from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_mail import Mail

db = SQLAlchemy()
migrate = Migrate()  # this object registers the `flask db` CLI when init_app is called
mail = Mail()
