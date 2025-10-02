from sqlalchemy import Column, Integer, String, ForeignKey
 # ✅ Correcto
from database.db import Base, SessionLocal, engine


class RespuestaEncuestaDB(Base):
    __tablename__ = "respuestas_encuesta"

    id = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), unique=True)
    respuestas_json = Column(String)  # Guardaremos la lista de respuestas como JSON
