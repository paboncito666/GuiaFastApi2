from dotenv import load_dotenv
load_dotenv()

from contextlib import asynccontextmanager

from fastapi import FastAPI

from database import crear_tablas, sembrar_datos
from routers import auth, categorias, colores, inventario, pedidos, productos, tallas, usuarios


@asynccontextmanager
async def lifespan(app: FastAPI):
    crear_tablas()
    sembrar_datos()
    yield


app = FastAPI(
    title="RopaExpress API REST",
    description=(
        "Backend para una plataforma de comercio electrónico de ropa. "
        "Gestiona catálogo, inventario por talla/color, clientes, pedidos y seguridad con JWT."
    ),
    version="1.0.0",
    lifespan=lifespan,
)

app.include_router(auth.router)
app.include_router(usuarios.router)
app.include_router(categorias.router)
app.include_router(tallas.router)
app.include_router(colores.router)
app.include_router(productos.router)
app.include_router(inventario.router)
app.include_router(pedidos.router)


@app.get("/", tags=["Sistema"])
def inicio():
    return {
        "proyecto": "RopaExpress",
        "mensaje": "API REST funcionando correctamente",
        "documentacion": "/docs",
    }


@app.get("/health", tags=["Sistema"])
def health():
    return {"status": "ok"}
