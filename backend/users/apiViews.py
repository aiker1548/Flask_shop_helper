from flask import Blueprint, jsonify, request
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from werkzeug.security import generate_password_hash, check_password_hash
from .models import db, User, Subscriber
from flask_restful import Resource

api = Blueprint('api', __name__, url_prefix='/api')

class Users(Resource):
    def get(self):
        users = User.query.all()
        return jsonify([user.serialize() for user in users]), 200

    def post(self):
        data = request.json
        hashed_password = generate_password_hash(data['password'])
        new_user = User(username=data['username'], email=data['email'], password=hashed_password, last_name=data['last_name'], first_name=data['first_name'])
        db.session.add(new_user)
        db.session.commit()
        return jsonify({'message': 'User created successfully'}), 201

class UserProfile(Resource):
    def get(self, user_id):
        user = User.query.get(user_id)
        if user:
            return jsonify(user.serialize()), 200
        else:
            return jsonify({'message': 'User not found'}), 404

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
    

@api.route('/login', methods=['POST'])
def login():
    data = request.json
    user = User.query.filter_by(username=data['username']).first()
    if not user or not check_password_hash(user.password, data['password']):
        return jsonify({'message': 'Invalid username or password'}), 401
    access_token = create_access_token(identity=user.id)
    return jsonify(access_token=access_token), 200


@api.route('/auth', methods=['GET'])
@jwt_required()
def authenticate():
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    return jsonify(user.serialize()), 200

@api.route('/users/me', methods=['GET'])
@jwt_required()
def my_profile():
    current_user_id = get_jwt_identity()
    try:
        user = User.query.get(current_user_id)
        return jsonify(user.serialize()), 200
    except:
        return jsonify({'message': 'User is not authorized'}), 401



api.add_url_rule('/users', view_func=Users.as_view('users'))
api.add_url_rule('/users/<int:user_id>', view_func=UserProfile.as_view('user_profile'))
api.add_url_rule('/users/subscriptions', view_func=UserSubscriptions.as_view('subscriptions'))
# Добавление поддержки подписки на пользователя
api.add_url_rule('/users/<int:user_id>/subscribe', view_func=Subscribe.as_view('subscribe_user'))
