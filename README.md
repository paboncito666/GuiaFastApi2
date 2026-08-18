# RopaExpress API REST

Backend académico para la actividad de ADSO: **Construcción de servicios web (API REST) para una plataforma de comercio electrónico**.

## Tecnologías

- Python 3.10+
- FastAPI
- Uvicorn
- SQLite
- Pydantic
- JWT con PyJWT
- bcrypt

## Estructura

```text
RopaExpress_API/
├── main.py
├── database.py
├── seguridad.py
├── schemas.py
├── modelos.py
├── requirements.txt
├── .env.example
├── .gitignore
├── README.md
└── routers/
    ├── auth.py
    ├── usuarios.py
    ├── categorias.py
    ├── tallas.py
    ├── colores.py
    ├── productos.py
    ├── inventario.py
    └── pedidos.py
```

## Modelo implementado

Se implementan las entidades de la documentación: Cliente/Usuario, Producto, Categoría, Talla, Color, Inventario, Pedido y DetallePedido. Se usa `Usuario` para resolver los requisitos de registro, login y roles.

La regla de inventario es `UNIQUE(producto_id, talla_id, color_id)`, lo que evita duplicar una combinación exacta de variante.

## Instalación en Windows / VS Code

### 1. Crear y activar entorno virtual

PowerShell:

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

CMD:

```cmd
python -m venv venv
venv\Scripts\activate
```

### 2. Instalar dependencias

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### 3. Variables de entorno

Copia `.env.example` como `.env` y cambia la clave JWT. Para la actividad también puedes trabajar con los valores locales incluidos.

### 4. Ejecutar

```bash
uvicorn main:app --reload
```

La API queda disponible en:

- `http://127.0.0.1:8000`
- Swagger: `http://127.0.0.1:8000/docs`
- ReDoc: `http://127.0.0.1:8000/redoc`

La base `ropaexpress.db` se crea automáticamente al iniciar la aplicación.

## Usuario administrador por defecto

```text
Correo: admin@ropaexpress.com
Contraseña: Admin123*
Rol: admin
```

**Cambia estas credenciales para cualquier uso fuera de la demostración académica.**

## Flujo rápido de prueba

### 1. Registrar cliente

`POST /auth/registro`

```json
{
  "nombre": "Laura Gomez",
  "email": "laura@example.com",
  "password": "Cliente123*",
  "telefono": "3001234567"
}
```

### 2. Login

`POST /auth/login`

```json
{
  "email": "laura@example.com",
  "password": "Cliente123*"
}
```

Copia `access_token` y pulsa **Authorize** en Swagger. Escribe:

```text
Bearer TU_TOKEN
```

### 3. Probar catálogo público

- `GET /productos`
- `GET /categorias`
- `GET /productos/1/inventario`

### 4. Probar operación de administrador

Inicia sesión con el administrador y prueba:

- `POST /productos`
- `DELETE /productos/{id}`
- `GET /usuarios`

Con un cliente normal, las operaciones restringidas devuelven **403**.

## Endpoints principales

| Método | Ruta | Protección |
|---|---|---|
| POST | `/auth/registro` | Público |
| POST | `/auth/login` | Público |
| GET | `/productos` | Público |
| GET | `/productos/{id}` | Público |
| GET | `/productos/{id}/inventario` | Público |
| POST | `/productos` | Vendedor/Admin |
| PUT | `/productos/{id}` | Vendedor/Admin |
| DELETE | `/productos/{id}` | Admin |
| GET | `/categorias` | Público |
| POST | `/categorias` | Vendedor/Admin |
| DELETE | `/categorias/{id}` | Admin |
| GET | `/inventario` | Público |
| POST | `/inventario` | Vendedor/Admin |
| PUT | `/inventario/{id}` | Vendedor/Admin |
| DELETE | `/inventario/{id}` | Admin |
| POST | `/pedidos` | Autenticado |
| GET | `/pedidos/mios` | Autenticado |
| GET | `/pedidos/{id}` | Autenticado |
| PATCH | `/pedidos/{id}/estado` | Vendedor/Admin |

## Requisitos de la guía cubiertos

- Entorno virtual `venv`.
- `requirements.txt`.
- `.gitignore` con `venv/`, `__pycache__/`, `*.db` y `.env`.
- SQLite con `check_same_thread=False` y `sqlite3.Row`.
- `crear_tablas()` y `sembrar_datos()`.
- Validación Pydantic.
- bcrypt para contraseñas.
- JWT para autenticación.
- Respuestas `400`, `401`, `403` y `404`.
- Consultas SQL parametrizadas con `?`.
- `commit()` y cierre de conexiones.
- CRUD para entidades principales y dependientes.
- Validación previa de existencia de la entidad principal.
- Bloqueo por integridad referencial.
- JOIN para obtener inventario de un producto.
- `lifespan` en `main.py`.

## Historial Git

El archivo entregado incluye un repositorio Git local con 5 commits descriptivos. Después de crear tu repositorio en GitHub puedes configurar el remoto y subir la rama principal.

```bash
git remote add origin https://github.com/TU-USUARIO/RopaExpress_API.git
git branch -M main
git push -u origin main
```

## Pruebas manuales sugeridas

1. Abrir `/docs`.
2. Registrar un cliente.
3. Iniciar sesión como cliente.
4. Intentar crear producto y comprobar `403`.
5. Iniciar sesión como admin.
6. Crear producto.
7. Crear inventario con una combinación talla/color.
8. Consultar `/productos/{id}/inventario`.
9. Crear un pedido con stock suficiente.
10. Volver a consultar inventario y comprobar que el stock disminuyó.

