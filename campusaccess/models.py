"""Modelo de una solicitud académica ficticia de acceso a recursos digitales."""
from dataclasses import dataclass, replace

ESTADOS = frozenset({"pendiente", "autorizada", "cerrada"})


@dataclass(frozen=True, slots=True)
class Solicitud:
    identificador: str
    usuario: str
    recurso: str
    minuto: int  # minutos desde medianoche; intervalo del día 0..1439
    estado: str = "pendiente"

    def __post_init__(self) -> None:
        if not self.identificador or not self.usuario or not self.recurso:
            raise ValueError("ID, usuario y recurso son obligatorios")
        if not 0 <= self.minuto < 1440:
            raise ValueError("El minuto debe estar entre 0 y 1439")
        if self.estado not in ESTADOS:
            raise ValueError(f"Estado inválido: {self.estado}")

    def con_estado(self, estado: str) -> "Solicitud":
        return replace(self, estado=estado)


def hora(minuto: int) -> str:
    return f"{minuto // 60:02d}:{minuto % 60:02d}"
