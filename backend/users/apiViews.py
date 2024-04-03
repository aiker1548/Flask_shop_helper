from flask import Blueprint, jsonify, request
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from werkzeug.security import generate_password_hash, check_password_hash
from .models import db, User, Subscriber


api = Blueprint('api', __name__)

@api.route('/users', methods=['GET'])
def get_users():
    users = User.query.all()
    return jsonify([user.serialize() for user in users]), 200

@api.route('/users', methods=['POST'])
def create_user():
    data = request.json
    print(data)
    hashed_password = generate_password_hash(data['password'])
    new_user = User(username=data['username'], email=data['email'], password=hashed_password, last_name=data['last_name'], first_name=data['first_name'])
    db.session.add(new_user)
    db.session.commit()
    return jsonify({'message': 'User created successfully'}), 201

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

@api.route('/subscribe', methods=['POST'])
@jwt_required()
def subscribe():
    current_user_id = get_jwt_identity()
    data = request.json
    user_to_subscribe_id = data.get('user_id')

    user_to_subscribe = User.query.get(user_to_subscribe_id)
    if user_to_subscribe is None:
        return jsonify({'message': 'User not found'}), 404

    # Проверка, существует ли уже подписка
    existing_subscription = Subscriber.query.filter_by(subscriber_id=current_user_id, subscribed_to_id=user_to_subscribe_id).first()
    if existing_subscription:
        return jsonify({'message': 'Subscription already exists'}), 400

    if int(current_user_id) == int(user_to_subscribe_id):
        return jsonify({'message': 'User cannot subscribe to themselves'}), 400
    
    new_subscription = Subscriber(subscriber_id=current_user_id, subscribed_to_id=user_to_subscribe_id)
    db.session.add(new_subscription)
    db.session.commit()

    return jsonify({'message': 'Subscription created successfully'}), 201

@api.route('/subscriptions', methods=['GET'])
@jwt_required()
def get_subscriptions():
    current_user_id = get_jwt_identity()

    subscriptions = Subscriber.query.filter_by(user_id=current_user_id).all()
    subscribed_users = [User.query.get(subscription.subscribed_to) for subscription in subscriptions]

    return jsonify({'subscribed_users': [user.serialize() for user in subscribed_users]}), 200