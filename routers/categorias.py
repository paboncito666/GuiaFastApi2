import sqlite3

from fastapi import APIRouter, Depends, HTTPException, status

from database import obtener_conexion
from schemas import CategoriaActualizar, CategoriaCrear, CategoriaSalida
from seguridad import requiere_roles

router = APIRouter(prefix="/categorias", tags=["Categorías"])


@router.get("", response_model=list[CategoriaSalida])
def listar_categorias():
    conexion = obtener_conexion()
    try:
        rows = conexion.execute("SELECT id, nombre, descripcion FROM categoria ORDER BY nombre").fetchall()
        return [dict(row) for row in rows]
    finally:
        conexion.close()


@router.get("/{categoria_id}", response_model=CategoriaSalida)
def obtener_categoria(categoria_id: int):
    conexion = obtener_conexion()
    try:
        row = conexion.execute(
            "SELECT id, nombre, descripcion FROM categoria WHERE id = ?",
            (categoria_id,),
        ).fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Categoría no encontrada")
        return dict(row)
    finally:
        conexion.close()


@router.post("", response_model=CategoriaSalida, status_code=status.HTTP_201_CREATED)
def crear_categoria(data: CategoriaCrear, _=Depends(requiere_roles("admin", "vendedor"))):
    conexion = obtener_conexion()
    try:
        cursor = conexion.execute(
            "INSERT INTO categoria (nombre, descripcion) VALUES (?, ?)",
            (data.nombre.strip(), data.descripcion),
        )
        conexion.commit()
        return dict(conexion.execute("SELECT id, nombre, descripcion FROM categoria WHERE id = ?", (cursor.lastrowid,)).fetchone())
    except sqlite3.IntegrityError:
        conexion.rollback()
        raise HTTPException(status_code=400, detail="La categoría ya existe")
    finally:
        conexion.close()


@router.put("/{categoria_id}", response_model=CategoriaSalida)
def actualizar_categoria(categoria_id: int, data: CategoriaActualizar, _=Depends(requiere_roles("admin", "vendedor"))):
    conexion = obtener_conexion()
    try:
        cursor = conexion.execute(
            "UPDATE categoria SET nombre = ?, descripcion = ? WHERE id = ?",
            (data.nombre.strip(), data.descripcion, categoria_id),
        )
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Categoría no encontrada")
        conexion.commit()
        return dict(conexion.execute("SELECT id, nombre, descripcion FROM categoria WHERE id = ?", (categoria_id,)).fetchone())
    except sqlite3.IntegrityError:
        conexion.rollback()
        raise HTTPException(status_code=400, detail="No se puede duplicar el nombre de la categoría")
    finally:
        conexion.close()


@router.delete("/{categoria_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_categoria(categoria_id: int, _=Depends(requiere_roles("admin"))):
    conexion = obtener_conexion()
    try:
        dependientes = conexion.execute("SELECT 1 FROM producto WHERE categoria_id = ? LIMIT 1", (categoria_id,)).fetchone()
        if dependientes:
            raise HTTPException(status_code=400, detail="No se puede eliminar: la categoría tiene productos asociados")
        cursor = conexion.execute("DELETE FROM categoria WHERE id = ?", (categoria_id,))
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Categoría no encontrada")
        conexion.commit()
    finally:
        conexion.close()
