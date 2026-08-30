<p align="center">
  <img src="addons/geco_login_theme_prime/static/description/icon.png" alt="GECOERP Logo" width="130" style="border-radius: 24px; box-shadow: 0 10px 30px rgba(254,80,49,0.35);"/>
</p>

<h1 align="center">GECO ERP — Versión 1.0</h1>

<p align="center">
  <strong>Plataforma Empresarial Inteligente de Próxima Generación</strong>
</p>

<p align="center">
  <a href="https://github.com/gecoerp"><img src="https://img.shields.io/badge/Brand-GECOERP-fe5031?style=for-the-badge&logo=github&logoColor=white" alt="GECOERP GitHub"/></a>
  <a href="https://www.gecoerp.com"><img src="https://img.shields.io/badge/Web-gecoerp.com-0f172a?style=for-the-badge&logo=google-chrome&logoColor=white" alt="Website"/></a>
  <a href="#"><img src="https://img.shields.io/badge/Version-1.0.0-0f172a?style=for-the-badge" alt="GECO ERP 1.0"/></a>
  <a href="#"><img src="https://img.shields.io/badge/Python-3.10%20%7C%203.11%20%7C%203.12-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python Version"/></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/License-LGPL--3.0-green.svg?style=for-the-badge" alt="License LGPL-3.0"/></a>
  <a href="mailto:mcabanas@gecoerp.com"><img src="https://img.shields.io/badge/Lead-Manuel%20Cabañas-fe5031?style=for-the-badge&logo=gmail&logoColor=white" alt="Contact"/></a>
</p>

---

## 🌟 Resumen Ejecutivo

**GECO ERP V1** es la suite empresarial integral desarrollada por **GECOERP (Gestión Empresarial y Competencia Empresarial)**, diseñada para transformar la operativa de negocios modernos mediante una arquitectura modular de alto rendimiento, automatizaciones inteligentes, comunicación omnicanal y análisis de datos en tiempo real.

Integra una interfaz de usuario ejecutiva **Flame Orange & Slate**, módulos especializados para control multi-almacén, sincronización con **WhatsApp Business API**, y un núcleo avanzado de conectores **AI & MCP** (*Model Context Protocol*).

---

## 🎨 Arquitectura de Módulos & UI/UX

### 1. Interfaz Ejecutiva Rediseñada (`geco_ui_theme_core`)
* **White & Flame Orange Topbar:** Barra de navegación minimalista en blanco puro con acentos corporativos en Naranja `#fe5031` y gris pizarra `#0f172a`.
* **Botón Cápsula Lanzador de Aplicaciones:** Acceso rápido y elegante a todos los módulos sin sobrecarga visual.
* **Drawer Lateral con Búsqueda Inteligente:** Menú deslizante con motor de búsqueda en tiempo real para localizar cualquier función del ERP al instante.
* **Workflow Statusbar Interlocking:** Flujo de etapas (*Workflow Chevrons*) interconectadas con diseño poligonal de alta visibilidad.
* **Switches iOS en Formularios:** Campos booleanos transformados en botones toggle modernos y responsivos.

### 2. Inicio de Sesión Prime (`geco_login_theme_prime`)
* Experiencia visual *Glassmorphic* con efectos de desenfoque y gradientes de alta fidelidad.
* Identidad de marca oficial de GECOERP con personalización multisede.

### 3. Integración Nativa de WhatsApp (`geco_whatsapp`)
* Envío automatizado de cotizaciones, pedidos, órdenes de compra y facturas en formato PDF.
* Plantillas dinámicas y trazabilidad completa de conversaciones en el chatter.

### 4. Inteligencia Artificial & MCP Core (`geco_ai_core` & `geco_mcp`)
* Conexión estandarizada con agentes inteligentes y modelos de lenguaje de última generación mediante el protocolo **MCP**.
* Consultas en lenguaje natural sobre datos de ventas, inventario, tesorería y analítica de compras.

### 5. Cadena de Suministro & Operaciones Multisede (`geco_purchase_multi_warehouse`)
* Clasificación de órdenes de compra y venta por tipo de operación con tableros ejecutivos dedicados.
* Gestión inteligente de pedidos con recepción distribuida en múltiples almacenes.

---

## 📂 Estructura del Repositorio

```text
d:/GECO V8/
├── addons/                               # Módulos y extensiones oficiales de GECOERP
│   ├── geco_ui_theme_core/               # Núcleo de diseño, temas, navbar y UI moderna
│   ├── geco_login_theme_prime/           # Tema de login glassmorphic y branding oficial
│   ├── geco_whatsapp/                    # Conector y motor de mensajes WhatsApp
│   ├── geco_ai_core/                     # Asistente y lógica de Inteligencia Artificial
│   ├── geco_mcp/                         # Servidor MCP para integración de LLMs
│   ├── geco_purchase_multi_warehouse/    # Compras avanzadas multi-almacén
│   ├── purchase_order_type/              # Tipificación de órdenes de compra
│   ├── purchase_order_type_dashboard/    # Dashboard analítico de compras
│   ├── sale_order_type/                  # Tipificación de cotizaciones y pedidos
│   ├── sale_order_type_dashboard/        # Dashboard analítico de ventas
│   └── garazd_product_label/             # Generador e impresor de etiquetas
├── sites-enabled/                        # Configuraciones de servidor web y proxies
├── gecoerp.conf                          # Archivo de configuración del servidor ERP
├── iniciar_odoo.bat                      # Script para levantar el servicio localmente
├── actualizar_modulos.bat                # Script para compilar y actualizar módulos
├── requirements.txt                      # Dependencias de Python del proyecto
├── .gitignore                            # Exclusiones de control de versiones
├── LICENSE                               # Licencia LGPL-3.0
└── README.md                             # Documentación y portada principal
```

---

## ⚡ Guía de Inicio Rápido

### Prerrequisitos
* **Python:** 3.10, 3.11 o 3.12
* **PostgreSQL:** 14+ / 15+ / 16+
* **Git:** 2.30+

### 1. Clonar el Repositorio
```bash
git clone https://github.com/gecoerp/gecoerp.git
cd gecoerp
```

### 2. Crear y Activar Entorno Virtual
```bash
python -m venv .venv
# En Windows (PowerShell):
.\.venv\Scripts\Activate.ps1
# En Linux/macOS:
source .venv/bin/activate
```

### 3. Instalar Dependencias
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Configurar Base de Datos & Iniciar Servidor
Edita el archivo `gecoerp.conf` con las credenciales de tu PostgreSQL y ejecuta:
```bash
.\iniciar_odoo.bat
```

Abre tu navegador en: `http://localhost:8069`

---

## 📜 Licencia & Derechos de Autor

Este proyecto está licenciado bajo la **GNU Lesser General Public License v3.0 (LGPL-3.0)**.  
Consulta el archivo [LICENSE](LICENSE) para más detalles.

```text
Copyright (c) 2026 GECOERP — Gestión Empresarial y Competencia Empresarial
Líder de Proyecto: Manuel Cabañas
Email: mcabanas@gecoerp.com
Sitio Web: https://www.gecoerp.com
GitHub: https://github.com/gecoerp
```

---

<p align="center">
  Desarrollado con ❤️ por <strong>GECOERP</strong> | Innovando la gestión empresarial
</p>
