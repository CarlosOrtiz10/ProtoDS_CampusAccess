"""Módulo B: árbol AVL con rango semiabierto [a,b) y claves compuestas.

Se ordena por (minuto, identificador) para conservar solicitudes que
comparten horario sin sobrescribirlas. El AVL es auto-balanceado.
"""
from __future__ import annotations
from dataclasses import dataclass
from .models import Solicitud


@dataclass(slots=True)
class _Nodo:
    clave: tuple[int, str]
    solicitud: Solicitud
    izq: _Nodo | None = None
    der: _Nodo | None = None
    altura: int = 1


def _altura(n: _Nodo | None) -> int:
    return n.altura if n else 0


def _actualizar(n: _Nodo) -> None:
    n.altura = 1 + max(_altura(n.izq), _altura(n.der))


def _rotar_derecha(y: _Nodo) -> _Nodo:
    x = y.izq
    assert x is not None
    z = x.der
    x.der = y
    y.izq = z
    _actualizar(y)
    _actualizar(x)
    return x


def _rotar_izquierda(x: _Nodo) -> _Nodo:
    y = x.der
    assert y is not None
    z = y.izq
    y.izq = x
    x.der = z
    _actualizar(x)
    _actualizar(y)
    return y


class AgendaAVL:
    def __init__(self) -> None:
        self._raiz: _Nodo | None = None
        self._cantidad = 0
        self._ids: set[str] = set()

    def insertar(self, solicitud: Solicitud) -> None:
        if solicitud.identificador in self._ids:
            raise ValueError("El ID ya está indexado en el AVL")
        clave = (solicitud.minuto, solicitud.identificador)

        def rec(n: _Nodo | None) -> _Nodo:
            if n is None:
                return _Nodo(clave, solicitud)
            if clave < n.clave:
                n.izq = rec(n.izq)
            elif clave > n.clave:
                n.der = rec(n.der)
            else:
                raise ValueError("Clave del árbol duplicada")
            _actualizar(n)
            balance = _altura(n.izq) - _altura(n.der)
            if balance > 1:
                assert n.izq is not None
                if clave > n.izq.clave:
                    n.izq = _rotar_izquierda(n.izq)
                return _rotar_derecha(n)
            if balance < -1:
                assert n.der is not None
                if clave < n.der.clave:
                    n.der = _rotar_derecha(n.der)
                return _rotar_izquierda(n)
            return n

        self._raiz = rec(self._raiz)
        self._cantidad += 1
        self._ids.add(solicitud.identificador)

    def actualizar_solicitud(self, solicitud: Solicitud) -> None:
        """Sincroniza cambios de estado/recurso sin alterar la clave temporal."""
        clave = (solicitud.minuto, solicitud.identificador)
        nodo = self._raiz
        while nodo is not None:
            if clave == nodo.clave:
                nodo.solicitud = solicitud
                return
            nodo = nodo.izq if clave < nodo.clave else nodo.der
        raise KeyError(f"Solicitud inexistente en la agenda: {solicitud.identificador}")

    def rango(self, desde: int, hasta: int) -> list[Solicitud]:
        if not 0 <= desde < hasta <= 1440:
            raise ValueError("El rango debe cumplir 0 <= desde < hasta <= 1440")
        salida: list[Solicitud] = []

        def rec(n: _Nodo | None) -> None:
            if n is None:
                return
            if n.clave[0] >= desde:
                rec(n.izq)
            if desde <= n.clave[0] < hasta:
                salida.append(n.solicitud)
            if n.clave[0] < hasta:
                rec(n.der)

        rec(self._raiz)
        return salida

    def minimo(self) -> Solicitud | None:
        n = self._raiz
        while n and n.izq:
            n = n.izq
        return n.solicitud if n else None

    def maximo(self) -> Solicitud | None:
        n = self._raiz
        while n and n.der:
            n = n.der
        return n.solicitud if n else None

    def __len__(self) -> int:
        return self._cantidad

    @property
    def altura(self) -> int:
        return _altura(self._raiz)

    def validar(self) -> bool:
        """Comprueba orden BST, altura y factor AVL a cada nivel."""
        def rec(n: _Nodo | None, menor: tuple[int, str] | None,
                mayor: tuple[int, str] | None) -> tuple[bool, int, int]:
            if n is None:
                return True, 0, 0
            if (menor is not None and n.clave <= menor) or (
                mayor is not None and n.clave >= mayor
            ):
                return False, 0, 0
            bi, hi, ci = rec(n.izq, menor, n.clave)
            bd, hd, cd = rec(n.der, n.clave, mayor)
            ok = bi and bd and abs(hi - hd) <= 1 and n.altura == max(hi, hd) + 1
            return ok, n.altura, ci + cd + 1
        correcto, _, cantidad = rec(self._raiz, None, None)
        return correcto and cantidad == self._cantidad and len(self._ids) == cantidad
