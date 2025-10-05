from datetime import datetime, timedelta, timezone, date
from sqlalchemy import func, case
from database.models.gasto_model import Gasto
from database.models.streak_model import Streak
from database.models.leccion_model import ProgresoLeccion 
from typing import Tuple

def rango_periodo(periodo: str, now: datetime) -> Tuple[date, date]:
    hoy = now.date()
    if periodo == "diario":
        return hoy, hoy + timedelta(days=1)
    if periodo == "semanal":
        lunes = hoy - timedelta(days=hoy.weekday())
        return lunes, lunes + timedelta(days=7)
    if periodo == "mensual":
        primero = hoy.replace(day=1)
        if primero.month == 12:
            fin = primero.replace(year=primero.year+1, month=1, day=1)
        else:
            fin = primero.replace(month=primero.month+1, day=1)
        return primero, fin
    # anual
    primero = date(hoy.year, 1, 1)
    fin = date(hoy.year+1, 1, 1)
    return primero, fin

def build_streak(db, user_id: int):
    s = db.query(Streak).filter_by(usuario_id=user_id).first()
    if not s:
        return {"actual": 0, "maxima": 0, "hoy_contada": False}
    hoy_contada = (s.fecha_ultima_actividad == datetime.now().date())
    return {"actual": s.racha_actual, "maxima": s.racha_maxima, "hoy_contada": hoy_contada}

def build_gastos(db, user_id: int, inicio: date, fin: date, periodo: str):
    q = db.query(func.coalesce(func.sum(Gasto.monto), 0.0))\
          .filter(Gasto.usuario_id == user_id,
                  Gasto.fecha >= inicio,
                  Gasto.fecha <  fin)
    total = float(q.scalar() or 0.0)

    # por categoria
    rows = db.query(Gasto.categoria, func.sum(Gasto.monto))\
             .filter(Gasto.usuario_id == user_id,
                     Gasto.fecha >= inicio,
                     Gasto.fecha <  fin)\
             .group_by(Gasto.categoria).all()

    por_categoria = []
    for nombre, monto in rows:
        m = float(monto or 0.0)
        pct = 0.0 if total == 0 else m/total
        por_categoria.append({"nombre": nombre, "monto": m, "pct": pct})

    # necesarios vs no necesarios
    necesarios = float(db.query(func.coalesce(func.sum(Gasto.monto),0.0))
        .filter(Gasto.usuario_id==user_id,
                Gasto.fecha >= inicio, Gasto.fecha < fin,
                Gasto.es_necesario == True).scalar() or 0.0)
    necesarios_pct = 0.0 if total==0 else necesarios/total
    no_necesarios_pct = 1.0 - necesarios_pct if total>0 else 0.0

    return {
        "periodo": periodo,
        "inicio": inicio,
        "fin": fin,
        "total": total,
        "por_categoria": por_categoria,
        "necesarios_pct": necesarios_pct,
        "no_necesarios_pct": no_necesarios_pct,
    }

def build_lecciones(db, user_id: int, nivel: int):
    # Asumiendo que ya tienes tabla Leccion con campo nivel
    total = db.query(func.count(ProgresoLeccion.id)).filter(ProgresoLeccion.nivel == nivel).scalar() or 0
    completas = db.query(func.count(ProgresoLeccion.id))\
        .join(ProgresoLeccion, ProgresoLeccion.id == ProgresoLeccion.leccion_id)\
        .filter(ProgresoLeccion.usuario_id == user_id,
                ProgresoLeccion.completada == True,
                ProgresoLeccion.nivel == nivel).scalar() or 0
    return {"nivel": nivel, "completadas": int(completas), "total": int(total)}

def build_insights(gastos_total: float, gastos_semana_promedio: float = None):
    insights = []
    # ejemplo simple: compara contra promedio si te animas a calcularlo
    return insights