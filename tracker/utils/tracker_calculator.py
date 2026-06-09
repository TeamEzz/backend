"""Cálculos del Budget Tracker (racha, proyección, total ahorrado).

MANTENER SINCRONIZADO con el frontend si se duplica la lógica de display.
Los check-ins entran como objetos `CheckIn` (SQLAlchemy) o cualquier objeto con
los atributos `mes`, `anio`, `monto_aportado`, `objetivo_mes`.
"""
import math
from typing import List


def calcular_total_ahorrado(check_ins: List) -> float:
    """Suma de todos los aportes registrados."""
    return float(sum(ci.monto_aportado for ci in check_ins))


def calcular_racha(check_ins: List) -> int:
    """Meses consecutivos (hacia atrás desde el más reciente) en que el usuario
    cumplió al menos el 50% del objetivo del mes. Se rompe al primer mes flojo.
    """
    if not check_ins:
        return 0

    # Orden cronológico descendente por (año, mes).
    ordenados = sorted(check_ins, key=lambda c: (c.anio, c.mes), reverse=True)

    racha = 0
    for ci in ordenados:
        objetivo = ci.objetivo_mes if ci.objetivo_mes > 0 else 1.0
        if (ci.monto_aportado / objetivo) >= 0.5:
            racha += 1
        else:
            break
    return racha


def calcular_proyeccion(total_ahorrado: float, costo_meta: float, promedio_mensual: float) -> int:
    """Meses restantes estimados para alcanzar la meta al ritmo promedio actual.

    Devuelve 0 si ya se alcanzó la meta. Si aún no hay ritmo (promedio <= 0),
    devuelve -1 como sentinel de "sin datos suficientes".
    """
    restante = costo_meta - total_ahorrado
    if restante <= 0:
        return 0
    if promedio_mensual <= 0:
        return -1
    return int(math.ceil(restante / promedio_mensual))
