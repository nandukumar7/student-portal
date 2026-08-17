from databases.db import db
from models.user import User

# ==========================================
# HELPER: REGISTER + LOGIN
# ==========================================

def get_token(client, username, email, password):

    # Register user
    register_response = client.post(
        "/register",
        json={
            "username": username,
            "email": email,
            "password": password
        }
    )

    assert register_response.status_code == 201

    # Login user
    login_response = client.post(
        "/login",
        json={
            "email": email,
            "password": password
        }
    )

    assert login_response.status_code == 200

    return login_response.get_json()["access_token"]


# ==========================================
# HELPER: CHANGE USER ROLE
# ==========================================

def make_role(email, role):

    user = User.query.filter_by(
        email=email
    ).first()

    assert user is not None

    user.role = role

    db.session.commit()


# ==========================================
# STUDENT CANNOT DELETE
# ==========================================

def test_student_cannot_delete(client):

    # Create student user
    student_token = get_token(
        client,
        "student1",
        "student1@gmail.com",
        "123456"
    )

    # Create teacher user
    teacher_email = "teacher1@gmail.com"

    teacher_token = get_token(
        client,
        "teacher1",
        teacher_email,
        "123456"
    )

    # Change teacher role
    make_role(
        teacher_email,
        "teacher"
    )

    # Teacher creates a student
    create_response = client.post(
        "/students",
        json={
            "name": "Test Student",
            "age": 20
        },
        headers={
            "Authorization": f"Bearer {teacher_token}"
        }
    )

    # Make sure student creation worked
    assert create_response.status_code == 201

    data = create_response.get_json()

    student_id = data["student"]["id"]

    # Student attempts DELETE
    response = client.delete(
        f"/students/{student_id}",
        headers={
            "Authorization": f"Bearer {student_token}"
        }
    )

    # Student should NOT be allowed
    assert response.status_code == 403


# ==========================================
# TEACHER CANNOT DELETE
# ==========================================

def test_teacher_cannot_delete(client):

    teacher_email = "teacher2@gmail.com"

    # Create teacher user
    teacher_token = get_token(
        client,
        "teacher2",
        teacher_email,
        "123456"
    )

    # Change role from student -> teacher
    make_role(
        teacher_email,
        "teacher"
    )

    # Teacher creates a student
    create_response = client.post(
        "/students",
        json={
            "name": "Teacher Test Student",
            "age": 21
        },
        headers={
            "Authorization": f"Bearer {teacher_token}"
        }
    )

    assert create_response.status_code == 201

    data = create_response.get_json()

    student_id = data["student"]["id"]

    # Teacher attempts DELETE
    response = client.delete(
        f"/students/{student_id}",
        headers={
            "Authorization": f"Bearer {teacher_token}"
        }
    )

    # Teacher should NOT be allowed
    assert response.status_code == 403


# ==========================================
# ADMIN CAN DELETE
# ==========================================

def test_admin_can_delete(client):

    admin_email = "admin1@gmail.com"

    # Create admin user
    admin_token = get_token(
        client,
        "admin1",
        admin_email,
        "123456"
    )

    # Change role from student -> admin
    make_role(
        admin_email,
        "admin"
    )

    # Admin creates a student
    create_response = client.post(
        "/students",
        json={
            "name": "Admin Test Student",
            "age": 22
        },
        headers={
            "Authorization": f"Bearer {admin_token}"
        }
    )

    assert create_response.status_code == 201

    data = create_response.get_json()

    student_id = data["student"]["id"]

    # Admin deletes student
    response = client.delete(
        f"/students/{student_id}",
        headers={
            "Authorization": f"Bearer {admin_token}"
        }
    )

    # Admin should be allowed
    assert response.status_code == 200

    response_data = response.get_json()

    assert response_data["message"] == (
        "Student deleted successfully"
    )
def test_get_all_students(client):

    # Create teacher
    teacher_email = "getteacher@gmail.com"

    teacher_token = get_token(
        client,
        "getteacher",
        teacher_email,
        "123456"
    )

    make_role(
        teacher_email,
        "teacher"
    )

    # Create first student
    response1 = client.post(
        "/students",
        json={
            "name": "Alice",
            "age": 20
        },
        headers={
            "Authorization": f"Bearer {teacher_token}"
        }
    )

    assert response1.status_code == 201

    # Create second student
    response2 = client.post(
        "/students",
        json={
            "name": "Bob",
            "age": 22
        },
        headers={
            "Authorization": f"Bearer {teacher_token}"
        }
    )

    assert response2.status_code == 201

    # Get all students
    response = client.get("/students")

    assert response.status_code == 200

    data = response.get_json()

    assert len(data) == 2

    assert data[0]["name"] == "Alice"
    assert data[1]["name"] == "Bob"
def test_get_student_by_id(client):

    teacher_email = "singleteacher@gmail.com"

    teacher_token = get_token(
        client,
        "singleteacher",
        teacher_email,
        "123456"
    )

    make_role(
        teacher_email,
        "teacher"
    )

    # Create student
    create_response = client.post(
        "/students",
        json={
            "name": "Charlie",
            "age": 21
        },
        headers={
            "Authorization": f"Bearer {teacher_token}"
        }
    )

    assert create_response.status_code == 201

    student_id = (
        create_response
        .get_json()["student"]["id"]
    )

    # Get student
    response = client.get(
        f"/students/{student_id}"
    )

    assert response.status_code == 200

    data = response.get_json()

    assert data["id"] == student_id
    assert data["name"] == "Charlie"
    assert data["age"] == 21
def test_get_student_not_found(client):

    response = client.get("/students/9999")

    assert response.status_code == 404

    data = response.get_json()

    assert data["error"] == "Student not found"
def test_create_student(client):

    teacher_email = "postteacher@gmail.com"

    teacher_token = get_token(
        client,
        "postteacher",
        teacher_email,
        "123456"
    )

    make_role(
        teacher_email,
        "teacher"
    )

    response = client.post(
        "/students",
        json={
            "name": "David",
            "age": 24
        },
        headers={
            "Authorization": f"Bearer {teacher_token}"
        }
    )

    assert response.status_code == 201

    data = response.get_json()

    assert data["message"] == "Student created successfully"
    assert data["student"]["name"] == "David"
    assert data["student"]["age"] == 24
def test_create_student_missing_fields(client):

    teacher_email = "missingteacher@gmail.com"

    teacher_token = get_token(
        client,
        "missingteacher",
        teacher_email,
        "123456"
    )

    make_role(
        teacher_email,
        "teacher"
    )

    response = client.post(
        "/students",
        json={
            "name": "David"
        },
        headers={
            "Authorization": f"Bearer {teacher_token}"
        }
    )

    assert response.status_code == 400

    data = response.get_json()

    assert data["error"] == "Name and age are required"
def test_create_student_empty_name(client):

    teacher_email = "emptyteacher@gmail.com"

    teacher_token = get_token(
        client,
        "emptyteacher",
        teacher_email,
        "123456"
    )

    make_role(
        teacher_email,
        "teacher"
    )

    response = client.post(
        "/students",
        json={
            "name": "",
            "age": 20
        },
        headers={
            "Authorization": f"Bearer {teacher_token}"
        }
    )

    assert response.status_code == 400

    data = response.get_json()

    assert data["error"] == "Name cannot be empty"
def test_create_student_invalid_age(client):

    teacher_email = "ageteacher@gmail.com"

    teacher_token = get_token(
        client,
        "ageteacher",
        teacher_email,
        "123456"
    )

    make_role(
        teacher_email,
        "teacher"
    )

    response = client.post(
        "/students",
        json={
            "name": "David",
            "age": -5
        },
        headers={
            "Authorization": f"Bearer {teacher_token}"
        }
    )

    assert response.status_code == 400

    data = response.get_json()

    assert data["error"] == "Age must be greater than 0"
def test_student_cannot_create_student(client):

    student_token = get_token(
        client,
        "creatorstudent",
        "creatorstudent@gmail.com",
        "123456"
    )

    response = client.post(
        "/students",
        json={
            "name": "Not Allowed",
            "age": 20
        },
        headers={
            "Authorization": f"Bearer {student_token}"
        }
    )

    assert response.status_code == 403
def test_teacher_can_update_student(client):

    teacher_email = "putteacher@gmail.com"

    teacher_token = get_token(
        client,
        "putteacher",
        teacher_email,
        "123456"
    )

    make_role(
        teacher_email,
        "teacher"
    )

    # Create student
    create_response = client.post(
        "/students",
        json={
            "name": "Original Name",
            "age": 20
        },
        headers={
            "Authorization": f"Bearer {teacher_token}"
        }
    )

    assert create_response.status_code == 201

    student_id = (
        create_response
        .get_json()["student"]["id"]
    )

    # Update student
    response = client.put(
        f"/students/{student_id}",
        json={
            "name": "Updated Name",
            "age": 25
        },
        headers={
            "Authorization": f"Bearer {teacher_token}"
        }
    )

    assert response.status_code == 200

    data = response.get_json()

    assert data["message"] == "Student updated successfully"
    assert data["student"]["name"] == "Updated Name"
    assert data["student"]["age"] == 25
def test_student_cannot_update_student(client):

    student_token = get_token(
        client,
        "updatestudent",
        "updatestudent@gmail.com",
        "123456"
    )

    teacher_email = "updateteacher@gmail.com"

    teacher_token = get_token(
        client,
        "updateteacher",
        teacher_email,
        "123456"
    )

    make_role(
        teacher_email,
        "teacher"
    )

    # Teacher creates student
    create_response = client.post(
        "/students",
        json={
            "name": "Protected Student",
            "age": 20
        },
        headers={
            "Authorization": f"Bearer {teacher_token}"
        }
    )

    assert create_response.status_code == 201

    student_id = (
        create_response
        .get_json()["student"]["id"]
    )

    # Student attempts update
    response = client.put(
        f"/students/{student_id}",
        json={
            "name": "Hacked Name",
            "age": 99
        },
        headers={
            "Authorization": f"Bearer {student_token}"
        }
    )

    assert response.status_code == 403
def test_update_student_invalid_age(client):

    teacher_email = "invalidputteacher@gmail.com"

    teacher_token = get_token(
        client,
        "invalidputteacher",
        teacher_email,
        "123456"
    )

    make_role(
        teacher_email,
        "teacher"
    )

    # Create student
    create_response = client.post(
        "/students",
        json={
            "name": "Test Student",
            "age": 20
        },
        headers={
            "Authorization": f"Bearer {teacher_token}"
        }
    )

    assert create_response.status_code == 201

    student_id = (
        create_response
        .get_json()["student"]["id"]
    )

    # Invalid age
    response = client.put(
        f"/students/{student_id}",
        json={
            "age": -10
        },
        headers={
            "Authorization": f"Bearer {teacher_token}"
        }
    )

    assert response.status_code == 400

    data = response.get_json()

    assert data["error"] == "Age must be greater than 0"
def test_update_student_not_found(client):

    teacher_email = "notfoundputteacher@gmail.com"

    teacher_token = get_token(
        client,
        "notfoundputteacher",
        teacher_email,
        "123456"
    )

    make_role(
        teacher_email,
        "teacher"
    )

    response = client.put(
        "/students/9999",
        json={
            "name": "Does Not Exist",
            "age": 30
        },
        headers={
            "Authorization": f"Bearer {teacher_token}"
        }
    )

    assert response.status_code == 404

    data = response.get_json()

    assert data["error"] == "Student not found"