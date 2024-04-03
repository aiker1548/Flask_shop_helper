from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate


db = SQLAlchemy()

def create_app(config=None):
    # Создаем экземпляр Flask приложения
    app = Flask(__name__)

    # Подключаем конфигурацию вашего приложения (например, из файла config.py)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    # Инициализируем расширения приложения
    db.init_app(app)
    # Регистрируем блюпринты (подприложения) вашего приложения
    from backend.users.apiViews import api
    app.register_blueprint(api)

    with app.app_context():
        db.create_all()
        migrate = Migrate(app, db)
    return app