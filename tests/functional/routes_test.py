from project.main.models import User


class TestRegistration:
    registration_data = {
        "username": "Test Username",
        "password": "testpassword",
        "confirm": "testpassword",
    }

    def test_registration_route_get(self, app, client):
        response = client.get("/register")
        assert response.status_code == 200
        assert b"Registration Page" in response.data

    def test_registration_route_post_request(self, app, client, test_database):
        response = client.post(
            "/register",
            data=self.registration_data,
            follow_redirects=True,
        )
        assert response.status == "200 OK"
        assert b"User has been created successfully!" in response.data

    def test_registration_route_empty_fields(self, app, client):
        invalid_data = {
            "username": "",
            "password": "",
            "confirm": "",
        }
        response = client.post(
            "/register",
            data=invalid_data,
            follow_redirects=True,
        )
        for field in invalid_data:
            assert (
                f"{field.title()}: This field is required"
            ).encode() in response.data

    def test_registration_route_invalid_confirm(self, app, client):
        invalid_data = {
            "username": "User",
            "password": "invalid password",
            "confirm": "invalid confirm",
        }
        response = client.post(
            "/register",
            data=invalid_data,
            follow_redirects=True,
        )
        assert b"Passwords must match" in response.data

    def test_registration_route_user_exists(self, app, client, test_user):
        invalid_data = {
            "username": "User",
            "password": "invalid password",
            "confirm": "invalid password",
        }
        response = client.post(
            "/register",
            data=invalid_data,
            follow_redirects=True,
        )
        # assert b"already registered!" in response.data
        assert response.status_code == 200
        assert response.request.path == "/register"


class TestLogin:
    login_data = {
        "username": "User",
        "password": "password",
    }

    def test_login_route_get(self, app, client):
        response = client.get("/login")
        assert response.status_code == 200
        assert b"Login Page" in response.data

    # def test_login_route_post(self, app, client):
    #     user = User.query.filter_by(username="User")
    #     response = client.post(
    #         "/login",
    #         data=self.login_data,
    #         follow_redirects=True,
    #     )
    #     assert response.status_code == 200
    #     assert response.request.path == "/"
    #     assert b"User has been authenticated successfully!" in response.data


# class TestLogout:
#     def test_logout_route(self, app, client, logged_in_user):
#         response = client.get("/logout")
#         print(response.data)
