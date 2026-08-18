import sqlite3

from fastapi import APIRouter, HTTPException, status

from database import obtener_conexion
from schemas import LoginRequest, RegistroUsuario, TokenResponse, UsuarioSalida
from seguridad import crear_token_acceso, hash_password, verificar_password

router = APIRouter(prefix="/auth", tags=["Autenticación"])


@router.post("/registro", response_model=UsuarioSalida, status_code=status.HTTP_201_CREATED)
def registrar_usuario(data: RegistroUsuario):
    conexion = obtener_conexion()
    try:
        cursor = conexion.execute(
            """
            INSERT INTO usuario (nombre, email, password_hash, telefono, rol)
            VALUES (?, ?, ?, ?, 'cliente')
            """,
            (data.nombre.strip(), data.email.lower(), hash_password(data.password), data.telefono),
        )
        conexion.commit()
        row = conexion.execute(
            "SELECT id, nombre, email, telefono, rol, activo FROM usuario WHERE id = ?",
            (cursor.lastrowid,),
        ).fetchone()
        return dict(row)
    except sqlite3.IntegrityError:
        conexion.rollback()
        raise HTTPException(status_code=400, detail="El correo ya está registrado")
    finally:
        conexion.close()


@router.post("/login", response_model=TokenResponse)
def login(data: LoginRequest):
    conexion = obtener_conexion()
    try:
        row = conexion.execute(
            "SELECT id, email, password_hash, rol, activo FROM usuario WHERE email = ?",
            (data.email.lower(),),
        ).fetchone()
        if not row or not row["activo"] or not verificar_password(data.password, row["password_hash"]):
            raise HTTPException(status_code=401, detail="Correo o contraseña incorrectos")
        token = crear_token_acceso(row["id"], row["email"], row["rol"])
        return {"access_token": token, "token_type": "bearer"}
    finally:
        conexion.close()
