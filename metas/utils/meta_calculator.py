"""Cálculo determinístico del plan de presupuesto (fuente de verdad).

MANTENER SINCRONIZADO con el frontend `BudgetCalculator.swift`.
"""
from typing import Optional, Tuple, Dict, Any

# Costos fijos por tag (COP). "ahorro" y "futuro" se calculan desde el ingreso.
_COSTOS_FIJOS = {
    "hogar": 180_000_000,
    "movilidad": 65_000_000,
    "viaje": 8_000_000,
    "educacion": 80_000_000,
}


def costo_meta_por_tag(tag: Optional[str], ingreso_mensual: float, costo_custom: float) -> float:
    if tag == "ahorro":
        return ingreso_mensual * 6
    if tag == "futuro":
        return ingreso_mensual * 12 * 20
    if tag in _COSTOS_FIJOS:
        return float(_COSTOS_FIJOS[tag])
    return float(costo_custom)        # custom / sin tag


def instrumento(horizonte_meses: int) -> Tuple[str, str]:
    if horizonte_meses < 12:
        return ("CDT",
                "Certificado de depósito a término. Liquidez y bajo riesgo para metas de corto plazo.")
    if horizonte_meses < 36:
        return ("TES — Títulos de Tesorería",
                "Renta fija del Estado colombiano. Bajo riesgo y rendimiento estable a tu plazo.")
    if horizonte_meses < 84:
        return ("Mix TES + ETF conservador",
                "Combinas renta fija estable con algo de crecimiento para un plazo medio.")
    return ("ETF de crecimiento (QQQ / VGT)",
            "Acciones de crecimiento global. Más volátil, pero potente en el largo plazo.")


def mensaje_toro(viabilidad: str) -> str:
    if viabilidad == "verde":
        return ("¡Esto es 100% alcanzable! Con disciplina, tu meta deja de ser un sueño y se vuelve "
                "un plan. Tu yo del futuro te lo va a agradecer 🚀")
    if viabilidad == "amarillo":
        return ("Se puede, pero pide constancia. Aquí la disciplina es tu superpoder: mete el ahorro "
                "en automático y no lo sueltes 💪")
    return ("Está apretado, no te voy a mentir. Pero no es un “no”, es un “todavía no”. Estiremos el "
            "tiempo o subamos el ingreso y vamos 💪")


def calcular(
    meta_titulo: str,
    meta_tag: Optional[str],
    es_custom: bool,
    horizonte_meses: int,
    ingreso_mensual: float,
    gastos_mensuales: float,
    costo_meta: float,
) -> Dict[str, Any]:
    meses = max(1, int(horizonte_meses))
    costo = costo_meta_por_tag(meta_tag, ingreso_mensual, costo_meta)
    ahorro_mes = costo / meses
    pct = (ahorro_mes / ingreso_mensual) if ingreso_mensual > 0 else 1.0
    disponible = max(ingreso_mensual - gastos_mensuales, 1.0)
    ratio = ahorro_mes / disponible

    if ratio <= 0.5:
        viabilidad = "verde"
    elif ratio <= 1.0:
        viabilidad = "amarillo"
    else:
        viabilidad = "rojo"

    inst_nombre, inst_desc = instrumento(meses)

    return {
        "meta_titulo": meta_titulo,
        "meta_tag": meta_tag,
        "es_custom": es_custom,
        "horizonte_meses": meses,
        "costo_meta": costo,
        "ahorro_requerido": ahorro_mes,
        "pct_ingreso": pct,
        "viabilidad": viabilidad,
        "instrumento": inst_nombre,
        "instrumento_desc": inst_desc,
        "mensaje_toro": mensaje_toro(viabilidad),
    }
