# Recomendador de libros con Flask y Gemini

Proyecto de clase para desplegar una **API REST** y un **frontend web** que recomiendan libros
a partir de una base de datos SQLite. La aplicación incluye:

- Recomendador clásico basado en filtros (género, rating, límite).
- **Chatbot de recomendación de libros** impulsado por un modelo LLM (Gemini).
- Base de datos SQLite con libros de ejemplo.
- API documentada y tests automatizados con `pytest`.
- Dockerfile para construir y ejecutar la aplicación en un contenedor.

---

## 1. Arquitectura general

### Componentes principales

- **Flask (`app.py`)**  
  - Expone los endpoints REST y las páginas HTML.
  - Gestiona el ciclo de vida de la aplicación y la conexión a la base de datos.

- **Base de datos SQLite (`books.db`)**  
  - Gestionada con **SQLAlchemy**.
  - Modelo principal: `Book` (título, autor, género, descripción, rating, nº de ratings).

- **Recomendador clásico (`recommender.py`)**
  - Función `recommend_books(params)` que realiza consultas SQL a la tabla `books`
    aplicando filtros por género, rating mínimo y límite de resultados.

- **Chatbot con LLM (`chat_llm.py`)**
  - Función `chat_recommend_books(chat_req)` que:
    1. Lee el historial de conversación del usuario.
    2. Obtiene una lista de libros candidatos de la base de datos.
    3. Llama al modelo de Gemini (`models/gemini-2.0-flash`) con un `prompt` que incluye:
       - Historial de chat.
       - Catálogo de libros (con IDs, título, autor, género y descripción).
    4. Espera una respuesta en formato JSON con:
       - `answer`: texto de respuesta al usuario.
       - `book_ids`: IDs de libros recomendados.
    5. Recupera esos libros de la BD y devuelve un `ChatResponse` con:
       - `reply`: texto de respuesta.
       - `recommendations`: lista de libros (`BookOut`).

  - **Fallback:** si la llamada a Gemini falla (por ejemplo, por falta de cuota o problemas
    de red) el sistema:
    - Devuelve una respuesta explicando que no se ha podido contactar con el modelo, y
    - Recomienda algunos de los libros más populares de la base de datos (top por rating).

- **Esquemas Pydantic (`schemas.py`)**
  - `RecommendationRequest`, `BookOut`, `RecommendationResponse` para el recomendador clásico.
  - `ChatMessage`, `ChatRequest`, `ChatResponse` para el chatbot.

- **Scripts auxiliares**
  - `seed_data.py`: crea la base de datos `books.db` y la rellena con libros de ejemplo.
  - `test_db.py`: comprueba que la base de datos y el modelo `Book` funcionan.
  - `test_recommender.py`, `test_api.py`: tests automatizados con `pytest`.

- **Frontend (plantillas Jinja2 en `templates/`)**
  - `base.html`: plantilla base con cabecera y navegación.
  - `index.html`: formulario de recomendación clásica (género, rating mínimo, límite).
  - `recommendations.html`: muestra la lista de libros recomendados.
  - `chat.html`: interfaz tipo chat para el chatbot con LLM.
  - `docs.html`: página de documentación de la API.

---

## 2. Requisitos

### Python

- Python 3.11 (recomendado)
- Pip actualizado

### Dependencias (requirements.txt)

Algunas de las dependencias principales son:

- `Flask`
- `Flask-SQLAlchemy`
- `pydantic`
- `google-generativeai` (cliente oficial para Gemini)
- `pytest`

Se instalan automáticamente con:

```bash
pip install -r requirements.txt
```

---

## 3. Variables de entorno

Para usar el LLM de Gemini, es necesario configurar la API key en la variable de entorno
`GEMINI_API_KEY`.

En **Windows (PowerShell)**:

```powershell
setx GEMINI_API_KEY "TU_API_KEY_DE_GEMINI"
# Cerrar y abrir una nueva terminal
echo $Env:GEMINI_API_KEY
```

En **Linux/macOS (bash)**:

```bash
export GEMINI_API_KEY="TU_API_KEY_DE_GEMINI"
echo $GEMINI_API_KEY
```

> Nota: si la cuota de la API key para el modelo `models/gemini-2.0-flash` es 0, la llamada
> al LLM devolverá un error 429 (quota exceeded) y el sistema activará automáticamente
> el modo *fallback* basado únicamente en la base de datos local.

---

## 4. Puesta en marcha en local

### 4.1. Clonar el proyecto y crear entorno

```bash
git clone <url-del-repositorio>
cd book_recommender
python -m venv .venv
# En Windows
.venv\Scripts\activate
# En Linux/macOS
source .venv/bin/activate
```

### 4.2. Instalar dependencias

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 4.3. Crear y poblar la base de datos

```bash
python seed_data.py
```

Esto creará el archivo `books.db` en la raíz del proyecto y lo poblará con libros de ejemplo.

### 4.4. Ejecutar la aplicación Flask

```bash
python app.py
```

Por defecto se levantará en:

- `http://127.0.0.1:5000`

Con la aplicación en marcha puedes acceder a:

- `/` → formulario de recomendación clásica.
- `/recommendations` → resultados del formulario.
- `/chat` → interfaz de chatbot con LLM.
- `/docs` → documentación simple de la API.
- `/health` → endpoint de salud (`{"status": "ok"}`).

---

## 5. Endpoints de la API

### 5.1. `GET /health`

Comprueba el estado básico de la aplicación.

**Respuesta de ejemplo**

```json
{
  "status": "ok"
}
```

---

### 5.2. `POST /api/recommend` (recomendador clásico)

Filtra libros según los parámetros proporcionados. El motor es puramente SQL/SQLAlchemy
(no usa el LLM).

**Body (JSON)**

```json
{
  "favorite_genre": "Fantasia",
  "min_rating": 4.0,
  "limit": 3
}
```

Campos:

- `favorite_genre` (opcional): género preferido.
- `min_rating` (float, opcional): rating mínimo (por defecto 4.0 si no se indica).
- `limit` (int, opcional): número máximo de libros a devolver.

**Respuesta (200)**

```json
{
  "recommendations": [
    {
      "id": 1,
      "title": "El Señor de los Anillos",
      "author": "J. R. R. Tolkien",
      "genre": "Fantasia",
      "description": "...",
      "rating": 4.9
    }
  ]
}
```

---

### 5.3. `POST /api/chat` (chatbot con LLM)

Endpoint del chatbot de recomendación de libros. Recibe el historial de la conversación
y devuelve una respuesta en lenguaje natural junto con recomendaciones de libros.

**Body (JSON)**

```json
{
  "messages": [
    { "role": "user", "content": "Hola, me gustan los libros de fantasía y terror, recomiéndame 3." }
  ]
}
```

- `messages`: lista de mensajes del chat.
  - `role`: `"user"` o `"assistant"`.
  - `content`: texto del mensaje.

**Respuesta (200)**

```json
{
  "reply": "Aquí tienes algunas recomendaciones de fantasía y terror que podrían gustarte...",
  "recommendations": [
    {
      "id": 1,
      "title": "El Señor de los Anillos",
      "author": "J. R. R. Tolkien",
      "genre": "Fantasia",
      "description": "...",
      "rating": 4.9
    }
  ]
}
```

Internamente:

- Si la llamada al modelo `models/gemini-2.0-flash` tiene éxito, la selección y el orden
  de los libros dependen del LLM.
- Si la llamada falla (por ejemplo, error 429 de cuota), el endpoint responde igualmente
  pero seleccionando los libros más populares de la base de datos (modo *fallback*).

---

## 6. Frontend

### 6.1. Página de inicio (`/`)

- Formulario para usar el recomendador clásico.
- Permite elegir género favorito, rating mínimo y número máximo de resultados.
- Envía una petición POST a `/recommendations` y muestra los resultados en una tabla.

### 6.2. Chatbot (`/chat`)

- Interfaz tipo chat implementada en `chat.html` con JavaScript sencillo.
- Mantiene el historial de mensajes en el navegador y lo envía a `/api/chat`.
- Muestra:
  - mensajes del usuario (`Tú:`),
  - respuestas del bot (`Bot:`),
  - lista de libros recomendados debajo de cada respuesta del bot.

### 6.3. Documentación (`/docs`)

- Página HTML con ejemplos de uso de los endpoints:
  - `/health`
  - `/api/recommend`
  - `/api/chat`

---

## 7. Tests automatizados

El proyecto incluye tests con `pytest` para verificar:

- Que la base de datos y el modelo `Book` funcionan correctamente.
- Que el recomendador clásico devuelve resultados adecuados.
- Que el endpoint `/api/recommend` responde con el formato esperado.

Para ejecutar los tests:

```bash
pytest
```

Si todos los tests pasan, verás algo similar a:

```text
7 passed, 1 warning in 0.63s
```

---

## 8. Docker

La aplicación incluye un `Dockerfile` para construir una imagen Docker que:

- Copia el código del proyecto.
- Instala las dependencias desde `requirements.txt`.
- Ejecuta la aplicación Flask en el puerto 5000.

### 8.1. Construir la imagen

Desde la raíz del proyecto:

```bash
docker build -t book-recommender .
```

### 8.2. Ejecutar el contenedor

```bash
docker run -p 5000:5000 -e GEMINI_API_KEY="TU_API_KEY_DE_GEMINI" book-recommender
```

Después podrás acceder a la aplicación en:

- `http://127.0.0.1:5000/`

> Nota: si en el entorno de ejecución dentro de Docker la API key no tiene cuota o no
> puede acceder a Gemini, el chatbot seguirá funcionando en modo *fallback* usando solo
> la base de datos local.

---

## 9. Limitaciones y posibles mejoras

- El catálogo de libros de ejemplo es pequeño y no pretende ser exhaustivo.
- Actualmente el LLM se usa como **re-ranker/generador** sobre un conjunto de candidatos
  recuperados de la BD; no se hace búsqueda semántica avanzada.
- El manejo de usuarios no está implementado (no hay login ni perfiles persistentes).

Posibles mejoras futuras:

- Añadir autenticación de usuarios y preferencias personalizadas.
- Integrar un buscador semántico (embeddings) para enriquecer la selección de candidatos.
- Guardar el historial de conversaciones en la base de datos.
- Añadir paginación en las recomendaciones.
- Incluir más metadatos de los libros (año, idioma, número de páginas, etc.).

---

## 10. Resumen

Este proyecto cumple los objetivos planteados en la práctica:

- Despliega un modelo LLM (Gemini) accesible mediante API REST.
- Ofrece un endpoint principal (`/api/chat`) para consumir el LLM en forma de chatbot.
- Incluye un frontend web tanto para recomendaciones clásicas como para el chatbot.
- Usa una base de datos real (SQLite + SQLAlchemy).
- Está dockerizado y preparado para ejecutarse en un contenedor.
- Incorpora tests automatizados y documentación básica de la API.

