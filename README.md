# GECO Start

[![edition](https://img.shields.io/badge/edition-GECO_Start-0066cc?style=flat-square)](https://github.com/gecoerp/gecoerp)
[![version](https://img.shields.io/badge/version-1.0.0-0066cc?style=flat-square)](https://github.com/gecoerp/gecoerp)
[![build](https://img.shields.io/badge/build-passing-4c1?style=flat-square)](https://github.com/gecoerp/gecoerp)
[![license](https://img.shields.io/badge/license-LGPL--3.0-green.svg?style=flat-square)](LICENSE)
[![upgrade](https://img.shields.io/badge/upgrade-GECO_Prime-0f172a?style=flat-square)](https://www.gecoerp.com)

**GECO Start** is the open foundation of the **GECO Intelligent Enterprise Platform**, developed by **GECOERP (Gestión Empresarial y Competencia Empresarial)**.

Designed for growing businesses, startups, and developers, **GECO Start** provides a robust, extensible business management backbone covering essential operations including commercial management, invoicing, inventory tracking, and purchasing workflows.

---

## 🧩 GECO Platform Editions

| Feature / Capability | 🌱 GECO Start *(Open Foundation)* | 🚀 GECO Prime *(Enterprise Suite)* |
| :--- | :---: | :---: |
| **Licensing** | **LGPL-3.0 (Open Source)** | **Commercial Proprietary** |
| **Core CRM & Sales Operations** | ✅ Included | ✅ Advanced + Sales Forecasting |
| **Invoicing & Payments** | ✅ Included | ✅ Automated Tax & Multi-Currency Ledger |
| **Inventory & Warehouse** | ✅ Single Warehouse | ✅ Multi-Warehouse Dynamic Logistics |
| **Purchasing & Procurement** | ✅ Standard Orders | ✅ Multi-Warehouse Orders & Approvals |
| **User Experience (UI/UX)** | ✅ Clean Base Theme | 💎 Executive Glassmorphic UI & Drawer |
| **Omnichannel Messaging** | — | 💎 Native WhatsApp Business API |
| **AI Intelligence Core & MCP** | — | 💎 Autonomous Data Agents & MCP Server |
| **Executive Analytical Dashboards**| — | 💎 Real-Time Executive KPI Dashboards |

---

## 🚀 Core Capabilities in GECO Start

* **Commercial Flow:** Manage leads, customer databases, quotations, and confirmed sales orders seamlessly.
* **Procurement Operations:** Create supplier catalogs, track purchase requests, and validate received goods.
* **Warehouse Management:** Real-time stock counts, product cataloging, and inventory adjustments.
* **Billing & Financials:** Generate standard invoices, register customer payments, and track vendor bills.
* **Modular Extensibility:** Clean Python-based architecture ready to be extended with custom business apps or upgraded to **GECO Prime**.

---

## ⚡ Deployment & Quickstart

### Prerequisites
* **Python Runtime:** 3.10 / 3.11 / 3.12
* **Database Engine:** PostgreSQL 14+
* **Environment:** Linux / macOS / Windows Server

### 1. Clone & Setup
```bash
git clone https://github.com/gecoerp/gecoerp.git
cd gecoerp
```

### 2. Virtual Environment Setup
```bash
python -m venv .venv
# On Windows PowerShell:
.\.venv\Scripts\Activate.ps1
# On Linux/macOS:
source .venv/bin/activate

pip install --upgrade pip
pip install -r requirements.txt
```

### 3. Launch GECO Start
Configure your database connection parameters in `gecoerp.conf` and start the service:
```bash
python gecoerp-bin -c gecoerp.conf
```
Access the management console at: `http://localhost:8069`

---

## 🔒 Security & Support

For security vulnerability reports or assistance, contact our technical team directly at [mcabanas@gecoerp.com](mailto:mcabanas@gecoerp.com).

---

## 📜 Intellectual Property & Licensing

**GECO Start** is licensed under the **GNU Lesser General Public License v3.0 (LGPL-3.0)**. See [LICENSE](LICENSE) for full details.

```text
Copyright (c) 2026 GECOERP — Gestión Empresarial y Competencia Empresarial
Corporate Portal: https://www.gecoerp.com
Repository: https://github.com/gecoerp
Contact: mcabanas@gecoerp.com
```

---

<p align="center">
  <strong>GECO Start</strong> — The Open Foundation for Business Digitalization  
  <br/>
  Powered by <strong>GECOERP</strong>
</p>
