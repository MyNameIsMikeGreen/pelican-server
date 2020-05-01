def test_server_returns_static_homepage(client):
    response = client.get('/', follow_redirects=True)
    assert 200 == response.status_code
    with open("testresources/index.html") as index_page:
        expected_content = index_page.read()
        assert expected_content == response.data.decode("utf-8")
