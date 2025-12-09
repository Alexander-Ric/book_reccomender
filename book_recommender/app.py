# app.py
from flask import Flask, request, jsonify, render_template
from pydantic import ValidationError

from database import db
from recommender import recommend_books
from schemas import (
    RecommendationRequest,
    RecommendationResponse,
    ChatRequest,
    ChatResponse,
)
from chat_llm import chat_recommend_books


def create_app():
    """
    Crea e inicializa la aplicación Flask.
    """
    app = Flask(__name__)

    # Configuración de la base de datos
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///books.db"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    # Inicializamos SQLAlchemy con esta app
    db.init_app(app)

    # ---------- RUTAS API (MODELO CLÁSICO) ----------

    @app.route("/health", methods=["GET"])
    def health():
        return jsonify({"status": "ok"})

    @app.route("/api/recommend", methods=["POST"])
    def api_recommend():
        """
        Endpoint principal de la API clásica (JSON in -> JSON out).
        Usa el recomendador basado en filtros SQL.
        """
        try:
            data = request.get_json()
            if data is None:
                return (
                    jsonify(
                        {
                            "error": "Se esperaba un cuerpo JSON en la petición.",
                        }
                    ),
                    400,
                )

            params = RecommendationRequest(**data)

        except ValidationError as e:
            return (
                jsonify(
                    {
                        "error": "Entrada inválida",
                        "details": e.errors(),
                    }
                ),
                400,
            )

        recommendations = recommend_books(params)
        response = RecommendationResponse(recommendations=recommendations)
        return jsonify(response.dict())

    # ---------- RUTAS API (CHATBOT CON GEMINI) ----------

    @app.route("/api/chat", methods=["POST"])
    def api_chat():
        """
        Endpoint del chatbot.

        Recibe el historial de mensajes y devuelve:
          - reply: texto del asistente
          - recommendations: lista de libros recomendados
        """
        data = request.get_json()
        if data is None:
            return jsonify({"error": "Se esperaba un cuerpo JSON."}), 400

        try:
            chat_req = ChatRequest(**data)
        except ValidationError as e:
            return (
                jsonify({"error": "Entrada inválida", "details": e.errors()}),
                400,
            )

        chat_resp: ChatResponse = chat_recommend_books(chat_req)
        return jsonify(chat_resp.dict())

    # ---------- RUTAS HTML (FRONTEND) ----------

    @app.route("/", methods=["GET"])
    def index():
        """
        Página principal con el formulario clásico.
        """
        return render_template("index.html")

    @app.route("/recommendations", methods=["POST"])
    def recommendations_page():
        """
        Procesa el formulario clásico y muestra recomendaciones.
        """
        favorite_genre = request.form.get("favorite_genre") or None
        min_rating_str = request.form.get("min_rating") or "4.0"
        limit_str = request.form.get("limit") or "5"

        try:
            min_rating = float(min_rating_str)
        except ValueError:
            min_rating = 4.0

        try:
            limit = int(limit_str)
        except ValueError:
            limit = 5

        params = RecommendationRequest(
            favorite_genre=favorite_genre,
            min_rating=min_rating,
            limit=limit,
        )

        recs = recommend_books(params)

        return render_template(
            "recommendations.html",
            recommendations=recs,
            params=params,
        )

    @app.route("/chat", methods=["GET"])
    def chat_page():
        """
        Página con interfaz tipo chat para recomendaciones LLM.
        """
        return render_template("chat.html")

    @app.route("/docs", methods=["GET"])
    def docs():
        """
        Página de documentación sencilla de la API.
        """
        return render_template("docs.html")

    return app


if __name__ == "__main__":
    app = create_app()
    with app.app_context():
        db.create_all()
    app.run(host="0.0.0.0", port=5000, debug=True)

