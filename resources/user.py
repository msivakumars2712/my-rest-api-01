from db import db
from flask.views import MethodView
from models import UserModel
from flask_smorest import Blueprint, abort
from schemas import UserSchema
from passlib.hash import pbkdf2_sha256
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from flask_jwt_extended import create_access_token, get_jwt, jwt_required, create_refresh_token
from blocklist import BLOCKLIST
from flask import jsonify

blp = Blueprint("User", "user", "Operations related to User")


@blp.route("/register")
class UserRegistration(MethodView):
    @blp.arguments(UserSchema)
    @blp.response(201, UserSchema)
    def post(self, user_data):
        username = user_data["username"]
        password = pbkdf2_sha256.hash(user_data["password"])
        user = UserModel(username=username, password=password)

        try:
            db.session.add(user)
            db.session.commit()
            return user
        except IntegrityError:
            abort(400, message="User with that name already exist")
        except SQLAlchemyError as e:
            abort(500, message=str(e))


@blp.route("/login")
class LogIn(MethodView):
    @blp.arguments(UserSchema)
    def post(self, user_data):
        user = UserModel.query.filter(
            UserModel.username == user_data["username"]
        ).first()
        if user and pbkdf2_sha256.verify(user_data["password"], user.password):
            access_token = create_access_token(identity=user.id, fresh=True)
            refresh_token = create_refresh_token(identity=user.id)
            return jsonify(
                {
                    "jws_token": access_token,
                    "refresh_token": refresh_token
                }
            )
        abort(401, message="Invalid credentials")


@blp.route("/logout")
class LogOut(MethodView):
    @jwt_required()
    def post(self):
        jwt = get_jwt()
        jti = jwt.get("jti")
        BLOCKLIST.add(jti)
        return {"message": "Successfully logged out"}, 200


@blp.route("/user/<int:user_id>")
class UserById(MethodView):
    @blp.response(200, UserSchema)
    def get(self, user_id):
        user = UserModel.query.get_or_404(user_id)
        return user

    def delete(self, user_id):
        user = UserModel.query.get_or_404(user_id)
        try:
            db.session.delete(user)
            db.session.commit()
            return {"message" : "User deleted"}
        except SQLAlchemyError as e:
            abort(500, message=str(e))


@blp.route("/users")
class UserList(MethodView):
    @blp.response(200, UserSchema(many=True))
    def get(self):
        users = UserModel.query.all()
        return users