# Bitácora Técnica de Cambios y Arquitectura - GECOERP (v18.0)

**Proyecto:** GECOERP (Distribución empresarial basada en Odoo 18.0)  
**Ruta Principal:** `D:\GECO V8`  
**Base de Datos Activa:** `v8`  
**Entorno Python:** `D:\GECO V8\.venv` (Python 3.12)  
**Última Actualización:** 27 de Agosto de 2026

---

## 1. Resumen Ejecutivo del Fork

GECOERP se estructura como una distribución empresarial propia y desacoplada de dependencias externas no deseadas, integrando:
1. **Gestión Comercial Avanzada**: Tipos de orden de compra y venta con tableros interactivos Kanban, recurrencia/suscripciones enterprise (MRR, periodos, fechas de corte) y vinculación a Equipos de Ventas (`crm.team`).
2. **Logística y Cadena de Suministro**: Recepción multi-almacén por línea en órdenes de compra con separación automática de albaranes (`stock.picking`).
3. **Inteligencia Artificial y Conectividad**: Servidor MCP nativo con 19 herramientas expuestas, pasarela WhatsApp-Web.js con chat y código QR, y motor de IA (`geco_ai_core`) con auditoría de tokens y proyecciones ML.
4. **Tesorería y Facturación**: Pagos múltiples/masivos de facturas y notas de crédito con conciliación automática (`gecoerp_invoice_multi_payment`) y módulo analítico nativo de líneas de facturación (`geco_account_line_view`).

---

## 2. Inventario de Módulos GECOERP y Modificaciones

---

### A. Tipos de Compra y Tablero
#### 1. `purchase_order_type`
- **Ubicación:** [`D:\GECO V8\addons\purchase_order_type`](file:///D:/GECO%20V8/addons/purchase_order_type)
- **Funcionalidad:** Clasificación de compras (Ordinarias, Activos Fijos, Importaciones, Gastos Operativos, etc.) y compras periódicas/recurrentes estilo suscripción.
- **Archivos Clave:**
  - `models/purchase_order_type.py`: Modelo `purchase.order.type` con soporte de periodicidad (`recurrence_period`: mensual, trimestral, anual), prorrateo, días de gracia y métricas financieras de gasto recurrente.
  - `models/purchase_order.py`: Inyección automática de `order_type_id`, secuencias dedicadas y propagación contable/analítica.
  - `views/view_purchase_order_type.xml`: Vistas de configuración y formulario con pestaña de recurrencia.

#### 2. `purchase_order_type_dashboard`
- **Ubicación:** [`D:\GECO V8\addons\purchase_order_type_dashboard`](file:///D:/GECO%20V8/addons/purchase_order_type_dashboard)
- **Funcionalidad:** Panel de control visual en Kanban para el departamento de compras.
- **Archivos Clave:**
  - `models/purchase_order_type.py`: Cómputo de KPIs (órdenes activas, gasto mensual, compras periódicas pendientes, autorizaciones requeridas).
  - `views/view_purchase_order_type.xml`: Tarjetas Kanban con barras de progreso, accesos directos y menús de 3 puntos.

---

### B. Tipos de Venta, Equipos CRM y Tablero
#### 3. `sale_order_type`
- **Ubicación:** [`D:\GECO V8\addons\sale_order_type`](file:///D:/GECO%20V8/addons/sale_order_type)
- **Funcionalidad:** Clasificación de ventas y pólizas recurrentes vinculadas a Equipos de Ventas (`crm.team`).
- **Archivos Clave:**
  - `models/sale_order_type.py`: Modelo `sale.order.type` con campos `team_id` (`crm.team`), `user_id` (líder de equipo), periodicidad de venta, cálculo de MRR y fechas de corte.
  - `models/sale_order.py`: Propagación automática de `team_id` al seleccionar el tipo de orden en cotizaciones/pedidos.
  - `views/view_sale_order_type.xml`: Formulario de configuración con selección de equipo comercial.

#### 4. `sale_order_type_dashboard`
- **Ubicación:** [`D:\GECO V8\addons\sale_order_type_dashboard`](file:///D:/GECO%20V8/addons/sale_order_type_dashboard)
- **Funcionalidad:** Panel Kanban comercial con métricas de ventas, ingresos recurrentes (MRR) y acceso al equipo asignado.
- **Archivos Clave:**
  - `models/sale_order_type.py`: Método `action_open_team` y creación de cotizaciones con `default_team_id`.
  - `views/view_sale_order_type.xml`: Tarjeta Kanban que muestra el Equipo de Ventas, Líder y enlace directo en el menú contextual.

---

### C. Logística y Multi-Almacén
#### 5. `geco_purchase_multi_warehouse`
- **Ubicación:** [`D:\GECO V8\addons\geco_purchase_multi_warehouse`](file:///D:/GECO%20V8/addons/geco_purchase_multi_warehouse)
- **Funcionalidad:** Permite especificar en cada línea de compra (`purchase.order.line`) un almacén o tipo de operación de destino diferente.
- **Archivos Clave:**
  - `models/purchase_order_line.py`: Campo `picking_type_id` (`stock.picking.type`).
  - `models/purchase_order.py`: Sobrescritura de `_create_picking()` compatible con Odoo 18 (`consu`/`is_storable`) para agrupar líneas por almacén y generar recepciones (`stock.picking`) independientes automáticamente al confirmar.
  - `views/purchase_order_view.xml`: Columna `picking_type_id` añadida en la tabla de productos de la orden de compra.
  - `views/purchase_order_report.xml`: Reporte impreso QWeb con columna "Deliver To / Entregar en".

---

### D. Inteligencia Artificial y Servidor MCP
#### 6. `geco_ai_core`
- **Ubicación:** [`D:\GECO V8\addons\geco_ai_core`](file:///D:/GECO%20V8/addons/geco_ai_core)
- **Funcionalidad:** Motor maestro de IA para GECOERP. Enrutamiento hacia OpenAI / Gemini, almacenamiento seguro de llaves API, auditoría de tokens consumidos y proyecciones de gasto por Machine Learning (`scikit-learn`/`pandas`).
- **Archivos Clave:**
  - `models/geco_ai_engine.py`: API central `generate_text()` y enrutamiento de llamadas con function-calling.
  - `models/geco_ai_log.py`: Registro transaccional de peticiones, tokens y costo estimado.
  - `models/geco_ai_dashboard.py`: Algoritmo de regresión neuronal (`MLPRegressor`) para proyectar consumo mensual y anual.
  - `static/src/js/geco_ai_dashboard.js`: Componente OWL 2 para visualización gráfica del consumo.

#### 7. `geco_mcp`
- **Ubicación:** [`D:\GECO V8\addons\geco_mcp`](file:///D:/GECO%20V8/addons/geco_mcp)
- **Funcionalidad:** Servidor nativo Model Context Protocol (MCP) para conectar agentes externos (Claude Desktop, Cursor, IDEs) a la base de datos de Odoo mediante Streamable HTTP.
- **Archivos Clave:**
  - `core/tool.py`, `models/tool.py`: Registro y ejecución de herramientas nativas (19 herramientas configuradas).
  - `controllers/`: Endpoints HTTP con autenticación por llaves API (`geco_mcp.key`).
  - `views/`: Vistas actualizadas a Odoo 18 (`view_mode="list,form"` y plantillas `<t t-name="card">`).

---

### E. WhatsApp Empresarial
#### 8. `geco_whatsapp`
- **Ubicación:** [`D:\GECO V8\addons\geco_whatsapp`](file:///D:/GECO%20V8/addons/geco_whatsapp)
- **Funcionalidad:** Pasarela con microservicio WhatsApp-Web.js para envío directo de cotizaciones, facturas, mensajes libres y registro de conversaciones entrantes/salientes en el chatter del contacto.
- **Archivos Clave:**
  - `models/whatsapp_service.py`: Comunicación HTTP con el servicio WhatsApp-Web.js.
  - `models/whatsapp_gateway_log.py`: Modelo de bitácora con inicialización automática de tabla `whatsapp_gateway_logs`.
  - `wizard/whatsapp_compose.py`: Asistente interactivo de redacción con plantillas dinámicas QWeb.
  - `static/src/js/whatsapp_qr_dialog.js`: Diálogo OWL para escanear código QR de vinculación de sesión.

---

### F. Facturación y Contabilidad
#### 9. `gecoerp_invoice_multi_payment`
- **Ubicación:** [`D:\GECO V8\addons\gecoerp_invoice_multi_payment`](file:///D:/GECO%20V8/addons/gecoerp_invoice_multi_payment)
- **Funcionalidad:** Registro de pagos combinados de múltiples facturas y notas de crédito de clientes y proveedores desde el pago o asistente masivo.
- **Archivos Clave:**
  - `models/account_payment.py`: Modo de pago `multi_payment`, cálculo de asignaciones y conciliación (`dev_reconcile`).
  - `models/advnce_payment_line.py`: Líneas de asignación de saldos por factura (`advance.payment.line`).
  - `wizard/bulk_invoice_payment.py`: Asistente de pago masivo con selección múltiple en facturas.
  - `views/account_payment.xml`: Pestaña "Facturas a Pagar" integrada en el formulario contable de Odoo 18.

#### 10. `geco_account_line_view` (Módulo Propio Nativo)
- **Ubicación:** [`D:\GECO V8\addons\geco_account_line_view`](file:///D:/GECO%20V8/addons/geco_account_line_view)
- **Funcionalidad:** Análisis, consulta y auditoría multidimensional de líneas de facturación (`account.move.line`) para clientes y proveedores.
- **Archivos Clave:**
  - `models/account_move_line.py`: Campos relacionales optimizados (`product_image_128`, `product_categ_id`, `invoice_user_id`, `invoice_date_due`) y método `action_open_invoice()` para apertura directa de la factura origen.
  - `views/account_move_line_views.xml`: Vistas de búsqueda, `<list>` con sumatorios de subtotales y cantidades, `<kanban>` con tarjetas de producto, `<pivot>` dinámico, `<graph>` interactivo y `<calendar>`.
  - `views/account_move_line_customer_views.xml`: Menús "Líneas de Facturas" y "Líneas de Notas de Crédito" en **Facturación ➔ Clientes**.
  - `views/account_move_line_vendor_views.xml`: Menús "Líneas de Facturas de Proveedor" y "Líneas de Notas de Crédito" en **Facturación ➔ Proveedores**.
  - `views/account_move_line_report_views.xml`: Menú "Análisis de Líneas de Facturación" en **Facturación ➔ Informes**.

---

## 3. Scripts Operativos de Mantenimiento

1. [`iniciar_odoo.bat`](file:///D:/GECO%20V8/iniciar_odoo.bat):
   Inicia el servidor GECOERP en `http://localhost:8069` utilizando el entorno virtual `.venv` y el archivo `odoo.conf`.
2. [`actualizar_modulos.bat`](file:///D:/GECO%20V8/actualizar_modulos.bat):
   Ejecuta la actualización por lotes de toda la suite de módulos GECOERP en la base de datos `v8`:
   ```bat
   "D:\GECO V8\.venv\Scripts\python.exe" "D:\GECO V8\odoo-18.0\odoo-bin" -c "D:\GECO V8\odoo.conf" -d v8 -u purchase_order_type,purchase_order_type_dashboard,sale_order_type,sale_order_type_dashboard,geco_purchase_multi_warehouse,geco_ai_core,geco_mcp,geco_whatsapp,gecoerp_invoice_multi_payment,geco_account_line_view --stop-after-init
   ```

---

## 4. Convenciones y Reglas de Calidad para el Fork GECOERP

- **Etiquetas de Vistas:** Usar siempre `<list>` en lugar del obsoleto `<tree>`, y `<t t-name="card">` en vistas `<kanban>`.
- **Acciones:** `view_mode` debe definirse exclusivamente con valores válidos de v18 (`list,form,kanban,pivot,graph,calendar`).
- **Módulos JavaScript / OWL:** Todos los scripts de cliente deben iniciar con la cabecera `/** @odoo-module **/`.
- **Autoría:** Mantener `author: 'GECOERP'` y licencia limpia `LGPL-3` / `OPL-1`.
