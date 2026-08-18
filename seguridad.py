import os

from dotenv import load_dotenv

load_dotenv()
from datetime import datetime, timedelta, timezone
from typing import Any

import bcrypt
import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "ropaexpress-clave-local-cambiar-en-produccion")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
JWT_EXPIRATION_MINUTES = int(os.getenv("JWT_EXPIRATION_MINUTES", "60"))

bearer_scheme = HTTPBearer(auto_error=False)


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verificar_password(password: str, password_hash: str) -> bool:
    try:
        return bcrypt.checkpw(password.encode("utf-8"), password_hash.encode("utf-8"))
    except (ValueError, TypeError):
        return False


def crear_token_acceso(usuario_id: int, email: str, rol: str) -> str:
    ahora = datetime.now(timezone.utc)
    payload = {
        "sub": str(usuario_id),
        "email": email,
        "rol": rol,
        "iat": ahora,
        "exp": ahora + timedelta(minutes=JWT_EXPIRATION_MINUTES),
    }
    return jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)


def obtener_usuario_actual(
    credenciales: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
) -> dict[str, Any]:
    if not credenciales:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token requerido")

    try:
        payload = jwt.decode(
            credenciales.credentials,
            JWT_SECRET_KEY,
            algorithms=[JWT_ALGORITHM],
        )
        usuario_id = int(payload.get("sub", 0))
        if usuario_id <= 0:
            raise ValueError("sub inválido")
        return {
            "id": usuario_id,
            "email": payload.get("email"),
            "rol": payload.get("rol"),
        }
    except (jwt.ExpiredSignatureError, jwt.InvalidTokenError, ValueError):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token inválido o expirado")


def requiere_roles(*roles: str):
    def dependencia(usuario: dict[str, Any] = Depends(obtener_usuario_actual)):
        if usuario.get("rol") not in roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No tienes permisos para realizar esta operación",
            )
        return usuario

    return dependencia
