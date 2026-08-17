def test_home(client):

    response = client.get("/")

    assert response.status_code == 200


def test_register_user(client):

    response = client.post(
        "/register",
        json={
            "username": "testuser",
            "email": "testuser@gmail.com",
            "password": "123456"
        }
    )

    assert response.status_code == 201

    data = response.get_json()

    assert data["message"] == "User registered successfully"
    assert data["user"]["username"] == "testuser"
    assert data["user"]["email"] == "testuser@gmail.com"
    assert data["user"]["role"] == "student"
def test_duplicate_email(client):

    client.post(
        "/register",
        json={
            "username": "user1",
            "email": "same@gmail.com",
            "password": "123456"
        }
    )

    response = client.post(
        "/register",
        json={
            "username": "user2",
            "email": "same@gmail.com",
            "password": "123456"
        }
    )

    assert response.status_code == 409

    data = response.get_json()

    assert data["error"] == "Email already exists"
def test_register_short_password(client):

    response = client.post(
        "/register",
        json={
            "username": "testuser",
            "email": "test@gmail.com",
            "password": "123"
        }
    )

    assert response.status_code == 400

    data = response.get_json()

    assert data["error"] == (
        "Password must be at least 6 characters"
    )

def test_login_success(client):

    # First create a user
    client.post(
        "/register",
        json={
            "username": "loginuser",
            "email": "loginuser@gmail.com",
            "password": "123456"
        }
    )

    # Login
    response = client.post(
        "/login",
        json={
            "email": "loginuser@gmail.com",
            "password": "123456"
        }
    )

    assert response.status_code == 200

    data = response.get_json()

    assert data["message"] == "Login successful"
    assert "access_token" in data
    assert data["user"]["email"] == "loginuser@gmail.com"
def test_login_wrong_password(client):

    client.post(
        "/register",
        json={
            "username": "wrongpass",
            "email": "wrongpass@gmail.com",
            "password": "123456"
        }
    )

    response = client.post(
        "/login",
        json={
            "email": "wrongpass@gmail.com",
            "password": "wrongpassword"
        }
    )

    assert response.status_code == 401

    data = response.get_json()

    assert data["error"] == "Invalid email or password"
def test_login_unknown_user(client):

    response = client.post(
        "/login",
        json={
            "email": "doesnotexist@gmail.com",
            "password": "123456"
        }
    )

    assert response.status_code == 401

    data = response.get_json()

    assert data["error"] == "Invalid email or password"
def test_profile_without_token(client):

    response = client.get("/profile")

    assert response.status_code == 401
def test_profile_with_token(client):

    # Register
    client.post(
        "/register",
        json={
            "username": "profileuser",
            "email": "profileuser@gmail.com",
            "password": "123456"
        }
    )

    # Login
    login_response = client.post(
        "/login",
        json={
            "email": "profileuser@gmail.com",
            "password": "123456"
        }
    )

    token = login_response.get_json()["access_token"]

    # Access profile
    response = client.get(
        "/profile",
        headers={
            "Authorization": f"Bearer {token}"
        }
    )

    assert response.status_code == 200

    data = response.get_json()

    assert data["email"] == "profileuser@gmail.com"
    assert data["username"] == "profileuser"
    assert data["role"] == "student"