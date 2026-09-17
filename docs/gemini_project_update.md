# Actualizacion del proyecto Apex Nutrition

## Objetivo de este documento

Este documento resume el estado actual del proyecto para que otro asistente, especialmente Gemini, pueda continuar el desarrollo sin perder contexto ni repetir cambios.

## Producto

Apex Nutrition es un sistema de gestion para una marca dominicana de suplementos, enfocada en creatina en gomitas. El sistema cubre:

- Inventario por lotes.
- Control de productos y costos.
- Facturacion fiscal DGII mediante NCF.
- Entregas y logistica.
- Integracion con n8n para eventos omnicanal.
- Dashboard operativo en Streamlit.

La arquitectura es hexagonal:

- Driver de API: FastAPI.
- Driver de interfaz: Streamlit.
- Dominio: modelos y servicios de negocio.
- Adaptadores: Supabase y proveedores externos de rutas.

## Estructura relevante

```text
backend/app/
  main.py
  domain/models.py
  domain/services.py
  adapters/supa_base_repository.py
  adapters/database.py

dashboard/app.py
docs/supabase_venta_transaccional.sql
docs/supabase_delivery_coordinates.sql
```

## Cambios realizados en el backend

### Modelos de dominio

En `backend/app/domain/models.py`:

- `DeliveryCreate` acepta coordenadas opcionales del cliente:
  - `destino_lat`
  - `destino_lng`
- `distancia_km` puede calcularse automaticamente cuando existen coordenadas.
- `DeliveryQuoteRequest` recibe coordenadas de destino y, opcionalmente, coordenadas de origen.
- `DeliveryQuoteResponse` devuelve:
  - distancia en kilometros;
  - duracion estimada en minutos;
  - costo del envio en DOP;
  - proveedor usado.
- `DeliveryResponse` incluye coordenadas cuando existen.
- El flujo manual actual requiere una `venta_id` asociada. El cambio para permitir deliveries B2C sin venta fue revertido en la ultima iteracion.

### Servicio de entregas

En `backend/app/domain/services.py`:

- Se mantiene la regla de costos:
  - tarifa base: RD$ 150 para los primeros 3 km;
  - costo adicional: RD$ 35 por kilometro extra.
- El metodo `cotizar_ruta` usa esta prioridad:
  1. openrouteservice, si existe `OPENROUTESERVICE_API_KEY`;
  2. OSRM publico como respaldo sin API key.
- Google Maps fue eliminado del flujo de rutas.
- openrouteservice se consulta mediante `POST /v2/directions/driving-car`.
- OSRM se consulta mediante `https://router.project-osrm.org/route/v1/driving/...`.
- El resultado de distancia se usa para calcular el costo de entrega.

### API FastAPI

En `backend/app/main.py`:

- Se mantiene `POST /deliveries` para crear entregas.
- Si se envian coordenadas, la API calcula distancia y costo con `cotizar_ruta`.
- Si no se envian coordenadas, acepta `distancia_km` como alternativa manual.
- Se persiste la distancia calculada antes de insertar el delivery.
- Se agrego `POST /deliveries/cotizar` para devolver una cotizacion sin crear el delivery.
- Se mantiene `GET /ventas/{venta_id}/delivery`.
- Se mantiene `PATCH /deliveries/{delivery_id}/estado` para cambiar estados.
- Estados disponibles:
  - `PENDIENTE`
  - `EN_RUTA`
  - `ENTREGADO`
  - `CANCELADO`
- El endpoint de cambio de estado recibe el enum mediante query parameter `estado`.

### Repositorio Supabase

En `backend/app/adapters/supa_base_repository.py`:

- Los deliveries guardan `venta_id`, direccion, distancia, costo y estado.
- Si el delivery trae coordenadas, tambien guarda `destino_lat` y `destino_lng`.
- La asociacion con venta es obligatoria en el flujo actual.
- El ID principal del delivery lo genera Supabase.

## Cambios realizados en Supabase

### Funcion transaccional de ventas

`docs/supabase_venta_transaccional.sql` contiene una funcion PostgreSQL que:

- Registra la venta y sus detalles en una transaccion.
- Bloquea el lote con `FOR UPDATE`.
- Valida stock suficiente.
- Descuenta el inventario atomica y automaticamente.
- Marca el lote como `AGOTADO` cuando llega a cero.
- Devuelve codigo de factura, NCF, totales y fecha.
- Configura politicas anonimas para operaciones usadas por el dashboard.

### Coordenadas de deliveries

`docs/supabase_delivery_coordinates.sql` agrega a `public.deliveries`:

```sql
destino_lat double precision
destino_lng double precision
```

Tambien agrega validaciones de rango para latitud y longitud.

Esta migracion debe estar ejecutada en Supabase para que las nuevas entregas con coordenadas se guarden correctamente.

La migracion `supabase_b2c_deliveries.sql` ya no existe porque el flujo B2C sin venta asociada fue revertido.

## Configuracion de entorno

El archivo `.env` contiene variables de Supabase y de rutas. Nunca copiar valores secretos al prompt de Gemini ni subirlos al repositorio.

Variables esperadas:

```env
SUPABASE_URL="..."
SUPABASE_KEY="..."
OPENROUTESERVICE_API_KEY="..."
ROUTE_ORIGIN_LAT="..."
ROUTE_ORIGIN_LNG="..."
```

La ubicacion de origen actualmente configurada en el entorno corresponde a:

- Latitud: `18.4934`
- Longitud: `-69.9912`
- Referencia aproximada: Entrada IMCA, Villa Peravia, Santo Domingo Oeste, Republica Dominicana.

La API debe reiniciarse despues de cambiar el `.env` porque las variables se cargan al iniciar el proceso.

## Cambios visuales del dashboard

En `dashboard/app.py` se transformo el panel para que no parezca una tabla tecnica de Supabase.

### Estilo

- Tema oscuro con glassmorphism.
- Sidebar translucido con blur.
- Tarjetas de vidrio con bordes suaves.
- Botones activos y secundarios diferenciados.
- Layout responsive para pantallas estrechas.
- Estetica orientada a marca de suplementos y rendimiento.

### Navegacion

- Se elimino el dropdown principal.
- La navegacion usa botones directos en el sidebar:
  - Dashboard
  - Catalogo & Lotes
  - Facturacion DGII
  - Logistica
  - Webhooks n8n
- La seccion activa queda resaltada.

### Dashboard

El Dashboard ahora muestra:

- Ventas del mes.
- Proyeccion de cierre mensual basada en el promedio diario real.
- Dinero en stock calculado con unidades disponibles por precio de venta.
- Ganancia neta estimada.
- ITBIS acumulado.
- Unidades disponibles.
- Envíos pendientes.
- Grafica de acumulado real contra proyeccion.
- Tarjetas de ventas y despachos recientes.

La ganancia neta estimada usa la siguiente aproximacion:

```text
ingresos sin ITBIS - costo de produccion de unidades vendidas - costo de deliveries
```

Es una estimacion operativa, no un estado financiero auditado.

### Catalogo

- Se eliminaron tablas directas.
- Los lotes se muestran como tarjetas.
- Hay busqueda por lote o producto.
- Hay filtro por estado.
- Se mantiene el formulario para abrir un lote.

### Facturacion

- Se eliminaron tablas directas.
- Se muestran metricas y tarjetas de comprobantes.
- El selector visible usa nombres amigables:
  - `B02` se muestra como `Consumidor final`.
  - `B01` se muestra como `Empresas`.
- Internamente el payload sigue enviando `B02` y `B01` para cumplir DGII.
- Los comprobantes recientes traducen los codigos a esas etiquetas.

### Logistica

- Se eliminaron tablas directas.
- Las entregas aparecen como tarjetas.
- Se puede filtrar por estado.
- Cada entrega permite cambiar su estado.
- Cada entrega tiene boton `Vista mapa`.
- Si hay coordenadas, abre la ubicacion exacta en OpenStreetMap.
- Si no hay coordenadas, busca la direccion agregando Santo Domingo y Republica Dominicana para reducir ambiguedades.
- Hay una seccion para cotizar una ubicacion antes de crearla.
- Hay un formulario para crear una entrega manual en caso de falla de n8n.
- El formulario manual actual asocia la entrega a una venta existente usando un selector; el ID se obtiene automaticamente y no se escribe a mano.
- El formulario admite direccion, sector, receptor, telefono, coordenadas, distancia manual y notas.

### Webhooks n8n

- Los eventos se muestran como tarjetas.
- Se evita ordenar por `creado_en` cuando esa columna no existe.
- Si la tabla tiene alguna columna de fecha compatible, se ordena en memoria.

## Pruebas realizadas

Se verifico:

- Compilacion de Python con `py_compile` para backend y dashboard.
- Dashboard activo en `http://localhost:8501`.
- API activa en `http://127.0.0.1:8000`.
- Endpoint de cotizacion real usando openrouteservice.
- Fallback de rutas con OSRM.
- Vista Logistica sin errores.
- Cambio de estados desde el panel.
- Enlaces de OpenStreetMap.
- Formulario manual de entregas.
- Selector de tipos fiscales con las etiquetas amigables.

Ejemplo de respuesta validada del endpoint de cotizacion:

```json
{
  "distancia_km": 4.94,
  "duracion_minutos": 6,
  "costo_envio_dop": 217.9,
  "proveedor": "openrouteservice"
}
```

## Estado actual de los servicios

Para ejecutar el backend:

```powershell
.\venv\Scripts\python.exe -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000
```

Para ejecutar el dashboard:

```powershell
.\venv\Scripts\python.exe -m streamlit run dashboard\app.py --server.headless true --server.port 8501
```

## Pendientes y advertencias

1. Confirmar que `docs/supabase_delivery_coordinates.sql` fue ejecutado en el proyecto Supabase correcto.
2. Verificar que el checkout o n8n envia `destino_lat` y `destino_lng` al crear deliveries.
3. No exponer `SUPABASE_KEY` ni `OPENROUTESERVICE_API_KEY` en prompts, capturas, commits o frontend.
4. La busqueda textual de direcciones antiguas sigue siendo menos exacta que guardar coordenadas.
5. El servidor publico de OSRM es solo un respaldo para pruebas; para alto volumen debe usarse una instancia propia o un proveedor con limites conocidos.
6. El flujo manual actual requiere asociar una venta. Si se desea separar B2C de B2B en el futuro, primero debe revisarse la restriccion `venta_id` y la relacion en Supabase.
7. La ganancia neta del dashboard es una estimacion y no incluye otros gastos operativos, impuestos adicionales, devoluciones o comisiones de pago.

## Instruccion para Gemini

Continua el proyecto respetando estas reglas:

- No reemplaces openrouteservice/OSRM por Google Maps sin solicitarlo.
- No expongas secretos del `.env`.
- Conserva B02 y B01 en el backend, aunque la interfaz use etiquetas amigables.
- Conserva el estilo glassmorphism y la navegacion por botones.
- No vuelvas a mostrar tablas crudas de Supabase en las vistas principales.
- Antes de cambiar el esquema de deliveries, revisa las migraciones existentes.
- Si modificas el flujo manual, no generes IDs de venta inventados: usa ventas existentes o cambia explicitamente el modelo y la base de datos.
- Valida con `py_compile`, API y navegador despues de editar.
