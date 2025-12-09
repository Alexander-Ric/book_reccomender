# recommender.py
from typing import List
from database import db  # no lo usamos directamente ahora, pero puede ser útil
from models import Book
from schemas import RecommendationRequest, BookOut


def recommend_books(params: RecommendationRequest) -> List[BookOut]:
    """
    Lógica principal del recomendador de libros.

    Recibe un RecommendationRequest (parámetros de usuario)
    y devuelve una lista de BookOut (libros recomendados).
    """

    # 1. Empezamos por todos los libros
    query = Book.query

    # 2. Filtramos por género si el usuario lo ha enviado
    if params.favorite_genre:
        # ilike -> case-insensitive; usamos % para permitir "contiene"
        query = query.filter(Book.genre.ilike(f"%{params.favorite_genre}%"))

    # 3. Filtramos por rating mínimo
    if params.min_rating is not None:
        query = query.filter(Book.rating >= params.min_rating)

    # 4. Ordenamos: primero mayor rating, luego más valoraciones
    query = query.order_by(Book.rating.desc(), Book.n_ratings.desc())

    # 5. Limitamos el número de resultados
    books = query.limit(params.limit).all()

    # 6. Convertimos los objetos Book (ORM) a BookOut (Pydantic)
    result: List[BookOut] = [
        BookOut(
            id=b.id,
            title=b.title,
            author=b.author,
            genre=b.genre,
            description=b.description,
            rating=b.rating,
        )
        for b in books
    ]

    return result
