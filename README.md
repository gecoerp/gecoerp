# GECO ERP

[![1.0 build](https://img.shields.io/badge/1.0-success-4c1?style=flat-square)](https://github.com/gecoerp/gecoerp)
[![1.0 docs](https://img.shields.io/badge/1.0-docs-714B67?style=flat-square)](https://www.gecoerp.com)
[![1.0 help](https://img.shields.io/badge/1.0-help-714B67?style=flat-square)](https://www.gecoerp.com)
[![1.0 releases](https://img.shields.io/badge/1.0-releases-714B67?style=flat-square)](https://github.com/gecoerp/gecoerp/releases)

GECO ERP is a suite of modern enterprise business applications.

The main GECO ERP Apps include an [Enterprise CRM](https://www.gecoerp.com), [Sales Management](https://www.gecoerp.com), [Multi-Warehouse Inventory](https://www.gecoerp.com), [Purchasing & Supply Chain](https://www.gecoerp.com), [Billing & Financial Accounting](https://www.gecoerp.com), [Point of Sale (POS)](https://www.gecoerp.com), [Human Resources (HRMS)](https://www.gecoerp.com), [Omnichannel WhatsApp Integration](https://www.gecoerp.com), [AI & MCP Intelligence Core](https://www.gecoerp.com), ...

GECO ERP Apps can be used as stand-alone applications, but they also integrate seamlessly so you get a full-featured Enterprise ERP when you install several Apps.

## Getting started with GECO ERP

For a standard installation please follow the [Setup instructions](#setup-instructions) from the documentation.

To learn the software, we recommend the [GECO ERP Knowledge Base](https://www.gecoerp.com). Developers can start with the developer tutorials and API documentation.

### Setup instructions

1. **Clone the repository:**
   ```bash
   git clone https://github.com/gecoerp/gecoerp.git
   cd gecoerp
   ```

2. **Environment Setup:**
   ```bash
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1  # Windows PowerShell
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

3. **Start the GECO ERP Service:**
   ```bash
   .\iniciar_odoo.bat
   ```
   Open your browser at `http://localhost:8069`.

## Security

If you believe you have found a security issue, check our [Responsible Disclosure page](https://www.gecoerp.com) for details and get in touch with us via email at [mcabanas@gecoerp.com](mailto:mcabanas@gecoerp.com).

## License

This software is copyrighted by **GECOERP — Gestión Empresarial y Competencia Empresarial**.  
Licensed under the **GNU Lesser General Public License v3.0 (LGPL-3.0)**. See the [LICENSE](LICENSE) file for details.

---

Copyright (c) 2026 GECOERP. All rights reserved.  
Website: [https://www.gecoerp.com](https://www.gecoerp.com)
