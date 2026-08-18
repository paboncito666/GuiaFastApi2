# Matriz de endpoints

| Módulo | Endpoint | Tipo de acceso |
|---|---|---|
| Auth | POST `/auth/registro` | Público |
| Auth | POST `/auth/login` | Público |
| Productos | GET `/productos` | Público |
| Productos | GET `/productos/{id}` | Público |
| Productos | POST `/productos` | Vendedor/Admin |
| Productos | PUT `/productos/{id}` | Vendedor/Admin |
| Productos | DELETE `/productos/{id}` | Admin |
| Productos | GET `/productos/{id}/inventario` | Público |
| Inventario | GET/POST/PUT/DELETE `/inventario` | Público para GET; protegido para escritura |
| Pedidos | POST `/pedidos` | Autenticado |
| Pedidos | GET `/pedidos/mios` | Autenticado |
| Pedidos | GET `/pedidos/{id}` | Autenticado |
| Pedidos | PATCH `/pedidos/{id}/estado` | Vendedor/Admin |
