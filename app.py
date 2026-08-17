import os
from datetime import timedelta

from config import Config
from databases.db import db
from dotenv import load_dotenv
from flask import Flask, jsonify
from flask_bcrypt import Bcrypt
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate
from routes.auth_routes import auth_bp
from routes.students_routes import students_bp
from utils.errors import register_error_handlers

load_dotenv()

app = Flask(__name__)

app.config.from_object(Config)

# JWT secret from .env
app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY")
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(hours=1)
register_error_handlers(app)

print(app.config.get("SQLALCHEMY_DATABASE_URI"))


# =========================
# INITIALIZE EXTENSIONS
# =========================

db.init_app(app)

migrate = Migrate(app, db)

bcrypt = Bcrypt(app)

jwt = JWTManager(app)
# ==========================================
# JWT ERROR HANDLERS
# ==========================================

@jwt.unauthorized_loader
def handle_missing_token(error):

    return jsonify({
        "success": False,
        "error": "Authentication token is required"
    }), 401


@jwt.invalid_token_loader
def handle_invalid_token(error):

    return jsonify({
        "success": False,
        "error": "Invalid authentication token"
    }), 401


@jwt.expired_token_loader
def handle_expired_token(jwt_header, jwt_payload):

    return jsonify({
        "success": False,
        "error": "Authentication token has expired"
    }), 401

CORS(
    app,
    resources={
        r"/*": {
            "origins": [
                "http://localhost:5173"
            ]
        }
    },
    supports_credentials=False
)


# =========================
# REGISTER BLUEPRINTS
# =========================

app.register_blueprint(students_bp)

app.register_blueprint(auth_bp)


# =========================
# HOME
# =========================

@app.route("/")
def home():
    return "Welcome to the Student API!"


# =========================
# RUN APPLICATION
# =========================

if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=int(os.getenv("PORT", 5000)),
        debug=os.getenv("FLASK_DEBUG", "0") == "1"
    )