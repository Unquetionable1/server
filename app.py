from flask import Flask, jsonify, request, session
from flask_restful import Resource, Api
from flask_bcrypt import Bcrypt
from flask_migrate import Migrate
from config import Config
from models import db, User, Item
from flask_cors import CORS
# App configuration
app = Flask(__name__)
app.config.from_object(Config)
CORS(app)
# Database configuration
db.init_app(app)
migrate = Migrate(app, db)

# API configuration
api = Api(app)

# Bcrypt configuration
bcrypt = Bcrypt(app)


# Home route
@app.route('/')
def index():
    return "My API is running"


# Resource for user registration and listing
class UserResource(Resource):
    def get(self):
        data = User.query.all()
        users = [{"name": user.name} for user in data]
        return jsonify(users)

    def post(self):
        data = request.get_json()
        name = data.get("name")
        password = data.get("password")

        if not name or not password:
            return {"message": "Name and password are required"}, 400

        if User.query.filter_by(name=name).first():
            return {"message": "User already exists"}, 400

        hashed_password = bcrypt.generate_password_hash(password).decode("utf-8")
        user = User(name=name, password=hashed_password)
        db.session.add(user)
        db.session.commit()

        return {"message": f"User {name} created successfully"}, 201

    def delete(self):
        data = request.get_json()
        name = data.get("name")

        user = User.query.filter_by(name=name).first()
        if not user:
            return {"message": "User not found"}, 404

        db.session.delete(user)
        db.session.commit()
        return {"message": f"User {name} deleted successfully"}, 200


# Resource for user login and logout
class AuthResource(Resource):
    def post(self):
        data = request.get_json()
        name = data.get('name')
        password = data.get('password')

        if not name or not password:
            return {"message": "Name and password are required"}, 400

        user = User.query.filter_by(name=name).first()
        if not user:
            return {"message": "User does not exist. Please register first."}, 404

        if bcrypt.check_password_hash(user.password, password):
            session["user_id"] = user.id
            return {"message": "User logged in successfully."}, 200
        else:
            return {"message": "Invalid password"}, 401

    def delete(self):
        if 'user_id' in session:
            session.pop('user_id', None)
            return {"message": 'Logged out'}, 200
        else:
            return {"message": 'No active session'}, 401

    def get(self):
        if 'user_id' in session:
            return {"message": "User is authenticated"}, 200
        else:
            return {"message": "No active session"}, 401


# Resource for managing items
class ItemsResource(Resource):
    def get(self):
        data = Item.query.all()
        items = [{"id": item.id, "name": item.name} for item in data]
        return jsonify(items)

    def post(self):
        if 'user_id' not in session:
            return {"message": "Authentication required"}, 401

        data = request.get_json()
        name = data.get("name")

        if not name:
            return {"message": "Name is required"}, 400

        item = Item(name=name)
        db.session.add(item)
        db.session.commit()
        return jsonify({"id": item.id, "name": item.name}), 201


# test
# Adding resources to the API
api.add_resource(UserResource, "/register")
api.add_resource(AuthResource, "/auth")
api.add_resource(ItemsResource, "/items")

if __name__ == "__main__":
    app.run(debug=True)
