# seed_data.py
from flask import Flask
from database import db
from models import Book


def create_app():
    """
    Crea una app Flask mínima solo para gestionar la base de datos.
    Más adelante tendrás otra app (o esta misma) con las rutas de la API.
    """
    app = Flask(__name__)

    # Configuración de la base de datos: fichero SQLite en el proyecto
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///books.db"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    # Vinculamos SQLAlchemy con esta app
    db.init_app(app)

    return app


def seed():
    app = create_app()

    with app.app_context():
        # (Opcional, pero útil en desarrollo) Borrar todas las tablas existentes
        db.drop_all()

        # Crear todas las tablas definidas en models.py
        db.create_all()

        # Lista de libros de ejemplo
        books = [
            Book(
                title="Dune",
                author="Frank Herbert",
                genre="Ciencia ficción",
                description="Intriga política y aventuras en el planeta desértico Arrakis.",
                rating=4.6,
                n_ratings=120000,
            ),
            Book(
                title="1984",
                author="George Orwell",
                genre="Distopía",
                description="Un clásico sobre la vigilancia y los regímenes totalitarios.",
                rating=4.5,
                n_ratings=200000,
            ),
            Book(
                title="El nombre del viento",
                author="Patrick Rothfuss",
                genre="Fantasía",
                description="La historia de Kvothe, un mago legendario, narrada en primera persona.",
                rating=4.7,
                n_ratings=180000,
            ),
            Book(
                title="Orgullo y prejuicio",
                author="Jane Austen",
                genre="Romántica",
                description="Relaciones, prejuicios y crítica social en la Inglaterra del siglo XIX.",
                rating=4.4,
                n_ratings=150000,
            ),
            Book(
                title="Fundación",
                author="Isaac Asimov",
                genre="Ciencia ficción",
                description="Una saga sobre el colapso y renacimiento de un imperio galáctico.",
                rating=4.3,
                n_ratings=95000,
            ),
            Book(
                title="El Señor de los Anillos",
                author="J. R. R. Tolkien",
                genre="Fantasía",
                description="La comunidad del anillo y la lucha contra Sauron.",
                rating=4.9,
                n_ratings=250000,
            ),
            Book(
                title="Crónica de una muerte anunciada",
                author="Gabriel García Márquez",
                genre="Ficción",
                description="La historia de un crimen anunciado desde el principio.",
                rating=4.2,
                n_ratings=80000,
            ),
            Book(
                title="El código Da Vinci",
                author="Dan Brown",
                genre="Thriller",
                description="Un profesor de simbología se ve envuelto en una conspiración religiosa.",
                rating=3.8,
                n_ratings=300000,
            ),
            Book(
                title="Los pilares de la Tierra",
                author="Ken Follett",
                genre="Histórica",
                description="La construcción de una catedral en la Edad Media y sus conspiraciones.",
                rating=4.4,
                n_ratings=210000,
            ),
            Book(
                title="La sombra del viento",
                author="Carlos Ruiz Zafón",
                genre="Misterio",
                description="Un niño encuentra un libro maldito en el Cementerio de los Libros Olvidados.",
                rating=4.5,
                n_ratings=175000,
            ),
        ]

        # Puedes añadir más libros siguiendo el mismo patrón si quieres llegar a 20+.
        # Por ejemplo, duplicar con ligeras variaciones o añadir más títulos reales.

        db.session.bulk_save_objects(books)
        db.session.commit()

        print("Base de datos creada y sembrada con libros de ejemplo.")


if __name__ == "__main__":
    seed()
