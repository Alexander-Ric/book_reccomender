# chat_llm.py
import os
import json
from typing import List

import google.generativeai as genai

from models import Book
from schemas import ChatRequest, ChatResponse, BookOut


def _configure_gemini() -> None:
    """
    Configura la librería de Gemini usando la variable de entorno GEMINI_API_KEY.
    """
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError(
            "La variable de entorno GEMINI_API_KEY no está definida. "
            "Configúrala antes de usar el chatbot."
        )
    genai.configure(api_key=api_key)


def _get_candidate_books(limit: int = 30) -> List[Book]:
    """
    Selecciona libros candidatos de la base de datos.
    Aquí usamos un criterio sencillo: top N por rating y número de valoraciones.
    """
    return (
        Book.query
        .order_by(Book.rating.desc(), Book.n_ratings.desc())
        .limit(limit)
        .all()
    )


def chat_recommend_books(chat_req: ChatRequest) -> ChatResponse:
    """
    Usa Gemini como chatbot de recomendación de libros.

    Entrada: historial de mensajes (ChatRequest).
    Salida: texto del asistente + lista de libros recomendados (ChatResponse).
    """
    _configure_gemini()

    # 1. Candidatos desde la BD
    candidates = _get_candidate_books()

    books_description = []
    for b in candidates:
        books_description.append(
            f"ID {b.id}: '{b.title}' de {b.author} "
            f"({b.genre}, rating={b.rating}). "
            f"Descripción: {b.description}"
        )

    # 2. Historial de conversación a texto
    history_text = []
    for msg in chat_req.messages:
        prefix = "Usuario" if msg.role == "user" else "Asistente"
        history_text.append(f"{prefix}: {msg.content}")

    conversation_str = "\n".join(history_text)

    system_prompt = (
        "Eres un asistente que recomienda libros basándote en un catálogo "
        "predefinido. Solo puedes recomendar libros que estén en la lista "
        "que te proporciono.\n\n"
        "DEBES responder en castellano.\n\n"
        "Tu salida SIEMPRE debe ser un JSON con la siguiente estructura:\n"
        "{\n"
        '  \"answer\": \"<texto que le dirías al usuario>\",\n'
        '  \"book_ids\": [1, 5, 7]\n'
        "}\n"
        "Donde book_ids es una lista de IDs de los libros recomendados. "
        "Si no puedes recomendar nada, usa una lista vacía.\n"
        "No añadas texto fuera del JSON, ni explicaciones adicionales."
    )

    user_prompt = (
        "Historial de la conversación:\n"
        f"{conversation_str}\n\n"
        "Catálogo de libros disponibles (con IDs):\n"
        + "\n".join(books_description)
    )

    # 3. Llamada a Gemini
    model = genai.GenerativeModel("models/gemini-2.0-flash")

    try:
        response = model.generate_content(
            [system_prompt, user_prompt]
        )
        content = response.text.strip()
    except Exception as e:
        # Fallback si falla la llamada al LLM
        print("Error al llamar a Gemini:", e, flush=True)
        answer = (
            "No he podido conectar con el modelo de lenguaje ahora mismo. "
            "Aun así, te puedo recomendar algunos de los libros más populares "
            "de la base de datos."
        )
        ids = [b.id for b in candidates[:5]]

        selected_books = Book.query.filter(Book.id.in_(ids)).all()
        id_to_book = {b.id: b for b in selected_books}
        ordered = [id_to_book[i] for i in ids if i in id_to_book]

        recommendations = [
            BookOut(
                id=b.id,
                title=b.title,
                author=b.author,
                genre=b.genre,
                description=b.description,
                rating=b.rating,
            )
            for b in ordered
        ]

        return ChatResponse(reply=answer, recommendations=recommendations)

    # 4. Parsear el JSON devuelto por Gemini
    try:
        # Quitar posibles ```json ... ``` alrededor
        if content.startswith("```"):
            content = content.strip("`")
            if content.lower().startswith("json"):
                content = content[4:].strip()

        data = json.loads(content)
        answer = data.get("answer", "").strip()
        ids = data.get("book_ids", [])
    except Exception as e:
        print("Error al parsear la respuesta de Gemini:", e, flush=True)
        answer = (
            "Ha habido un problema interpretando la respuesta del modelo. "
            "Te puedo recomendar algunos de los libros más populares de la base de datos."
        )
        ids = [b.id for b in candidates[:5]]

    if not answer:
        answer = "Aquí tienes algunas recomendaciones de libros basadas en tus preferencias."

    # 5. Recuperar libros recomendados por ID y mantener orden
    selected_books = Book.query.filter(Book.id.in_(ids)).all()
    id_to_book = {b.id: b for b in selected_books}
    ordered = [id_to_book[i] for i in ids if i in id_to_book]

    recommendations = [
        BookOut(
            id=b.id,
            title=b.title,
            author=b.author,
            genre=b.genre,
            description=b.description,
            rating=b.rating,
        )
        for b in ordered
    ]

    return ChatResponse(reply=answer, recommendations=recommendations)
