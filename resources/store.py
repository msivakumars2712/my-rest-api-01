from flask.views import MethodView
from schemas import StoreSchema
from models import StoreModel
from db import db
from flask_smorest import Blueprint, abort
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from flask_jwt_extended import jwt_required, get_jwt

blp = Blueprint("Store", "store", description="Operation related to store")


@blp.route("/store")
class CreateStore(MethodView):
    @jwt_required()
    @blp.arguments(StoreSchema)
    @blp.response(201, StoreSchema)
    def post(self, store_data):
        store = StoreModel(**store_data)
        try:
            db.session.add(store)
            db.session.commit()
            return store
        except IntegrityError:
            abort(400, message="Store with that name already exist")
        except SQLAlchemyError as e:
            abort(500, message=str(e))


@blp.route("/store/<string:store_id>")
class UserById(MethodView):
    @jwt_required()
    @blp.response(200, StoreSchema)
    def get(self, store_id):
        store = StoreModel.query.get_or_404(store_id)
        return store

    @jwt_required()
    def delete(self, store_id):
        jwt = get_jwt()
        if not jwt.get("is_admin"):
            abort(400, message="Admin privilege required")

        store = StoreModel.query.get_or_404(store_id)
        try:
            db.session.delete(store)
            db.session.commit()
            return {"message": "store deleted"}
        except SQLAlchemyError as e:
            abort(500, message=str(e))


@blp.route("/stores")
class StoreList(MethodView):
    @jwt_required()
    @blp.response(200, StoreSchema(many=True))
    def get(self):
        stores = StoreModel.query.all()
        return stores
