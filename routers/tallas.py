import sqlite3
from fastapi import APIRouter, Depends, HTTPException, status
from database import obtener_conexion
from schemas import TallaActualizar, TallaCrear, TallaSalida
from seguridad import requiere_roles

router = APIRouter(prefix="/tallas", tags=["Tallas"])

@router.get("", response_model=list[TallaSalida])
def listar():
    conexion = obtener_conexion()
    try:
        return [dict(r) for r in conexion.execute("SELECT id, nombre FROM talla ORDER BY id").fetchall()]
    finally:
        conexion.close()

@router.get("/{talla_id}", response_model=TallaSalida)
def obtener(talla_id: int):
    conexion = obtener_conexion()
    try:
        row = conexion.execute("SELECT id, nombre FROM talla WHERE id = ?", (talla_id,)).fetchone()
        if not row: raise HTTPException(status_code=404, detail="Talla no encontrada")
        return dict(row)
    finally: conexion.close()

@router.post("", response_model=TallaSalida, status_code=status.HTTP_201_CREATED)
def crear(data: TallaCrear, _=Depends(requiere_roles("admin", "vendedor"))):
    conexion = obtener_conexion()
    try:
        cursor = conexion.execute("INSERT INTO talla (nombre) VALUES (?)", (data.nombre.upper(),))
        conexion.commit()
        return dict(conexion.execute("SELECT id, nombre FROM talla WHERE id = ?", (cursor.lastrowid,)).fetchone())
    except sqlite3.IntegrityError:
        conexion.rollback(); raise HTTPException(status_code=400, detail="La talla ya existe")
    finally: conexion.close()

@router.put("/{talla_id}", response_model=TallaSalida)
def actualizar(talla_id: int, data: TallaActualizar, _=Depends(requiere_roles("admin", "vendedor"))):
    conexion = obtener_conexion()
    try:
        cursor = conexion.execute("UPDATE talla SET nombre = ? WHERE id = ?", (data.nombre.upper(), talla_id))
        if cursor.rowcount == 0: raise HTTPException(status_code=404, detail="Talla no encontrada")
        conexion.commit()
        return dict(conexion.execute("SELECT id, nombre FROM talla WHERE id = ?", (talla_id,)).fetchone())
    except sqlite3.IntegrityError:
        conexion.rollback(); raise HTTPException(status_code=400, detail="La talla ya existe")
    finally: conexion.close()

@router.delete("/{talla_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar(talla_id: int, _=Depends(requiere_roles("admin"))):
    conexion = obtener_conexion()
    try:
        if conexion.execute("SELECT 1 FROM inventario WHERE talla_id = ? LIMIT 1", (talla_id,)).fetchone():
            raise HTTPException(status_code=400, detail="No se puede eliminar: talla en uso")
        cursor = conexion.execute("DELETE FROM talla WHERE id = ?", (talla_id,))
        if cursor.rowcount == 0: raise HTTPException(status_code=404, detail="Talla no encontrada")
        conexion.commit()
    finally: conexion.close()
