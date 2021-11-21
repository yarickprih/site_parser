def test_index_user_not_logged_in(app):
    client = app.test_client()
    with client:
        response = client.get("/")
    assert response.status_code == 404
