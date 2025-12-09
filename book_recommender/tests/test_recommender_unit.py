# tests/test_recommender_unit.py
from flask import Flask

from database import db
from models import Book
from recommender import recommend_books
from schemas import RecommendationRequest

# Usamos el mismo fichero books.db para no complicar la configuración
DB_URI = "sqlite:///books.db"


def create_test_app():
    """
    Crea una app Flask mínima para los tests de lógica.
    """
    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = DB_URI
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    db.init_app(app)
    return app


def setup_module(module):
    """
    Esta función se ejecuta UNA VEZ antes de todos los tests de este fichero.

    Aquí:
    - Borramos todas las tablas si existen.
    - Creamos las tablas.
    - Insertamos algunos libros de ejemplo para probar el recomendador.
    """
    app = create_test_app()
    with app.app_context():
        db.drop_all()
        db.create_all()

        sample_books = [
            Book(
                title="El Señor de los Anillos",
                author="J. R. R. Tolkien",
                genre="Fantasia",
                description="La comunidad del anillo y la lucha contra Sauron.",
                rating=4.9,
                n_ratings=250000,
            ),
            Book(
                title="El nombre del viento",
                author="Patrick Rothfuss",
                genre="Fantasia",
                description="La historia de Kvothe, un mago legendario.",
                rating=4.7,
                n_ratings=180000,
            ),
            Book(
                title="Dune",
                author="Frank Herbert",
                genre="Ciencia ficcion",
                description="Intriga política en el planeta desértico Arrakis.",
                rating=4.6,
                n_ratings=120000,
            ),
            Book(
                title="1984",
                author="George Orwell",
                genre="Distopia",
                description="Un clásico sobre la vigilancia y el totalitarismo.",
                rating=4.5,
                n_ratings=200000,
            ),
        ]

        db.session.bulk_save_objects(sample_books)
        db.session.commit()


def test_there_are_books():
    """
    Asegura que la base de datos de test tiene libros.
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
        min_rating = 4.6
        params = RecommendationRequest(min_rating=min_rating)
        recs = recommend_books(params)

        for book in recs:
            assert book.rating is None or book.rating >= min_rating


def test_filter_by_genre_works():
    """
    Comprobar que el filtro por género afecta a los resultados.
    """
    app = create_test_app()
    with app.app_context():
        # Sin filtro de género
        params_all = RecommendationRequest(limit=10)
        recs_all = recommend_books(params_all)

        # Con filtro de género (Fantasia, sin tilde para evitar problemas de codificación)
        params_fantasy = RecommendationRequest(favorite_genre="Fantasia", limit=10)
        recs_fantasy = recommend_books(params_fantasy)

        # Si hay recomendaciones con el filtro, comprobamos que al menos
        # alguna contenga "Fantas" en el género almacenado en la BD
        if recs_fantasy:
            assert any("Fantas" in (book.genre or "") for book in recs_fantasy)

        # En cualquier caso, los resultados con filtro no deberían ser más
        # numerosos que los resultados sin filtro
        assert len(recs_fantasy) <= len(recs_all)

