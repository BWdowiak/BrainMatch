from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

db = SQLAlchemy()
login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.login_message_category = 'info'
login_manager.login_message = 'Zaloguj się, aby uzyskać dostęp do tej strony.'

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'sekretny_klucz_do_sesji_12345'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)
    login_manager.init_app(app)

    from app.main import main
    from app.auth import auth
    from app.errors import errors

    app.register_blueprint(main)
    app.register_blueprint(auth)
    app.register_blueprint(errors)

    return app