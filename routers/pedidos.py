import sqlite3

from fastapi import APIRouter, Depends, HTTPException, status

from database import obtener_conexion
from schemas import EstadoPedidoActualizar, PedidoCrear, PedidoSalida
from seguridad import obtener_usuario_actual, requiere_roles

router = APIRouter(prefix="/pedidos", tags=["Pedidos"])


def _obtener_pedido(conexion: sqlite3.Connection, pedido_id: int):
    pedido = conexion.execute(
        "SELECT id, cliente_id, fecha, estado, total FROM pedido WHERE id = ?",
        (pedido_id,),
    ).fetchone()
    if not pedido:
        raise HTTPException(status_code=404, detail="Pedido no encontrado")
    detalles = conexion.execute(
        """
        SELECT id, inventario_id, cantidad, precio_unitario
        FROM detalle_pedido
        WHERE pedido_id = ?
        ORDER BY id
        """,
        (pedido_id,),
    ).fetchall()
    resultado = dict(pedido)
    resultado["detalles"] = [dict(d) for d in detalles]
    return resultado


@router.post("", response_model=PedidoSalida, status_code=status.HTTP_201_CREATED)
def crear_pedido(data: PedidoCrear, usuario=Depends(obtener_usuario_actual)):
    conexion = obtener_conexion()
    try:
        cliente_id = usuario["id"]
        if usuario["rol"] in {"admin", "vendedor"} and data.cliente_id:
            cliente_id = data.cliente_id

        if not conexion.execute("SELECT 1 FROM usuario WHERE id = ? AND activo = 1", (cliente_id,)).fetchone():
            raise HTTPException(status_code=400, detail="El cliente no existe o está inactivo")

        subtotal = 0.0
        validaciones: list[tuple[int, int, float]] = []
        for detalle in data.detalles:
            row = conexion.execute(
                """
                SELECT i.id, i.cantidad_disponible, p.precio
                FROM inventario i JOIN producto p ON p.id = i.producto_id
                WHERE i.id = ?
                """,
                (detalle.inventario_id,),
            ).fetchone()
            if not row:
                raise HTTPException(status_code=400, detail=f"El inventario {detalle.inventario_id} no existe")
            if row["cantidad_disponible"] < detalle.cantidad:
                raise HTTPException(status_code=400, detail=f"Stock insuficiente para inventario {detalle.inventario_id}")
            subtotal += row["precio"] * detalle.cantidad
            validaciones.append((detalle.inventario_id, detalle.cantidad, row["precio"]))

        cursor = conexion.execute(
            "INSERT INTO pedido (cliente_id, estado, total) VALUES (?, 'pendiente', ?)",
            (cliente_id, subtotal),
        )
        pedido_id = cursor.lastrowid

        for inventario_id, cantidad, precio in validaciones:
            conexion.execute(
                """
                INSERT INTO detalle_pedido (pedido_id, inventario_id, cantidad, precio_unitario)
                VALUES (?, ?, ?, ?)
                """,
                (pedido_id, inventario_id, cantidad, precio),
            )
            conexion.execute(
                "UPDATE inventario SET cantidad_disponible = cantidad_disponible - ? WHERE id = ?",
                (cantidad, inventario_id),
            )

        conexion.commit()
        return _obtener_pedido(conexion, pedido_id)
    except sqlite3.IntegrityError:
        conexion.rollback()
        raise HTTPException(status_code=400, detail="No se pudo crear el pedido por integridad de datos")
    finally:
        conexion.close()


@router.get("/mios", response_model=list[PedidoSalida])
def mis_pedidos(usuario=Depends(obtener_usuario_actual)):
    conexion = obtener_conexion()
    try:
        if usuario["rol"] in {"admin", "vendedor"}:
            rows = conexion.execute("SELECT id FROM pedido ORDER BY id DESC").fetchall()
        else:
            rows = conexion.execute("SELECT id FROM pedido WHERE cliente_id = ? ORDER BY id DESC", (usuario["id"],)).fetchall()
        return [_obtener_pedido(conexion, row["id"]) for row in rows]
    finally:
        conexion.close()


@router.get("/{pedido_id}", response_model=PedidoSalida)
def obtener_pedido(pedido_id: int, usuario=Depends(obtener_usuario_actual)):
    conexion = obtener_conexion()
    try:
        pedido = _obtener_pedido(conexion, pedido_id)
        if usuario["rol"] == "cliente" and pedido["cliente_id"] != usuario["id"]:
            raise HTTPException(status_code=403, detail="No puedes consultar este pedido")
        return pedido
    finally:
        conexion.close()


@router.patch("/{pedido_id}/estado", response_model=PedidoSalida)
def actualizar_estado(pedido_id: int, data: EstadoPedidoActualizar, _=Depends(requiere_roles("admin", "vendedor"))):
    conexion = obtener_conexion()
    try:
        cursor = conexion.execute("UPDATE pedido SET estado = ? WHERE id = ?", (data.estado, pedido_id))
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Pedido no encontrado")
        conexion.commit()
        return _obtener_pedido(conexion, pedido_id)
    finally:
        conexion.close()
