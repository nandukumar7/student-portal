from databases.db import db
from flask import Blueprint, jsonify, request
from models.student import Student
from sqlalchemy.exc import SQLAlchemyError
from utils.decoraters import role_required

students_bp = Blueprint("students", __name__)


# ==========================================
# GET ALL STUDENTS
# ==========================================

@students_bp.route("/students", methods=["GET"])
def get_students():

    students = Student.query.all()

    return jsonify([
        student.to_dict()
        for student in students
    ])


# ==========================================
# GET STUDENT BY ID
# ==========================================

@students_bp.route("/students/<int:student_id>", methods=["GET"])
def get_student(student_id):

    student = db.session.get(
        Student,
        student_id
    )

    if student:
        return jsonify(
            student.to_dict()
        )

    return jsonify({
        "error": "Student not found"
    }), 404


# ==========================================
# CREATE STUDENT
# ==========================================

@students_bp.route("/students", methods=["POST"])
@role_required("teacher", "admin")
def add_student():

    data = request.get_json()

    # Check JSON
    if not data:
        return jsonify({
            "error": "Request body must contain JSON data"
        }), 400

    # Get values
    name = data.get("name")
    age = data.get("age")

    # Required fields
    if name is None or age is None:
        return jsonify({
            "error": "Name and age are required"
        }), 400

    # Validate name
    if not isinstance(name, str):
        return jsonify({
            "error": "Name must be a string"
        }), 400

    name = name.strip()

    if not name:
        return jsonify({
            "error": "Name cannot be empty"
        }), 400

    # Validate age
    if not isinstance(age, int):
        return jsonify({
            "error": "Age must be an integer"
        }), 400

    if age <= 0:
        return jsonify({
            "error": "Age must be greater than 0"
        }), 400

    # Create student
    student = Student(
        name=name,
        age=age
    )

    # Database transaction
    try:

        db.session.add(student)

        db.session.commit()

    except SQLAlchemyError:

        db.session.rollback()

        return jsonify({
            "error": "Failed to create student"
        }), 500

    return jsonify({
        "message": "Student created successfully",
        "student": student.to_dict()
    }), 201


# ==========================================
# UPDATE STUDENT
# ==========================================

@students_bp.route(
    "/students/<int:student_id>",
    methods=["PUT"]
)
@role_required("teacher", "admin")
def update_student(student_id):

    # Find student
    student = db.session.get(
        Student,
        student_id
    )

    if not student:
        return jsonify({
            "error": "Student not found"
        }), 404

    # Get JSON
    data = request.get_json()

    if not data:
        return jsonify({
            "error": "Request body must contain JSON data"
        }), 400

    # Get values
    name = data.get("name")
    age = data.get("age")

    # Validate name if provided
    if name is not None:

        if not isinstance(name, str):
            return jsonify({
                "error": "Name must be a string"
            }), 400

        name = name.strip()

        if not name:
            return jsonify({
                "error": "Name cannot be empty"
            }), 400

        student.name = name

    # Validate age if provided
    if age is not None:

        if not isinstance(age, int):
            return jsonify({
                "error": "Age must be an integer"
            }), 400

        if age <= 0:
            return jsonify({
                "error": "Age must be greater than 0"
            }), 400

        student.age = age

    # At least one field required
    if name is None and age is None:
        return jsonify({
            "error": "At least name or age must be provided"
        }), 400

    # Database transaction
    try:

        db.session.commit()

    except SQLAlchemyError:

        db.session.rollback()

        return jsonify({
            "error": "Failed to update student"
        }), 500

    return jsonify({
        "message": "Student updated successfully",
        "student": student.to_dict()
    }), 200


# ==========================================
# DELETE STUDENT
# ==========================================

@students_bp.route(
    "/students/<int:student_id>",
    methods=["DELETE"]
)
@role_required("admin")
def delete_student(student_id):

    student = db.session.get(
        Student,
        student_id
    )

    if not student:
        return jsonify({
            "error": "Student not found"
        }), 404

    # Database transaction
    try:

        db.session.delete(student)

        db.session.commit()

    except SQLAlchemyError:

        db.session.rollback()

        return jsonify({
            "error": "Failed to delete student"
        }), 500

    return jsonify({
        "message": "Student deleted successfully"
    }), 200