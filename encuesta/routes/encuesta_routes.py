from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from ..schemas import encuesta_schema
from ..utils.encuesta_utils import procesar_respuestas
from database.models.encuesta_model import RespuestaEncuestaDB
from database.db import SessionLocal  

router = APIRouter(prefix="/encuesta", tags=["Encuesta"])

# Dependencia para obtener la sesión de base de datos
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/responder", response_model=encuesta_schema.Resultados)
def responder_encuesta(payload: encuesta_schema.RespuestaEncuesta, db: Session = Depends(get_db)):
    try:
        # Procesar las respuestas como antes
        resultados = procesar_respuestas(payload.respuestas)

        # Guardar en la base de datos
        from json import dumps
        respuestas_json = dumps(payload.respuestas)

        existente = db.query(RespuestaEncuestaDB).filter_by(usuario_id=payload.usuario_id).first()

        if existente:
            existente.respuestas_json = respuestas_json
        else:
            nueva = RespuestaEncuestaDB(
                usuario_id=payload.usuario_id,
                respuestas_json=respuestas_json
            )
            db.add(nueva)

        db.commit()

        return resultados
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error procesando encuesta: {str(e)}")
