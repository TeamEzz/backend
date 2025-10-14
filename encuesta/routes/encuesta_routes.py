from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from json import dumps

from ..schemas import encuesta_schema
from ..utils.encuesta_utils import procesar_respuestas
from database.models.encuesta_model import RespuestaEncuestaDB
from database.db import get_db  # ✅ usa el get_db centralizado
from Auth.utils.jwt_utils import get_current_user  # ✅ toma el usuario del Bearer token
from database.models.user_model import Usuario

router = APIRouter(prefix="/encuesta", tags=["Encuesta"])


@router.post("/responder", response_model=encuesta_schema.Resultados)
def responder_encuesta(
    payload: encuesta_schema.RespuestaEncuesta,
    db: Session = Depends(get_db),
    user: Usuario = Depends(get_current_user),  # ← usuario autenticado por JWT
):
    try:
        # ✅ Prioriza el id del token; si viene en el body también sirve (compatibilidad)
        user_id = payload.usuario_id or user.id

        # Validaciones básicas
        if not payload.respuestas or len(payload.respuestas) < 12:
            raise HTTPException(status_code=400, detail="Encuesta incompleta")

        # Procesar como antes
        resultados = procesar_respuestas(payload.respuestas)

        # Guardar/actualizar en BD
        respuestas_json = dumps(payload.respuestas)
        existente = db.query(RespuestaEncuestaDB).filter_by(usuario_id=user_id).first()

        if existente:
            existente.respuestas_json = respuestas_json
        else:
            nueva = RespuestaEncuestaDB(
                usuario_id=user_id,
                respuestas_json=respuestas_json
            )
            db.add(nueva)

        db.commit()
        return resultados

    except HTTPException:
        # No hagas rollback en errores intencionales
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=f"Error procesando encuesta: {str(e)}")