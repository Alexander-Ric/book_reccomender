from datetime import datetime
from database import db

class Book(db.Model):
    __tablename__= "books"
    
    id = db.Column(db.Integer, primary_key= True) #Clave Primaria
    title = db.Column (db.String(255), nullable = False) #Nombre del libro, sin nulos
    author = db.Column (db.String(255), nullable = False) #Autor
    genre = db.Column (db.String(100), nullable = False) #Género
    description = db.Column (db.Text, nullable = True) #Descripicón como opcional, acepta nulo.
    n_ratings = db.Column(db.Integer, nullable=True) #Numero de valoraciones
    rating = db.Column (db.Float, nullable = False) #Nota media
    created_at = db.Column ( db.DateTime, default =datetime.utcnow) #Fecha de inserción del registro.
    
def __repr__(self):
    return f"<Book {self.title} ({self.author})>"
