# Modelo de datos RopaExpress

```mermaid
erDiagram
    USUARIO ||--o{ PEDIDO : realiza
    PEDIDO ||--|{ DETALLE_PEDIDO : contiene
    INVENTARIO ||--o{ DETALLE_PEDIDO : referencia
    PRODUCTO ||--o{ INVENTARIO : posee
    CATEGORIA ||--o{ PRODUCTO : clasifica
    TALLA ||--o{ INVENTARIO : define
    COLOR ||--o{ INVENTARIO : define
```

## Decisión de diseño clave

`Inventario` representa la variante exacta de un producto mediante `producto_id + talla_id + color_id`. Esto permite mantener el producto como entidad de catálogo y controlar el stock sin duplicar el producto por cada combinación.
