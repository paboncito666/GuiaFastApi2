import sqlite3

from fastapi import APIRouter, Depends, HTTPException, status

from database import obtener_conexion
from schemas import InventarioActualizar, InventarioCrear, InventarioSalida
from seguridad import requiere_roles

router = APIRouter(prefix="/inventario", tags=["Inventario"])


def _obtener_inventario(conexion: sqlite3.Connection, inventario_id: int):
    row = conexion.execute(
        """
        SELECT i.id, i.producto_id, i.talla_id, i.color_id,
               i.cantidad_disponible, t.nombre AS talla_nombre,
               c.nombre AS color_nombre, c.codigo_hex
        FROM inventario i
        JOIN talla t ON t.id = i.talla_id
        JOIN color c ON c.id = i.color_id
        WHERE i.id = ?
        """,
        (inventario_id,),
    ).fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Registro de inventario no encontrado")
    return dict(row)


@router.get("", response_model=list[InventarioSalida])
def listar_inventario():
    conexion = obtener_conexion()
    try:
        rows = conexion.execute(
            """
            SELECT i.id, i.producto_id, i.talla_id, i.color_id,
                   i.cantidad_disponible, t.nombre AS talla_nombre,
                   c.nombre AS color_nombre, c.codigo_hex
            FROM inventario i
            JOIN talla t ON t.id = i.talla_id
            JOIN color c ON c.id = i.color_id
            ORDER BY i.id DESC
            """
        ).fetchall()
        return [dict(row) for row in rows]
    finally:
        conexion.close()


@router.get("/{inventario_id}", response_model=InventarioSalida)
def obtener_inventario(inventario_id: int):
    conexion = obtener_conexion()
    try:
        return _obtener_inventario(conexion, inventario_id)
    finally:
        conexion.close()


@router.post("", response_model=InventarioSalida, status_code=status.HTTP_201_CREATED)
def crear_inventario(data: InventarioCrear, _=Depends(requiere_roles("admin", "vendedor"))):
    conexion = obtener_conexion()
    try:
        # Entidad principal: Producto. Se valida primero mediante SELECT.
        if not conexion.execute("SELECT 1 FROM producto WHERE id = ?", (data.producto_id,)).fetchone():
            raise HTTPException(status_code=400, detail="El producto principal no existe")
        if not conexion.execute("SELECT 1 FROM talla WHERE id = ?", (data.talla_id,)).fetchone():
            raise HTTPException(status_code=400, detail="La talla no existe")
        if not conexion.execute("SELECT 1 FROM color WHERE id = ?", (data.color_id,)).fetchone():
            raise HTTPException(status_code=400, detail="El color no existe")

        cursor = conexion.execute(
            """
            INSERT INTO inventario (producto_id, talla_id, color_id, cantidad_disponible)
            VALUES (?, ?, ?, ?)
            """,
            (data.producto_id, data.talla_id, data.color_id, data.cantidad_disponible),
        )
        conexion.commit()
        return _obtener_inventario(conexion, cursor.lastrowid)
    except sqlite3.IntegrityError:
        conexion.rollback()
        raise HTTPException(status_code=400, detail="Ya existe esa combinación Producto-Talla-Color")
    finally:
        conexion.close()


@router.put("/{inventario_id}", response_model=InventarioSalida)
def actualizar_inventario(inventario_id: int, data: InventarioActualizar, _=Depends(requiere_roles("admin", "vendedor"))):
    conexion = obtener_conexion()
    try:
        if not conexion.execute("SELECT 1 FROM talla WHERE id = ?", (data.talla_id,)).fetchone():
            raise HTTPException(status_code=400, detail="La talla no existe")
        if not conexion.execute("SELECT 1 FROM color WHERE id = ?", (data.color_id,)).fetchone():
            raise HTTPException(status_code=400, detail="El color no existe")
        cursor = conexion.execute(
            """
            UPDATE inventario
            SET talla_id = ?, color_id = ?, cantidad_disponible = ?
            WHERE id = ?
            """,
            (data.talla_id, data.color_id, data.cantidad_disponible, inventario_id),
        )
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Registro de inventario no encontrado")
        conexion.commit()
        return _obtener_inventario(conexion, inventario_id)
    except sqlite3.IntegrityError:
        conexion.rollback()
        raise HTTPException(status_code=400, detail="Ya existe esa combinación Producto-Talla-Color")
    finally:
        conexion.close()


@router.delete("/{inventario_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_inventario(inventario_id: int, _=Depends(requiere_roles("admin"))):
    conexion = obtener_conexion()
    try:
        if conexion.execute("SELECT 1 FROM detalle_pedido WHERE inventario_id = ? LIMIT 1", (inventario_id,)).fetchone():
            raise HTTPException(status_code=400, detail="No se puede eliminar: el inventario tiene pedidos asociados")
        cursor = conexion.execute("DELETE FROM inventario WHERE id = ?", (inventario_id,))
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Registro de inventario no encontrado")
        conexion.commit()
    finally:
        conexion.close()
