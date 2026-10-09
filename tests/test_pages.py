import pytest


# ------------------------------------------------------------------ #
# Public pages                                                        #
# ------------------------------------------------------------------ #

@pytest.mark.parametrize("path", ["/", "/register", "/login"])
def test_page_loads(client, path):
    response = client.get(path)
    assert response.status_code == 200
    assert response.content_type.startswith("text/html")


def test_register_form_fields(client):
    html = client.get("/register").get_data(as_text=True)
    assert 'action="/register"' in html
    for field in ("name", "email", "password"):
        assert f'name="{field}"' in html


def test_login_form_fields(client):
    html = client.get("/login").get_data(as_text=True)
    assert 'action="/login"' in html
    for field in ("email", "password"):
        assert f'name="{field}"' in html


def test_unknown_page_returns_404(client):
    assert client.get("/does-not-exist").status_code == 404


# ------------------------------------------------------------------ #
# Placeholder routes — update these as each step is implemented       #
# ------------------------------------------------------------------ #

@pytest.mark.parametrize(
    "path",
    ["/logout", "/profile", "/expenses/add", "/expenses/1/edit", "/expenses/1/delete"],
)
def test_placeholder_routes_respond(client, path):
    assert client.get(path).status_code == 200


def test_expense_routes_require_integer_id(client):
    assert client.get("/expenses/abc/edit").status_code == 404
