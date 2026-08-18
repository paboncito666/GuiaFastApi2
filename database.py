import os
import sqlite3

from dotenv import load_dotenv

load_dotenv()
from pathlib import Path

from seguridad import hash_password

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / os.getenv("DATABASE_FILE", "ropaexpress.db")


def obtener_conexion() -> sqlite3.Connection:
    """Abre SQLite con acceso seguro para FastAPI y filas tipo diccionario."""
    conexion = sqlite3.connect(DB_PATH, check_same_thread=False)
    conexion.row_factory = sqlite3.Row
    conexion.execute("PRAGMA foreign_keys = ON")
    return conexion


def crear_tablas() -> None:
    """Crea el modelo relacional completo definido para RopaExpress.

    Aunque la guía mínima habla de tres tablas, este proyecto implementa el
    modelo de datos de la documentación: 8 entidades + Usuario para autenticación.
    """
    conexion = obtener_conexion()
    cursor = conexion.cursor()
    cursor.executescript(
        """
        CREATE TABLE IF NOT EXISTS usuario (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL,
            telefono TEXT,
            rol TEXT NOT NULL DEFAULT 'cliente'
                CHECK (rol IN ('admin', 'vendedor', 'cliente')),
            activo INTEGER NOT NULL DEFAULT 1 CHECK (activo IN (0, 1))
        );

        CREATE TABLE IF NOT EXISTS categoria (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL UNIQUE,
            descripcion TEXT
        );

        CREATE TABLE IF NOT EXISTS producto (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            descripcion TEXT,
            precio REAL NOT NULL CHECK (precio >= 0),
            categoria_id INTEGER NOT NULL,
            FOREIGN KEY (categoria_id) REFERENCES categoria(id)
        );

        CREATE TABLE IF NOT EXISTS talla (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL UNIQUE
        );

        CREATE TABLE IF NOT EXISTS color (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL UNIQUE,
            codigo_hex TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS inventario (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            producto_id INTEGER NOT NULL,
            talla_id INTEGER NOT NULL,
            color_id INTEGER NOT NULL,
            cantidad_disponible INTEGER NOT NULL DEFAULT 0 CHECK (cantidad_disponible >= 0),
            UNIQUE(producto_id, talla_id, color_id),
            FOREIGN KEY (producto_id) REFERENCES producto(id),
            FOREIGN KEY (talla_id) REFERENCES talla(id),
            FOREIGN KEY (color_id) REFERENCES color(id)
        );

        CREATE TABLE IF NOT EXISTS pedido (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cliente_id INTEGER NOT NULL,
            fecha TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            estado TEXT NOT NULL DEFAULT 'pendiente'
                CHECK (estado IN ('pendiente', 'confirmado', 'enviado', 'entregado', 'cancelado')),
            total REAL NOT NULL DEFAULT 0 CHECK (total >= 0),
            FOREIGN KEY (cliente_id) REFERENCES usuario(id)
        );

        CREATE TABLE IF NOT EXISTS detalle_pedido (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            pedido_id INTEGER NOT NULL,
            inventario_id INTEGER NOT NULL,
            cantidad INTEGER NOT NULL CHECK (cantidad > 0),
            precio_unitario REAL NOT NULL CHECK (precio_unitario >= 0),
            FOREIGN KEY (pedido_id) REFERENCES pedido(id) ON DELETE CASCADE,
            FOREIGN KEY (inventario_id) REFERENCES inventario(id)
        );
        """
    )
    conexion.commit()
    conexion.close()


def sembrar_datos() -> None:
    """Inserta datos de demostración y un administrador por defecto."""
    conexion = obtener_conexion()
    cursor = conexion.cursor()

    existe_usuario = cursor.execute("SELECT COUNT(*) AS total FROM usuario").fetchone()["total"]
    if existe_usuario == 0:
        cursor.execute(
            """
            INSERT INTO usuario (nombre, email, password_hash, telefono, rol)
            VALUES (?, ?, ?, ?, ?)
            """,
            ("Administrador RopaExpress", "admin@ropaexpress.com", hash_password("Admin123*"), "3000000000", "admin"),
        )

    if cursor.execute("SELECT COUNT(*) AS total FROM categoria").fetchone()["total"] == 0:
        cursor.executemany(
            "INSERT INTO categoria (nombre, descripcion) VALUES (?, ?)",
            [
                ("Camisetas", "Prendas superiores casuales"),
                ("Pantalones", "Pantalones para diferentes estilos"),
                ("Buzos", "Prendas para clima frío"),
            ],
        )

    if cursor.execute("SELECT COUNT(*) AS total FROM talla").fetchone()["total"] == 0:
        cursor.executemany(
            "INSERT INTO talla (nombre) VALUES (?)",
            [("S",), ("M",), ("L",), ("XL",)],
        )

    if cursor.execute("SELECT COUNT(*) AS total FROM color").fetchone()["total"] == 0:
        cursor.executemany(
            "INSERT INTO color (nombre, codigo_hex) VALUES (?, ?)",
            [("Negro", "#000000"), ("Blanco", "#FFFFFF"), ("Azul", "#1D4ED8")],
        )

    if cursor.execute("SELECT COUNT(*) AS total FROM producto").fetchone()["total"] == 0:
        categorias = {row["nombre"]: row["id"] for row in cursor.execute("SELECT id, nombre FROM categoria")}
        cursor.executemany(
            """
            INSERT INTO producto (nombre, descripcion, precio, categoria_id)
            VALUES (?, ?, ?, ?)
            """,
            [
                ("Camiseta Oversize", "Camiseta de algodón de corte amplio", 69900, categorias["Camisetas"]),
                ("Pantalón Cargo", "Pantalón cargo de uso urbano", 119900, categorias["Pantalones"]),
            ],
        )

    if cursor.execute("SELECT COUNT(*) AS total FROM inventario").fetchone()["total"] == 0:
        productos = {row["nombre"]: row["id"] for row in cursor.execute("SELECT id, nombre FROM producto")}
        tallas = {row["nombre"]: row["id"] for row in cursor.execute("SELECT id, nombre FROM talla")}
        colores = {row["nombre"]: row["id"] for row in cursor.execute("SELECT id, nombre FROM color")}
        registros = [
            (productos["Camiseta Oversize"], tallas["M"], colores["Negro"], 15),
            (productos["Camiseta Oversize"], tallas["L"], colores["Negro"], 8),
            (productos["Camiseta Oversize"], tallas["M"], colores["Blanco"], 10),
            (productos["Pantalón Cargo"], tallas["M"], colores["Azul"], 6),
        ]
        cursor.executemany(
            """
            INSERT INTO inventario (producto_id, talla_id, color_id, cantidad_disponible)
            VALUES (?, ?, ?, ?)
            """,
            registros,
        )

    conexion.commit()
    conexion.close()
