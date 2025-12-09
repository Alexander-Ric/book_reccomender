# schemas.py
from pydantic import BaseModel, Field
from typing import List, Optional


class RecommendationRequest(BaseModel):
    """
    Datos de entrada al recomendador.
    """
    favorite_genre: Optional[str] = Field(
        None,
        description="Género favorito del usuario, por ejemplo 'Fantasía' o 'Ciencia ficción'."
    )
    min_rating: float = Field(
        4.0,
        ge=0,
        le=5,
        description="Rating mínimo de los libros recomendados (0-5)."
    )
    limit: int = Field(
        5,
        ge=1,
        le=50,
        description="Número máximo de libros a devolver."
    )


class BookOut(BaseModel):
    """
    Representación de un libro en las respuestas.
    """
    id: int
    title: str
    author: str
    genre: str
    description: Optional[str]
    rating: Optional[float]


class RecommendationResponse(BaseModel):
    """
    Respuesta del recomendador: una lista de libros.
    """
    recommendations: List[BookOut]
from typing import Literal

# ... (lo que ya tienes arriba)


class ChatMessage(BaseModel):
    """
    Mensaje de la conversación.
    role: 'user' o 'assistant'
    content: texto del mensaje.
    """
    role: Literal["user", "assistant"]
    content: str


class ChatRequest(BaseModel):
    """
    Petición al chatbot.
    messages: historial completo de la conversación hasta ahora.
    """
    messages: List[ChatMessage]


class ChatResponse(BaseModel):
    """
    Respuesta del chatbot.
    reply: texto de Gemini.
    recommendations: mismos campos que BookOut, si el modelo devolvió libros.
    """
    reply: str
    recommendations: List[BookOut] = []
