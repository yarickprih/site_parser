def test_index_user_not_logged_in(client):
    response = client.get("/")
    assert response.status_code == 302
