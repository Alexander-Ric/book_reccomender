# tests/test_api.py
import json

from app import create_app
from database import db
from models import Book


def setup_app():
    """
    Crea la app usando create_app() y se asegura de que la BD está lista.
    """
    app = create_app()
    with app.app_context():
        db.create_all()
    return app


def test_health_endpoint():
    """
    El endpoint /health debe devolver status=ok.
    """
    app = setup_app()
    client = app.test_client()

    response = client.get("/health")
    assert response.status_code == 200

    data = response.get_json()
    assert data["status"] == "ok"


def test_api_recommend_returns_json():
    """
    Llamada correcta a /api/recommend debe devolver 200 y un JSON
    con la clave 'recommendations'.
    """
    app = setup_app()
    client = app.test_client()

    payload = {
        "favorite_genre": "Fantasia",
        "min_rating": 4.0,
        "limit": 3,
    }

    response = client.post(
        "/api/recommend",
        data=json.dumps(payload),
        content_type="application/json",
    )

    assert response.status_code == 200

    data = response.get_json()
    assert "recommendations" in data
    assert isinstance(data["recommendations"], list)


def test_api_recommend_invalid_input():
    """
    Si enviamos un tipo de dato incorrecto (por ejemplo limit como string),
    la API debe responder con 400 y un mensaje de error.
    """
    app = setup_app()
    client = app.test_client()

    payload = {
        "favorite_genre": "Fantasia",
        "min_rating": 4.0,
        "limit": "no_es_un_numero",  # error intencionado
    }

    response = client.post(
        "/api/recommend",
        data=json.dumps(payload),
        content_type="application/json",
    )

    assert response.status_code == 400

    data = response.get_json()
    assert "error" in data
