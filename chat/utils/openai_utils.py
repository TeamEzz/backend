from datetime import datetime
from sqlalchemy.orm import Session
from ..schemas.chat_schema import Conversacion, Mensaje

def obtener_o_crear_conversacion(db: Session, usuario_id: int, conversacion_id: int | None):
    if conversacion_id:
        conversacion = db.query(Conversacion).filter_by(id=conversacion_id, usuario_id=usuario_id).first()
        if conversacion:
            return conversacion
    # Si no existe, creamos una nueva
    nueva = Conversacion(usuario_id=usuario_id)
    db.add(nueva)
    db.commit()
    db.refresh(nueva)
    return nueva

def obtener_historial_conversacion(db: Session, conversacion_id: int):
    mensajes_db = (
        db.query(Mensaje)
        .filter_by(conversacion_id=conversacion_id)
        .order_by(Mensaje.timestamp.asc())
        .all()
    )
    historial = [
        {"role": m.autor, "content": m.contenido} for m in mensajes_db
    ]
    return historial


def guardar_mensajes(db, conversacion_id, mensaje_usuario, mensaje_ia):
    db.add_all([
        Mensaje(conversacion_id=conversacion_id, autor="user", contenido=mensaje_usuario, timestamp=datetime.utcnow()),
        Mensaje(conversacion_id=conversacion_id, autor="assistant", contenido=mensaje_ia, timestamp=datetime.utcnow())
    ])
    db.commit()
