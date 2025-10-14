from pydantic import BaseModel
from typing import List, Optional

# ✅ Entrada que recibe el backend desde la app
class RespuestaEncuesta(BaseModel):
    respuestas: List[str]

# ✅ Respuesta que el backend le devuelve a la app
class Resultados(BaseModel):
    nivel_conocimiento: str
    perfil_riesgo: str
    objetivo: str
    aprendizajes: List[str]
    respuesta_ia: Optional[str] = ""
    

class RespuestaEncuesta(BaseModel):
    respuestas: List[str]
    usuario_id: Optional[int] = None 
