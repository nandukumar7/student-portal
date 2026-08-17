import os

from databases.db import db
from flask import Blueprint, jsonify, request
from flask_bcrypt import Bcrypt
from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required
from models.user import User
from utils.decoraters import role_required

auth_bp = Blueprint("auth", __name__)

bcrypt = Bcrypt()


# =========================================================
# GET ALL USERS
# Admin only
# =========================================================

@auth_bp.route("/users", methods=["GET"])
@jwt_required()
@role_required("admin")
def get_users():

    users = User.query.all()

    return jsonify([
        user.to_dict()
        for user in users
    ]), 200


# =========================================================
# LOGIN
# =========================================================

@auth_bp.route("/login", methods=["POST"])
def login():

    data = request.get_json()

    # Check JSON
    if not data:
        return jsonify({
            "error": "Request body must contain JSON data"
        }), 400

    # Get values
    email = data.get("email")
    password = data.get("password")

    # Required fields
    if not email or not password:
        return jsonify({
            "error": "Email and password are required"
        }), 400

    # Validate email
    if not isinstance(email, str):
        return jsonify({
            "error": "Email must be a string"
        }), 400

    email = email.strip().lower()

    # Validate password
    if not isinstance(password, str):
        return jsonify({
            "error": "Password must be a string"
        }), 400

    # Find user
    user = User.query.filter_by(
        email=email
    ).first()

    # Check user
    if not user:
        return jsonify({
            "error": "Invalid email or password"
        }), 401

    # Check password
    if not bcrypt.check_password_hash(
        user.password,
        password
    ):
        return jsonify({
            "error": "Invalid email or password"
        }), 401

    # Create JWT
    access_token = create_access_token(
        identity=str(user.id)
    )

    # Response
    return jsonify({
        "message": "Login successful",
        "access_token": access_token,
        "user": user.to_dict()
    }), 200


# =========================================================
# REGISTER
# =========================================================

@auth_bp.route("/register", methods=["POST"])
def register():

    data = request.get_json()

    # Check JSON
    if not data:
        return jsonify({
            "error": "Request body must contain JSON data"
        }), 400

    # Get values
    username = data.get("username")
    email = data.get("email")
    password = data.get("password")

    # Required fields
    if not username or not email or not password:
        return jsonify({
            "error": "Username, email and password are required"
        }), 400

    # Validate username
    if not isinstance(username, str):
        return jsonify({
            "error": "Username must be a string"
        }), 400

    username = username.strip()

    if not username:
        return jsonify({
            "error": "Username cannot be empty"
        }), 400

    # Validate email
    if not isinstance(email, str):
        return jsonify({
            "error": "Email must be a string"
        }), 400

    email = email.strip().lower()

    if "@" not in email or "." not in email:
        return jsonify({
            "error": "Invalid email address"
        }), 400

    # Validate password
    if not isinstance(password, str):
        return jsonify({
            "error": "Password must be a string"
        }), 400

    if len(password) < 6:
        return jsonify({
            "error": "Password must be at least 6 characters"
        }), 400

    # Check existing email
    existing_user = User.query.filter_by(
        email=email
    ).first()

    if existing_user:
        return jsonify({
            "error": "Email already exists"
        }), 409

    # Check existing username
    existing_username = User.query.filter_by(
        username=username
    ).first()

    if existing_username:
        return jsonify({
            "error": "Username already exists"
        }), 409

    # Hash password
    hashed_password = bcrypt.generate_password_hash(
        password
    ).decode("utf-8")

    # Create user
    user = User(
        username=username,
        email=email,
        password=hashed_password
    )

    # Save
    db.session.add(user)
    db.session.commit()

    # Response
    return jsonify({
        "message": "User registered successfully",
        "user": user.to_dict()
    }), 201


# =========================================================
# PROFILE
# =========================================================

@auth_bp.route("/profile", methods=["GET"])
@jwt_required()
def profile():

    user_id = int(get_jwt_identity())

    user = db.session.get(
        User,
        user_id
    )

    if not user:
        return jsonify({
            "error": "User not found"
        }), 404

    return jsonify(
        user.to_dict()
    ), 200


# =========================================================
# TEMPORARY ADMIN SETUP
#
# Use this ONCE to create/promote the first admin.
# After creating the admin, DELETE this endpoint.
# =========================================================

@auth_bp.route("/setup-admin", methods=["POST"])
def setup_admin():

    # Get setup key
    setup_key = request.headers.get(
        "X-Setup-Key"
    )

    # Validate setup key
    if not setup_key or setup_key != os.getenv(
        "SETUP_ADMIN_KEY"
    ):
        return jsonify({
            "error": "Unauthorized"
        }), 401

    # Get JSON
    data = request.get_json()

    if not data:
        return jsonify({
            "error": "Request body is required"
        }), 400

    # Get values
    username = data.get("username")
    email = data.get("email")
    password = data.get("password")

    # Required fields
    if not username or not email or not password:
        return jsonify({
            "error": "Username, email and password are required"
        }), 400

    # Validate username
    if not isinstance(username, str):
        return jsonify({
            "error": "Username must be a string"
        }), 400

    username = username.strip()

    if not username:
        return jsonify({
            "error": "Username cannot be empty"
        }), 400

    # Validate email
    if not isinstance(email, str):
        return jsonify({
            "error": "Email must be a string"
        }), 400

    email = email.strip().lower()

    if "@" not in email or "." not in email:
        return jsonify({
            "error": "Invalid email address"
        }), 400

    # Validate password
    if not isinstance(password, str):
        return jsonify({
            "error": "Password must be a string"
        }), 400

    if len(password) < 6:
        return jsonify({
            "error": "Password must be at least 6 characters"
        }), 400

    # Check existing email
    user = User.query.filter_by(
        email=email
    ).first()

    # If user already exists,
    # promote that user to admin
    if user:

        user.role = "admin"

        db.session.commit()

        return jsonify({
            "message": "Existing user promoted to admin",
            "user": user.to_dict()
        }), 200

    # Check username
    existing_username = User.query.filter_by(
        username=username
    ).first()

    if existing_username:
        return jsonify({
            "error": "Username already exists"
        }), 409

    # Hash password
    hashed_password = bcrypt.generate_password_hash(
        password
    ).decode("utf-8")

    # Create admin
    admin = User(
        username=username,
        email=email,
        password=hashed_password,
        role="admin"
    )

    # Save
    db.session.add(admin)
    db.session.commit()

    # Response
    return jsonify({
        "message": "Admin created successfully",
        "user": admin.to_dict()
    }), 201