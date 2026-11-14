"""Mini-métrica opcional: tabla hash encadenada de capacidad FIJA.

IMPORTANTE: mide esta tabla educativa, NO la capacidad interna de dict/set
(CPython no expone su tamaño de tabla con su API pública).
"""
from dataclasses import dataclass


def hash_estable(clave: str) -> int:
    """FNV-1a de 32 bits: reproducción independiente de PYTHONHASHSEED."""
    h = 2166136261
    for b in clave.encode("utf-8"):
        h = ((h ^ b) * 16777619) & 0xFFFFFFFF
    return h


@dataclass(frozen=True)
class ResultadoBusqueda:
    encontrada: bool
    pasos: int


class TablaHashEducativa:
    def __init__(self, capacidad: int = 53) -> None:
        if capacidad < 1:
            raise ValueError("Capacidad debe ser positiva")
        self.capacidad = capacidad
        self.cubetas: list[list[str]] = [[] for _ in range(capacidad)]
        self.n = 0

    def insertar(self, clave: str) -> None:
        cubeta = self.cubetas[hash_estable(clave) % self.capacidad]
        if clave not in cubeta:
            cubeta.append(clave)
            self.n += 1

    def buscar(self, clave: str) -> ResultadoBusqueda:
        cubeta = self.cubetas[hash_estable(clave) % self.capacidad]
        # Cada acceso a cubeta = 1 paso; cada comparación dentro = 1 paso.
        pasos = 1
        for elemento in cubeta:
            pasos += 1
            if elemento == clave:
                return ResultadoBusqueda(True, pasos)
        return ResultadoBusqueda(False, pasos)

    @property
    def alfa(self) -> float:
        return self.n / self.capacidad

    @property
    def colisiones_insercion(self) -> int:
        return sum(max(0, len(cubeta) - 1) for cubeta in self.cubetas)


def evaluar(tabla: TablaHashEducativa,
            existentes: list[str], ausentes: list[str]) -> dict[str, float | int]:
    r1 = [tabla.buscar(x) for x in existentes]
    r2 = [tabla.buscar(x) for x in ausentes]
    return {
        "n": tabla.n,
        "capacidad": tabla.capacidad,
        "alfa": round(tabla.alfa, 4),
        "colisiones": tabla.colisiones_insercion,
        "aciertos": sum(r.encontrada for r in r1),
        "fallos": sum(not r.encontrada for r in r2),
        "promedio_pasos_existentes": round(sum(r.pasos for r in r1)/len(r1), 2),
        "promedio_pasos_ausentes": round(sum(r.pasos for r in r2)/len(r2), 2),
        "promedio_pasos_total": round(sum(r.pasos for r in r1+r2)/(len(r1)+len(r2)), 2),
    }
