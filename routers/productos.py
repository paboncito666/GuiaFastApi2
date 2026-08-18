import sqlite3

from fastapi import APIRouter, Depends, HTTPException, status

from database import obtener_conexion
from schemas import InventarioSalida, ProductoActualizar, ProductoCrear, ProductoSalida
from seguridad import requiere_roles

router = APIRouter(prefix="/productos", tags=["Productos"])


@router.get("", response_model=list[ProductoSalida])
def listar_productos():
    conexion = obtener_conexion()
    try:
        rows = conexion.execute(
            """
            SELECT p.id, p.nombre, p.descripcion, p.precio, p.categoria_id, c.nombre AS categoria_nombre
            FROM producto p JOIN categoria c ON c.id = p.categoria_id
            ORDER BY p.id DESC
            """
        ).fetchall()
        return [dict(row) for row in rows]
    finally:
        conexion.close()


@router.get("/{producto_id}", response_model=ProductoSalida)
def obtener_producto(producto_id: int):
    conexion = obtener_conexion()
    try:
        row = conexion.execute(
            """
            SELECT p.id, p.nombre, p.descripcion, p.precio, p.categoria_id, c.nombre AS categoria_nombre
            FROM producto p JOIN categoria c ON c.id = p.categoria_id
            WHERE p.id = ?
            """,
            (producto_id,),
        ).fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Producto no encontrado")
        return dict(row)
    finally:
        conexion.close()


@router.get("/{producto_id}/inventario", response_model=list[InventarioSalida])
def inventario_por_producto(producto_id: int):
    conexion = obtener_conexion()
    try:
        existe = conexion.execute("SELECT 1 FROM producto WHERE id = ?", (producto_id,)).fetchone()
        if not existe:
            raise HTTPException(status_code=404, detail="Producto no encontrado")

        # Consulta con JOIN en una sola sentencia para devolver las variantes.
        rows = conexion.execute(
            """
            SELECT i.id, i.producto_id, i.talla_id, i.color_id,
                   i.cantidad_disponible, t.nombre AS talla_nombre,
                   c.nombre AS color_nombre, c.codigo_hex
            FROM inventario i
            JOIN talla t ON t.id = i.talla_id
            JOIN color c ON c.id = i.color_id
            WHERE i.producto_id = ?
            ORDER BY t.id, c.id
            """,
            (producto_id,),
        ).fetchall()
        return [dict(row) for row in rows]
    finally:
        conexion.close()


@router.post("", response_model=ProductoSalida, status_code=status.HTTP_201_CREATED)
def crear_producto(data: ProductoCrear, _=Depends(requiere_roles("admin", "vendedor"))):
    conexion = obtener_conexion()
    try:
        if not conexion.execute("SELECT 1 FROM categoria WHERE id = ?", (data.categoria_id,)).fetchone():
            raise HTTPException(status_code=400, detail="La categoría no existe")
        cursor = conexion.execute(
            "INSERT INTO producto (nombre, descripcion, precio, categoria_id) VALUES (?, ?, ?, ?)",
            (data.nombre.strip(), data.descripcion, data.precio, data.categoria_id),
        )
        conexion.commit()
        row = conexion.execute(
            """
            SELECT p.id, p.nombre, p.descripcion, p.precio, p.categoria_id, c.nombre AS categoria_nombre
            FROM producto p JOIN categoria c ON c.id = p.categoria_id WHERE p.id = ?
            """,
            (cursor.lastrowid,),
        ).fetchone()
        return dict(row)
    finally:
        conexion.close()


@router.put("/{producto_id}", response_model=ProductoSalida)
def actualizar_producto(producto_id: int, data: ProductoActualizar, _=Depends(requiere_roles("admin", "vendedor"))):
    conexion = obtener_conexion()
    try:
        if not conexion.execute("SELECT 1 FROM categoria WHERE id = ?", (data.categoria_id,)).fetchone():
            raise HTTPException(status_code=400, detail="La categoría no existe")
        cursor = conexion.execute(
            """
            UPDATE producto
            SET nombre = ?, descripcion = ?, precio = ?, categoria_id = ?
            WHERE id = ?
            """,
            (data.nombre.strip(), data.descripcion, data.precio, data.categoria_id, producto_id),
        )
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Producto no encontrado")
        conexion.commit()
        row = conexion.execute(
            """
            SELECT p.id, p.nombre, p.descripcion, p.precio, p.categoria_id, c.nombre AS categoria_nombre
            FROM producto p JOIN categoria c ON c.id = p.categoria_id WHERE p.id = ?
            """,
            (producto_id,),
        ).fetchone()
        return dict(row)
    finally:
        conexion.close()


@router.delete("/{producto_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_producto(producto_id: int, _=Depends(requiere_roles("admin"))):
    conexion = obtener_conexion()
    try:
        if conexion.execute("SELECT 1 FROM inventario WHERE producto_id = ? LIMIT 1", (producto_id,)).fetchone():
            raise HTTPException(status_code=400, detail="No se puede eliminar: el producto tiene inventario asociado")
        cursor = conexion.execute("DELETE FROM producto WHERE id = ?", (producto_id,))
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Producto no encontrado")
        conexion.commit()
    except sqlite3.IntegrityError:
        conexion.rollback()
        raise HTTPException(status_code=400, detail="No se puede eliminar el producto por integridad referencial")
    finally:
        conexion.close()
