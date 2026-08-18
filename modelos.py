"""Modelos de dominio ligeros usados por los routers y para documentación."""

from dataclasses import dataclass


@dataclass(frozen=True)
class Usuario:
    id: int
    nombre: str
    email: str
    rol: str


@dataclass(frozen=True)
class Producto:
    id: int
    nombre: str
    descripcion: str | None
    precio: float
    categoria_id: int


@dataclass(frozen=True)
class Categoria:
    id: int
    nombre: str
    descripcion: str | None


@dataclass(frozen=True)
class Inventario:
    id: int
    producto_id: int
    talla_id: int
    color_id: int
    cantidad_disponible: int
