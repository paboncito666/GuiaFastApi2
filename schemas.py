from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator


class RegistroUsuario(BaseModel):
    nombre: str = Field(min_length=2, max_length=100)
    email: EmailStr
    password: str = Field(min_length=8, max_length=72)
    telefono: str | None = Field(default=None, max_length=20)


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=1, max_length=72)


class UsuarioSalida(BaseModel):
    id: int
    nombre: str
    email: EmailStr
    telefono: str | None
    rol: Literal["admin", "vendedor", "cliente"]
    activo: bool


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class CategoriaBase(BaseModel):
    nombre: str = Field(min_length=2, max_length=80)
    descripcion: str | None = Field(default=None, max_length=255)


class CategoriaCrear(CategoriaBase):
    pass


class CategoriaActualizar(CategoriaBase):
    pass


class CategoriaSalida(CategoriaBase):
    model_config = ConfigDict(from_attributes=True)
    id: int


class TallaBase(BaseModel):
    nombre: str = Field(min_length=1, max_length=10)


class TallaCrear(TallaBase):
    pass


class TallaActualizar(TallaBase):
    pass


class TallaSalida(TallaBase):
    id: int


class ColorBase(BaseModel):
    nombre: str = Field(min_length=2, max_length=50)
    codigo_hex: str = Field(pattern=r"^#[0-9A-Fa-f]{6}$")


class ColorCrear(ColorBase):
    pass


class ColorActualizar(ColorBase):
    pass


class ColorSalida(ColorBase):
    id: int


class ProductoBase(BaseModel):
    nombre: str = Field(min_length=2, max_length=120)
    descripcion: str | None = Field(default=None, max_length=500)
    precio: float = Field(ge=0)
    categoria_id: int = Field(gt=0)


class ProductoCrear(ProductoBase):
    pass


class ProductoActualizar(ProductoBase):
    pass


class ProductoSalida(ProductoBase):
    id: int
    categoria_nombre: str | None = None


class InventarioBase(BaseModel):
    producto_id: int = Field(gt=0)
    talla_id: int = Field(gt=0)
    color_id: int = Field(gt=0)
    cantidad_disponible: int = Field(ge=0)


class InventarioCrear(InventarioBase):
    pass


class InventarioActualizar(BaseModel):
    talla_id: int = Field(gt=0)
    color_id: int = Field(gt=0)
    cantidad_disponible: int = Field(ge=0)


class InventarioSalida(InventarioBase):
    id: int
    talla_nombre: str
    color_nombre: str
    codigo_hex: str


class PedidoCrear(BaseModel):
    cliente_id: int | None = Field(default=None, gt=0)
    detalles: list["DetallePedidoCrear"] = Field(min_length=1)


class DetallePedidoCrear(BaseModel):
    inventario_id: int = Field(gt=0)
    cantidad: int = Field(gt=0)


class DetallePedidoSalida(BaseModel):
    id: int
    inventario_id: int
    cantidad: int
    precio_unitario: float


class PedidoSalida(BaseModel):
    id: int
    cliente_id: int
    fecha: datetime
    estado: Literal["pendiente", "confirmado", "enviado", "entregado", "cancelado"]
    total: float
    detalles: list[DetallePedidoSalida]


class EstadoPedidoActualizar(BaseModel):
    estado: Literal["pendiente", "confirmado", "enviado", "entregado", "cancelado"]

