# tests/test_recommender_unit.py
from flask import Flask

from database import db
from models import Book
from recommender import recommend_books
from schemas import RecommendationRequest


def create_test_app():
    """
    Crea una app Flask mínima apuntando a la misma base de datos books.db.

    Para estos tests asumimos que ya has ejecutado `python seed_data.py`
    y que la tabla `books` está poblada.
    """
    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///books.db"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    db.init_app(app)
    return app


def test_there_are_books():
    """
    Asegura que la base de datos tiene libros.
    Esto nos da confianza de que el seed se ha ejecutado correctamente.
    """
    app = create_test_app()
    with app.app_context():
        count = Book.query.count()
        assert count > 0


def test_limit_is_respected():
    """
    El recomendador nunca debe devolver más libros que el límite pedido.
    """
    app = create_test_app()
    with app.app_context():
        params = RecommendationRequest(limit=3)
        recs = recommend_books(params)
        assert len(recs) <= 3


def test_min_rating_is_respected():
    """
    Todos los libros devueltos deben tener un rating >= min_rating.
    """
    app = create_test_app()
    with app.app_context():
        min_rating = 4.5
        params = RecommendationRequest(min_rating=min_rating)
        recs = recommend_books(params)

        # Si no hay recomendaciones, el test sigue siendo válido
        for book in recs:
            assert book.rating is None or book.rating >= min_rating


def test_filter_by_genre_works():
    """
    Comprobar que el filtro por género afecta a los resultados.
    No necesitamos el género exacto, solo que funcione el filtro.
    """
    app = create_test_app()
    with app.app_context():
        # Sin filtro de género
        params_all = RecommendationRequest(limit=10)
        recs_all = recommend_books(params_all)

        # Con filtro de género (Fantasia, sin tilde para evitar líos)
        params_fantasy = RecommendationRequest(favorite_genre="Fantasia", limit=10)
        recs_fantasy = recommend_books(params_fantasy)

        # Si hay recomendaciones con el filtro, comprobamos que al menos
        # alguno contenga algo tipo "Fantas" en el género.
        if recs_fantasy:
            assert any("Fantas" in (book.genre or "") for book in recs_fantasy)

        # En cualquier caso, los resultados con filtro no deberían ser más
        # numerosos que los resultados sin filtro
        assert len(recs_fantasy) <= len(recs_all)
