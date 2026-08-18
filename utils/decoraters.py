from functools import wraps

from databases.db import db
from flask import jsonify
from flask_jwt_extended import get_jwt_identity, jwt_required
from models.user import User


def role_required(allowed_roles):

    def decorator(fn):

        @wraps(fn)
        @jwt_required()
        def wrapper(*args, **kwargs):

            user_id = get_jwt_identity()

            user = db.session.get(User, int(user_id))

            if not user:
                return jsonify({
                    "error": "User not found"
                }), 404

            if user.role not in allowed_roles:
                return jsonify({
                    "error": "Access denied"
                }), 403

            return fn(*args, **kwargs)

        return wrapper

    return decorator