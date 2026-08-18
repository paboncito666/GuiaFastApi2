import sqlite3
from fastapi import APIRouter, Depends, HTTPException, status
from database import obtener_conexion
from schemas import ColorActualizar, ColorCrear, ColorSalida
from seguridad import requiere_roles

router = APIRouter(prefix="/colores", tags=["Colores"])

@router.get("", response_model=list[ColorSalida])
def listar():
    conexion = obtener_conexion()
    try:
        return [dict(r) for r in conexion.execute("SELECT id, nombre, codigo_hex FROM color ORDER BY id").fetchall()]
    finally: conexion.close()

@router.get("/{color_id}", response_model=ColorSalida)
def obtener(color_id: int):
    conexion = obtener_conexion()
    try:
        row = conexion.execute("SELECT id, nombre, codigo_hex FROM color WHERE id = ?", (color_id,)).fetchone()
        if not row: raise HTTPException(status_code=404, detail="Color no encontrado")
        return dict(row)
    finally: conexion.close()

@router.post("", response_model=ColorSalida, status_code=status.HTTP_201_CREATED)
def crear(data: ColorCrear, _=Depends(requiere_roles("admin", "vendedor"))):
    conexion = obtener_conexion()
    try:
        cursor = conexion.execute("INSERT INTO color (nombre, codigo_hex) VALUES (?, ?)", (data.nombre.strip(), data.codigo_hex.upper()))
        conexion.commit()
        return dict(conexion.execute("SELECT id, nombre, codigo_hex FROM color WHERE id = ?", (cursor.lastrowid,)).fetchone())
    except sqlite3.IntegrityError:
        conexion.rollback(); raise HTTPException(status_code=400, detail="El color ya existe")
    finally: conexion.close()

@router.put("/{color_id}", response_model=ColorSalida)
def actualizar(color_id: int, data: ColorActualizar, _=Depends(requiere_roles("admin", "vendedor"))):
    conexion = obtener_conexion()
    try:
        cursor = conexion.execute("UPDATE color SET nombre = ?, codigo_hex = ? WHERE id = ?", (data.nombre.strip(), data.codigo_hex.upper(), color_id))
        if cursor.rowcount == 0: raise HTTPException(status_code=404, detail="Color no encontrado")
        conexion.commit()
        return dict(conexion.execute("SELECT id, nombre, codigo_hex FROM color WHERE id = ?", (color_id,)).fetchone())
    except sqlite3.IntegrityError:
        conexion.rollback(); raise HTTPException(status_code=400, detail="El color ya existe")
    finally: conexion.close()

@router.delete("/{color_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar(color_id: int, _=Depends(requiere_roles("admin"))):
    conexion = obtener_conexion()
    try:
        if conexion.execute("SELECT 1 FROM inventario WHERE color_id = ? LIMIT 1", (color_id,)).fetchone():
            raise HTTPException(status_code=400, detail="No se puede eliminar: color en uso")
        cursor = conexion.execute("DELETE FROM color WHERE id = ?", (color_id,))
        if cursor.rowcount == 0: raise HTTPException(status_code=404, detail="Color no encontrado")
        conexion.commit()
    finally: conexion.close()
