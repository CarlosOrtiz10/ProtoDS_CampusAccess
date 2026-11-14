"""Módulo A: mapa dict para acceso directo y set para existencia."""
from .models import Solicitud


class RegistroSolicitudes:
    def __init__(self) -> None:
        self._por_id: dict[str, Solicitud] = {}
        self._ids: set[str] = set()

    def insertar(self, solicitud: Solicitud) -> None:
        if solicitud.identificador in self._ids:
            raise ValueError(f"ID duplicado: {solicitud.identificador}")
        self._por_id[solicitud.identificador] = solicitud
        self._ids.add(solicitud.identificador)

    def consultar(self, identificador: str) -> Solicitud | None:
        return self._por_id.get(identificador)

    def existe(self, identificador: str) -> bool:
        return identificador in self._ids

    def actualizar_estado(self, identificador: str, estado: str) -> Solicitud:
        actual = self._por_id.get(identificador)
        if actual is None:
            raise KeyError(f"Solicitud inexistente: {identificador}")
        nuevo = actual.con_estado(estado)
        self._por_id[identificador] = nuevo
        return nuevo

    def __len__(self) -> int:
        return len(self._por_id)

    def solicitudes(self) -> list[Solicitud]:
        return list(self._por_id.values())

    def validar(self) -> bool:
        return self._ids == set(self._por_id)
