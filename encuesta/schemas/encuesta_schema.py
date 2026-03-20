from pydantic import BaseModel
from typing import Any, Dict, List, Optional, Union

# ✅ Respuesta que el backend le devuelve a la app
class Resultados(BaseModel):
    nivel_conocimiento: str
    perfil_riesgo: str
    objetivo: str
    aprendizajes: List[str]
    respuesta_ia: Optional[str] = ""


# ✅ Entrada que recibe el backend desde la app.
# Acepta dos formatos:
#   - List[str]: encuesta original (13 respuestas posicionales)
#   - Dict[str, Any]: Encuesta2 (respuestas con claves preg_1, preg_2, …)
class RespuestaEncuesta(BaseModel):
    respuestas: Union[List[str], Dict[str, Any]]
    usuario_id: Optional[int] = None
