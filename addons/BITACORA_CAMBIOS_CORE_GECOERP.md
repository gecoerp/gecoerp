# Bitácora Técnica de Cambios y Arquitectura - GECOERP (v18.0)

**Proyecto:** GECOERP (Distribución empresarial basada en Odoo 18.0)  
**Ruta del Core Principal:** `D:\GECO V8\odoo-18.0\addons`  
**Ruta de Addons Propios:** `D:\GECO V8\addons`  
**Base de Datos Activa:** `v8`  
**Entorno Python:** `D:\GECO V8\.venv` (Python 3.12)  
**Última Actualización:** 27 de Agosto de 2026

---

## 1. Estructura Arquitectónica de GECOERP

El repositorio se divide estratégicamente en dos capas:
1. **Core Principal (`D:\GECO V8\odoo-18.0\addons\`)**:
   Módulos y extensiones nativas del sistema base GECOERP con nomenclaturas estándar, integrados directamente con **Ajustes de Configuración (`res.config.settings`)**.
2. **Addons Empresariales GECOERP (`D:\GECO V8\addons\`)**:
   Módulos de conectividad, inteligencia artificial, licenciamiento y características comerciales avanzadas (`geco_ui_theme_core`, `geco_ai_core`, `geco_mcp`, `geco_whatsapp`, `geco_purchase_multi_warehouse`, `purchase_order_type`, `sale_order_type`).

---

## 2. Inventario de Módulos y Modificaciones

---

### A. Módulos Integrados en el Core Principal (`D:\GECO V8\odoo-18.0\addons\`)

#### 1. `account_invoice_multi_payment`
- **Ubicación en el Core:** [`D:\GECO V8\odoo-18.0\addons\account_invoice_multi_payment`](file:///D:/GECO%20V8/odoo-18.0/addons/account_invoice_multi_payment)
- **Funcionalidad:** Registro de pagos para múltiples facturas y notas de crédito de clientes y proveedores con asignación exacta y personalizada por documento.
- **Configuración en Ajustes:** Integrado en **Facturación / Contabilidad ➔ Configuración ➔ Ajustes ➔ Pagos de Clientes** (`group_multi_invoice_payment`).

#### 2. `account_line_views`
- **Ubicación en el Core:** [`D:\GECO V8\odoo-18.0\addons\account_line_views`](file:///D:/GECO%20V8/odoo-18.0/addons/account_line_views)
- **Funcionalidad:** Análisis multidimensional a nivel de producto para líneas de facturas y notas de crédito (`account.move.line`) en Clientes, Proveedores e Informes de Facturación.

#### 3. `account_due_date_adjustment`
- **Ubicación en el Core:** [`D:\GECO V8\odoo-18.0\addons\account_due_date_adjustment`](file:///D:/GECO%20V8/odoo-18.0/addons/account_due_date_adjustment)
- **Funcionalidad:** Cálculo inteligente de fechas de vencimiento omitiendo fines de semana, aplicando días fijos de pago y feriados (globales o específicos por término).
- **Menú Técnico:** Menú CRUD en **Facturación ➔ Configuración ➔ Facturación ➔ Días Festivos e Inhábiles** protegido con `groups="base.group_no_one"` (Modo Desarrollador).
- **Configuración en Ajustes:** Integrado en **Facturación ➔ Configuración ➔ Ajustes ➔ Facturas de Clientes** (`group_due_date_adjustment`).

#### 4. `sale_order_line_views`
- **Ubicación en el Core:** [`D:\GECO V8\odoo-18.0\addons\sale_order_line_views`](file:///D:/GECO%20V8/odoo-18.0/addons/sale_order_line_views)
- **Funcionalidad:** Vistas multidimensionales y análisis a nivel de línea para pedidos de venta y cotizaciones (`sale.order.line`).
- **Menús Integrados en Ventas:**
  - **Ventas ➔ Órdenes ➔ Líneas de Cotizaciones** (`draft`, `sent`).
  - **Ventas ➔ Órdenes ➔ Líneas de Órdenes de Venta** (`sale`, `done`).
  - **Ventas ➔ Reportes ➔ Análisis de Líneas de Venta** (Pivot, Gráficos, Kanban).

#### 5. `purchase_order_line_views`
- **Ubicación en el Core:** [`D:\GECO V8\odoo-18.0\addons\purchase_order_line_views`](file:///D:/GECO%20V8/odoo-18.0/addons/purchase_order_line_views)
- **Funcionalidad:** Vistas multidimensionales y análisis a nivel de producto para solicitudes de cotización y órdenes de compra (`purchase.order.line`).
- **Menús Integrados en Compras:**
  - **Compras ➔ Órdenes ➔ Líneas de Solicitudes de Cotización** (`draft`, `sent`, `to approve`).
  - **Compras ➔ Órdenes ➔ Líneas de Órdenes de Compra** (`purchase`, `done`).
  - **Compras ➔ Reportes ➔ Análisis de Líneas de Compra** (Pivot, Gráficos, Kanban).

#### 6. `audit_security_log`
- **Ubicación en el Core:** [`D:\GECO V8\odoo-18.0\addons\audit_security_log`](file:///D:/GECO%20V8/odoo-18.0/addons/audit_security_log)
- **Funcionalidad:** Motor corporativo de pistas de auditoría inmutables (`audit.log` y `audit.rule`) que registra cambios en campos críticos (precios, límites de crédito, plazos, descuentos) y operaciones sensibles (cancelaciones, eliminaciones, creaciones).
- **Inmutabilidad:** Métodos `write` y `unlink` bloqueados para preservar la integridad legal y pericial de la bitácora.
- **Configuración:** Integrado en **Ajustes Generales ➔ Seguridad y Pistas de Auditoría** y menú dedicado en **Ajustes ➔ Seguridad y Pistas de Auditoría**.

#### 7. `base_branding_core`
- **Ubicación en el Core:** [`D:\GECO V8\odoo-18.0\addons\base_branding_core`](file:///D:/GECO%20V8/odoo-18.0/addons/base_branding_core)
- **Funcionalidad:** White-labeling e identidad corporativa total de GECOERP. Elimina menciones y enlaces de terceros en plantillas de correo salientes, layouts de reportes PDF y cliente web.
- **Configuración:** Integrado en **Ajustes Generales ➔ Identidad Corporativa y Marca** para personalizar nombre del sistema, pie de correos y pie de informes.

#### 8. `geco_license_marketplace`
- **Ubicación en el Core:** [`D:\GECO V8\odoo-18.0\addons\geco_license_marketplace`](file:///D:/GECO%20V8/odoo-18.0/addons/geco_license_marketplace)
- **Funcionalidad:** Gestor universal de licencias (Community, Pro, Enterprise) y Tienda/Marketplace dentro del ERP.
- **Auto-Gestión de Addons:** Detección y creación automática del directorio de almacenamiento de módulos del cliente (`~/.local/share/Gecoerp/addons/18.0/`).
- **Instalación en 1-Clic:** Descarga, descompresión e instalación de módulos adquiridos en el portal sin reinicio manual.

---

### B. Módulos en Addons Propios (`D:\GECO V8\addons\`)

#### 9. `geco_ui_theme_core`
- **Ubicación:** `D:\GECO V8\addons\geco_ui_theme_core`
- **Funcionalidad:** Rediseño total de la barra de navegación superior (Navbar) estilo SaaS Slate Deep Navy (#0b132b / #1c2541), botón lanzador de aplicaciones con insignia GECOERP, menús en píldoras con transiciones y dropdowns modernos.

#### 10. `purchase_order_type` y `purchase_order_type_dashboard`
- **Ubicación:** `D:\GECO V8\addons\purchase_order_type` y `purchase_order_type_dashboard`
- **Funcionalidad:** Tipos de compra, compras recurrentes/suscripciones enterprise y panel Kanban con KPIs.

#### 11. `sale_order_type` y `sale_order_type_dashboard`
- **Ubicación:** `D:\GECO V8\addons\sale_order_type` y `sale_order_type_dashboard`
- **Funcionalidad:** Tipos de venta, vinculación a Equipos de Ventas (`crm.team`), cálculo de MRR y panel Kanban comercial.

#### 12. `geco_purchase_multi_warehouse`
- **Ubicación:** `D:\GECO V8\addons\geco_purchase_multi_warehouse`
- **Funcionalidad:** Recepción multi-almacén por línea en órdenes de compra con separación automática de albaranes (`stock.picking`).

#### 13. `geco_ai_core`
- **Ubicación:** `D:\GECO V8\addons\geco_ai_core`
- **Funcionalidad:** Motor maestro de IA (OpenAI / Gemini), bitácora de consumo de tokens y proyecciones de gasto por Machine Learning (`scikit-learn`/`pandas`).

#### 14. `geco_mcp`
- **Ubicación:** `D:\GECO V8\addons\geco_mcp`
- **Funcionalidad:** Servidor nativo Model Context Protocol (MCP) con 19 herramientas expuestas vía Streamable HTTP.

#### 15. `geco_whatsapp`
- **Ubicación:** `D:\GECO V8\addons\geco_whatsapp`
- **Funcionalidad:** Pasarela WhatsApp-Web.js, plantillas dinámicas QWeb y diálogo QR interactivo en OWL.

---

## 3. Scripts Operativos

1. [`iniciar_odoo.bat`](file:///D:/GECO%20V8/iniciar_odoo.bat): Inicia el servidor GECOERP en `http://localhost:8069`.
2. [`actualizar_modulos.bat`](file:///D:/GECO%20V8/actualizar_modulos.bat): Actualiza todos los módulos en la base de datos `v8`.
