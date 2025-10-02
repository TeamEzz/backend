from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database.db import get_db
from Auth.utils.jwt_utils import get_current_user
from database.models.gasto_model import Gasto
from pydantic import BaseModel
from datetime import datetime

router = APIRouter()

class GastoRequest(BaseModel):
    categoria: str
    monto: float
    es_necesario: bool
    fecha: datetime

@router.post("/registrar")
def registrar_gasto(data: GastoRequest, db: Session = Depends(get_db), usuario=Depends(get_current_user)):
    nuevo_gasto = Gasto(
        usuario_id=usuario.id,
        categoria=data.categoria,
        monto=data.monto,
        es_necesario=data.es_necesario,
        fecha=data.fecha
    )
    db.add(nuevo_gasto)
    db.commit()
    db.refresh(nuevo_gasto)
    return {"mensaje": "Gasto registrado correctamente"}

@router.get("/resumen")
def obtener_resumen_gastos(db: Session = Depends(get_db), usuario=Depends(get_current_user)):
    gastos = db.query(Gasto).filter(Gasto.usuario_id == usuario.id).all()
    return gastos