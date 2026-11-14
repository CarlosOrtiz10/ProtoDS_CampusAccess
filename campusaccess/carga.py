"""Carga local determinista: no requiere credenciales ni conexiones externas."""
import json
from pathlib import Path
from .models import Solicitud
from .registro import RegistroSolicitudes
from .avl import AgendaAVL

DATOS = Path(__file__).resolve().parents[1] / "data" / "solicitudes.json"


def cargar_datos(ruta: Path = DATOS) -> list[Solicitud]:
    payload = json.loads(Path(ruta).read_text(encoding="utf-8"))
    if payload.get("escenario") != "CampusAccess-UCC-FICTICIO":
        raise ValueError("Escenario JSON no reconocido")
    return [Solicitud(**item) for item in payload["solicitudes"]]


def preparar_sistema() -> tuple[RegistroSolicitudes, AgendaAVL]:
    registro = RegistroSolicitudes()
    agenda = AgendaAVL()
    for s in cargar_datos():
        registro.insertar(s)
        agenda.insertar(s)
    return registro, agenda
