def test_index_user_not_logged_in(app, client):
    with app.test_request_context():
        response = client.get("/")
        assert response.status_code == 404
