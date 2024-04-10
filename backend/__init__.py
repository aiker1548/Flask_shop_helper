from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
import os
from datetime import timedelta
from sqlalchemy import MetaData

convention = {
    "ix": 'ix_%(column_0_label)s',
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s"
}

metadata = MetaData(naming_convention=convention)
db = SQLAlchemy(metadata=metadata)

def create_app(config=None):
    # Создаем экземпляр Flask приложения
    app = Flask(__name__)
    #Настраиваем jwt
    jwt = JWTManager(app)
    app.config['JWT_SECRET_KEY'] = os.environ.get('JWT_SECRET_KEY', 'my_default_secret_key')
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=1)
    # Подключаем конфигурацию вашего приложения (например, из файла config.py)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    # Инициализируем расширения приложения
    db.init_app(app)
    # Регистрируем блюпринты (подприложения) вашего приложения
    from backend.users.apiViews import api as api_user
    from backend.recipes.views import api as api_recipes
    app.register_blueprint(api_user)
    app.register_blueprint(api_recipes)
    

    with app.app_context():
        db.create_all()
        migrate = Migrate(app, db, render_as_batch=True)
    return app