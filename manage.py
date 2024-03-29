from backend import create_app
from backend.config import Config

# Создание Flask-приложения с использованием конфигурации
app = create_app(config=Config)

# Запуск приложения
if __name__ == '__main__':
    app.run()