from fastapi import APIRouter, Depends, HTTPException
from database import obtener_conexion
from schemas import UsuarioSalida
from seguridad import obtener_usuario_actual, requiere_roles

router = APIRouter(prefix="/usuarios", tags=["Usuarios"])

@router.get("/me", response_model=UsuarioSalida)
def mi_usuario(usuario=Depends(obtener_usuario_actual)):
    conexion = obtener_conexion()
    try:
        row = conexion.execute(
            "SELECT id, nombre, email, telefono, rol, activo FROM usuario WHERE id = ?",
            (usuario["id"],),
        ).fetchone()
        if not row: raise HTTPException(status_code=404, detail="Usuario no encontrado")
        return dict(row)
    finally: conexion.close()

@router.get("", response_model=list[UsuarioSalida])
def listar_usuarios(_=Depends(requiere_roles("admin"))):
    conexion = obtener_conexion()
    try:
        return [dict(r) for r in conexion.execute("SELECT id, nombre, email, telefono, rol, activo FROM usuario ORDER BY id").fetchall()]
    finally: conexion.close()
