from typing import List
from pydantic import BaseModel


class Resultados(BaseModel):
    nivel_conocimiento: str
    perfil_riesgo: str
    objetivo: str
    aprendizajes: List[str]
    respuesta_ia: str = ""


def procesar_respuestas(respuestas: List[str]) -> Resultados:
    if len(respuestas) < 11:
        raise ValueError("Faltan respuestas para procesar la encuesta")
    aprendizajes = set()

    # Pregunta 1 - Objetivo
    objetivo = respuestas[0]

    # Pregunta 2 - Nivel de conocimiento
    conocimiento = respuestas[1].lower().strip()

    if "casi nada" in conocimiento or "empezando" in conocimiento:
        nivel = "Principiante"
    elif "básic" in conocimiento or "basico" in conocimiento:  # con y sin tilde
        nivel = "Básico"
    elif "me defiendo" in conocimiento or "intermedio" in conocimiento:
        nivel = "Intermedio"
    else:
        nivel = "Avanzado"

    # Pregunta 3 - Aprendizajes deseados (multi-opción separada por "||")
    seleccion_aprendizaje = respuestas[2].split("||")
    for opcion in seleccion_aprendizaje:
        if "ahorrar" in opcion.lower():
            aprendizajes.add("Ahorrar de manera eficiente")
        if "inflación" in opcion.lower():
            aprendizajes.add("Proteger tus ahorros")
        if "invertir" in opcion.lower():
            aprendizajes.add("Iniciar en las inversiones")
        if "criptomoneda" in opcion.lower():
            aprendizajes.add("Entender las criptomonedas")
        if "estafa" in opcion.lower():
            aprendizajes.add("Evitar estafas")

    # Pregunta 4 - Ingreso esperado
    ingreso = respuestas[3]
    if "Más de" in ingreso:
        aprendizajes.add("Inversión avanzada")
    elif "Otro" in ingreso:
        aprendizajes.add("Planificación personalizada")
    else:
        aprendizajes.add("Establecer metas realistas")

    # Pregunta 5 - Perfil de riesgo
    decision = respuestas[5]
    if "perder" in decision:
        riesgo = "Conservador"
    elif "Esperaría" in decision:
        riesgo = "Moderado"
    else:
        riesgo = "Arriesgado"

    # Pregunta 6 - Relación con el dinero
    mentalidad = respuestas[4]
    if "ahorrar" in mentalidad or "gastos" in mentalidad:
        aprendizajes.add("Gestionar tu dinero")
    if "ansiedad" in mentalidad:
        aprendizajes.add("Inteligencia emocional financiera")

    # Pregunta 7 - Frecuencia de ahorro
    ahorro = respuestas[6]
    if ahorro == "Casi nunca":
        aprendizajes.add("Construir hábitos financieros")
    elif ahorro == "Tengo un plan claro de ahorro":
        aprendizajes.add("Optimizar tu plan de ahorro")

    # Pregunta 8 - Deudas
    deuda = respuestas[7]
    if deuda == "Sí, y me preocupa":
        aprendizajes.add("Salir de deudas")
    elif deuda == "Sí, pero la tengo controlada":
        aprendizajes.add("Manejo responsable de deudas")

    # Pregunta 9 - Conversaciones sobre dinero
    dialogo = respuestas[8]
    if dialogo == "Nunca, me incomoda":
        aprendizajes.add("Hablar de finanzas con confianza")

    # Pregunta 10 - Uso de dinero inesperado
    reaccion = respuestas[9]
    if reaccion == "Lo gasto en algo que quiero":
        aprendizajes.add("Priorizar tus finanzas")
    elif reaccion == "Lo invierto buscando hacerlo crecer":
        aprendizajes.add("Invertir estratégicamente")

    # Pregunta 11 - Obstáculo
    obstaculo = respuestas[10]
    if "empezar" in obstaculo.lower():
        aprendizajes.add("Primeros pasos financieros")
    if "disciplina" in obstaculo.lower():
        aprendizajes.add("Establecer metas claras")
    if "miedo" in obstaculo.lower():
        aprendizajes.add("Superar el miedo a invertir")

    return Resultados(
        nivel_conocimiento=nivel,
        perfil_riesgo=riesgo,
        objetivo=objetivo,
        aprendizajes=sorted(aprendizajes),
        respuesta_ia=""  # pendiente implementar
    )
