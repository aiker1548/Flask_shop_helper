from flask import Blueprint, jsonify, request, url_for
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity, unset_jwt_cookies
from werkzeug.security import generate_password_hash, check_password_hash
from .models import db, User, Subscriber
from flask_restful import Resource

api = Blueprint('api', __name__, url_prefix='/api')

class Users(Resource):
    def get(self):
        # Получаем параметры page и limit из запроса
        page = request.args.get('page', default=1, type=int)
        limit = request.args.get('limit', default=10, type=int)

        # Вычисляем смещение для запроса
        offset = (page - 1) * limit

        # Получаем список пользователей для текущей страницы
        users = User.query.offset(offset).limit(limit).all()

        # Формируем список результатов для текущей страницы
        results = [user.serialize() for user in users]

        # Получаем общее количество объектов в базе
        total_users_count = User.query.count()

        # Вычисляем ссылку на следующую страницу, если она есть
        next_page = None
        if offset + limit < total_users_count:
            next_page = url_for('api.users', page=page+1, limit=limit, _external=True)

        # Вычисляем ссылку на предыдущую страницу, если она есть
        previous_page = None
        if page > 1:
            previous_page = url_for('api.users', page=page-1, limit=limit, _external=True)

        # Формируем ответ в соответствии с заданным форматом
        response = {
            'count': total_users_count,
            'next': next_page,
            'previous': previous_page,
            'results': results
        }

        return jsonify(response), 200

    def post(self):
        try:
            data = request.json
            hashed_password = generate_password_hash(data['password'])
            new_user = User(username=data['username'], email=data['email'], password=hashed_password, last_name=data['last_name'], first_name=data['first_name'])
            db.session.add(new_user)
            db.session.commit()
            return jsonify(new_user.serialize()), 201
        except Exception as e:
            return jsonify({'message': f'{e}'}), 400

class UserProfile(Resource):
    def get(self, user_id):
        user = User.query.get(user_id)
        if user:
            return jsonify(user.serialize()), 200
        else:
            return jsonify({'message': 'User not found'}), 404

@api.route('/users/me', methods=['GET'])
@jwt_required()
def my_profile():
    current_user_id = get_jwt_identity()
    try:
        user = User.query.get(current_user_id)
        return jsonify(user.serialize()), 200
    except:
        return jsonify({'message': 'User is not authorized'}), 401


class UserSubscriptions(Resource):
    @jwt_required()
    def get(self):
        current_user_id = get_jwt_identity()
        subscriptions = Subscriber.query.filter_by(subscriber_id=current_user_id).all()
        subscribed_users = []
        for subscribe in subscriptions:
            subscribed_users.append(subscribe.subscribed_to.serialize())
        return jsonify({'subscribed_users': subscribed_users}), 200

class Subscribe(Resource):
    @jwt_required()
    def post(self, user_id):
        current_user_id = get_jwt_identity()
        if int(current_user_id) == int(user_id):
            return jsonify({'message': 'User cannot subscribe to themselves'}), 400
        
        user_to_subscribe = User.query.get(user_id)
        if user_to_subscribe is None:
            return jsonify({'message': 'User not found'}), 404

        existing_subscription = Subscriber.query.filter_by(subscriber_id=current_user_id, subscribed_to_id=user_id).first()
        if existing_subscription:
            return jsonify({'message': 'Subscription already exists'}), 400

        new_subscription = Subscriber(subscriber_id=current_user_id, subscribed_to_id=user_id)
        db.session.add(new_subscription)
        db.session.commit()

        return jsonify({'message': 'Subscription created successfully'}), 201


@api.route('/auth/token/login/', methods=['POST'])
def login():
    data = request.json
    if 'username' in data:
        user = User.query.filter_by(username=data['username']).first()
    elif  'email' in data:
        user = User.query.filter_by(email=data['email']).first()
    else:
        user = None
    if user is None or not check_password_hash(user.password, data['password']):
        return jsonify({'message': 'Invalid username or password'}), 400
    access_token = create_access_token(identity=user.id)
    return jsonify({"auth_token": access_token}), 200

@api.route('/auth/token/logout', methods=['POST'])
@jwt_required()
def logout():
    # Получаем идентификатор текущего пользователя из токена
    current_user_id = get_jwt_identity()

    # Очищаем куки с JWT токеном
    response = jsonify({'message': 'Logout successful'})
    unset_jwt_cookies(response)

    return response, 200

@api.route('/auth', methods=['GET'])
@jwt_required()
def authenticate():
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    return jsonify(user.serialize()), 200




api.add_url_rule('/users/', view_func=Users.as_view('users'))
api.add_url_rule('/users/<int:user_id>/', view_func=UserProfile.as_view('user_profile'))
api.add_url_rule('/users/subscriptions/', view_func=UserSubscriptions.as_view('subscriptions'))
# Добавление поддержки подписки на пользователя
api.add_url_rule('/users/<int:user_id>/subscribe/', view_func=Subscribe.as_view('subscribe_user'))
