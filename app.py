from flask import Flask, jsonify
from flask_smorest import Api
from resources.user import blp as user_blue_print
from resources.store import blp as store_blue_print
from db import db
from flask_jwt_extended import JWTManager
import os
from blocklist import BLOCKLIST
from flask_migrate import Migrate


def create_app(db_url=None):
    app = Flask(__name__)
    app.config["PROPAGATE_EXCEPTIONS"] = True
    app.config["API_TITLE"] = "First JWT App"
    app.config["API_VERSION"] = "v1"
    app.config["OPENAPI_VERSION"] = "3.0.3"
    app.config["OPENAPI_URL_PREFIX"] = "/"
    app.config["OPENAPI_SWAGGER_UI_PATH"] = "/swagger-ui"
    app.config["OPENAPI_SWAGGER_UI_URL"] = "https://cdn.jsdelivr.net/npm/swagger-ui-dist/"
    app.config["SQLALCHEMY_DATABASE_URI"] = db_url or os.getenv("DATABASE_URL", "sqlite:///data.db")
    app.config["SQLALCHEMY_TRACK_NOTIFICATIONS"] = True
    app.config["JWT_SECRET_KEY"] = "231913007243482132803017552228286401989"
    db.init_app(app)
    migrate = Migrate(app, db)
    jwt = JWTManager(app)

    @jwt.token_in_blocklist_loader
    def check_if_token_in_blocked_list(jwt_header,jwt_payload):
        return jwt_payload["jti"] in BLOCKLIST

    @jwt.revoked_token_loader
    def revoked_token_callback(jwt_header,jwt_payload):
        return (
            jsonify(
                {"message": "Token has been revoked", "error": "Revoked Token"}
            ), 401
        )

    @jwt.additional_claims_loader
    def add_additional_claims_to_jwt(identity):
        if identity == 1:
            return {"is_admin": True}
        return {"is_admin": False}

    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        return (
            jsonify(
                {"message": "Token has expired", "error": "Token expired"}
            ), 401
        )

    @jwt.invalid_token_loader
    def invalid_token_callback(error):
        return (
            jsonify(
                {"message": "Signature verification failed", "error": " Invalid Token"}
            ), 401
        )

    @jwt.unauthorized_loader
    def missing_token_callback(error):
        return (
            jsonify(
                {"message": "Request does not contain an access token", "error": "Authorization required"}
            ), 401
        )
    # with app.app_context():
    #     db.create_all()

    api = Api(app)
    api.register_blueprint(blp=user_blue_print)
    api.register_blueprint(blp=store_blue_print)
    return app
