# test_db.py
from flask import Flask
from database import db
from models import Book


def create_app():
    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///books.db"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    db.init_app(app)
    return app


if __name__ == "__main__":
    app = create_app()

    with app.app_context():
        # 1) Ver cuántos libros hay
        count = Book.query.count()
        print(f"Número de libros en la base de datos: {count}")

        # 2) Ver el primero
        first_book = Book.query.first()
        print("Primer libro en la base de datos (repr):", repr(first_book))
        print("Primer libro en la base de datos (print normal):", first_book)

        # 3) Listar algunos títulos
        print("\nPrimeros 5 libros:")
        for b in Book.query.limit(5).all():
            print(f"- {b.title} ({b.author})")
