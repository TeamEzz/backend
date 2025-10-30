from datetime import datetime
from sqlalchemy.orm import Session
from ..models.chat_model import Conversacion, Mensaje

def obtener_o_crear_conversacion(db: Session, usuario_id: int, conversacion_id: int | None):
    if conversacion_id:
        conversacion = (
            db.query(Conversacion)
            .filter_by(id=conversacion_id, usuario_id=usuario_id)
            .first()
        )
        if conversacion:
            return conversacion
    # Crear nueva conversación si no existe
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
    # Se asume que m.remitente ya almacena 'user' o 'assistant'
    historial = [{"role": m.remitente, "content": m.contenido} for m in mensajes_db]
    return historial


def guardar_mensajes(db: Session, conversacion_id: int, mensaje_usuario: str, mensaje_ia: str):
    ahora = datetime.utcnow()
    db.add_all(
        [
            Mensaje(
                conversacion_id=conversacion_id,
                remitente="user",
                contenido=mensaje_usuario,
                timestamp=ahora,
            ),
            Mensaje(
                conversacion_id=conversacion_id,
                remitente="assistant",
                contenido=mensaje_ia,
                timestamp=ahora,
            ),
        ]
    )
    # Actualiza marca de tiempo de la conversación
    conv = db.query(Conversacion).filter_by(id=conversacion_id).first()
    if conv:
        conv.fecha_ultima_actualizacion = ahora
    db.commit()


def listar_conversaciones_usuario(db: Session, usuario_id: int):
    return (
        db.query(Conversacion)
        .filter(Conversacion.usuario_id == usuario_id)
        .order_by(Conversacion.fecha_ultima_actualizacion.desc())
        .all()
    )


def obtener_mensajes_conversacion(db: Session, conversacion_id: int):
    return (
        db.query(Mensaje)
        .filter(Mensaje.conversacion_id == conversacion_id)
        .order_by(Mensaje.timestamp.asc())
        .all()
    )
