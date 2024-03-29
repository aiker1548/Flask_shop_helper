from flask import Flask
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

def create_app(config=None):
    # Создаем экземпляр Flask приложения
    app = Flask(__name__)

    # Подключаем конфигурацию вашего приложения (например, из файла config.py)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///your_database.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Инициализируем расширения приложения
    db.init_app(app)

    # Регистрируем блюпринты (подприложения) вашего приложения
    from backend.users.apiViews import api
    app.register_blueprint(api)

    with app.app_context():
        print('ok2')
        db.create_all()

    return app