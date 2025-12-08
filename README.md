# Recomendador de libros (Flask)

Proyecto de clase de Ingeniería de Datos / Machine Learning:
un **servicio web** que recomienda libros a partir de un pequeño catálogo,
expuesto mediante una **API REST en Flask** y un **frontend HTML** sencillo.

## Tecnologías

- Python 3.11
- Flask
- Flask-SQLAlchemy (SQLite como base de datos)
- Pydantic (validación de datos)
- HTML + Jinja2 (templates de Flask)

## Estructura del proyecto

```text
book_recommender/
├── app.py                 # Aplicación Flask (API + frontend)
├── database.py            # Inicialización de SQLAlchemy
├── models.py              # Modelo ORM Book
├── recommender.py         # Lógica de recomendación
├── schemas.py             # Esquemas Pydantic (entrada/salida)
├── seed_data.py           # Script para crear y poblar la base de datos
├── test_db.p_
