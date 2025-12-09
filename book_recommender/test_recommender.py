# test_recommender.py
from flask import Flask
from database import db
from models import Book
from schemas import RecommendationRequest
from recommender import recommend_books


def create_app():
    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///books.db"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    db.init_app(app)
    return app


if __name__ == "__main__":
    app = create_app()

    with app.app_context():
        print("Número total de libros:", Book.query.count())

        # Caso 1: recomendaciones por defecto (sin género, rating>=4, limit=5)
        params1 = RecommendationRequest()
        recs1 = recommend_books(params1)
        print("\nCaso 1: recomendaciones por defecto")
        for b in recs1:
            print(f"- {b.title} ({b.author}) | {b.genre} | rating={b.rating}")

        # Caso 2: Fantasía, rating mínimo 4.5, máximo 3 libros
        params2 = RecommendationRequest(
            favorite_genre="Fantasía",
            min_rating=4.5,
            limit=3,
        )
        recs2 = recommend_books(params2)
        print("\nCaso 2: Fantasía, rating>=4.5, max 3 libros")
        for b in recs2:
            print(f"- {b.title} ({b.author}) | {b.genre} | rating={b.rating}")

        # Caso 3: Ciencia ficción, rating mínimo 4.0, máximo 10 libros
        params3 = RecommendationRequest(
            favorite_genre="Ciencia ficción",
            min_rating=4.0,
            limit=10,
        )
        recs3 = recommend_books(params3)
        print("\nCaso 3: Ciencia ficción, rating>=4.0, max 10 libros")
        for b in recs3:
            print(f"- {b.title} ({b.author}) | {b.genre} | rating={b.rating}")
