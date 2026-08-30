# GECO — Intelligent Enterprise Platform

[![platform](https://img.shields.io/badge/platform-GECO_v1.0-0066cc?style=flat-square)](https://github.com/gecoerp/gecoerp)
[![edition](https://img.shields.io/badge/edition-GECO_Prime-0066cc?style=flat-square)](https://www.gecoerp.com)
[![build](https://img.shields.io/badge/build-passing-4c1?style=flat-square)](https://github.com/gecoerp/gecoerp)
[![architecture](https://img.shields.io/badge/architecture-Microservices_%26_Modular-0f172a?style=flat-square)](https://www.gecoerp.com)
[![docs](https://img.shields.io/badge/docs-available-0066cc?style=flat-square)](https://www.gecoerp.com)

**GECO** is a next-generation **Intelligent Enterprise Platform** designed to unify corporate operations, automate mission-critical workflows, and deliver real-time predictive business intelligence.

Engineered for scalability and modern enterprise ergonomics, the flagship **GECO Prime** edition combines an executive UI/UX design, native omnichannel WhatsApp communications, multi-warehouse supply chain intelligence, and deep integration with autonomous **AI & MCP** (*Model Context Protocol*) data agents.

---

## 🚀 Core Platform Capabilities

### 1. GECO Intelligence Core (AI & MCP)
* **Autonomous BI Agents:** Natural language querying over sales velocity, stock levels, cash flow projections, and purchasing cycles.
* **Model Context Protocol (MCP):** Enterprise-grade bridge connecting large language models (LLMs) securely with operational business databases.
* **Automated Decision Support:** Real-time anomaly detection and predictive replenishment recommendations.

### 2. GECO Connect & Omnichannel Hub
* **Native WhatsApp Business API:** Automated dispatch of purchase orders, invoices, shipment tracking, and quotations directly to customers and vendors.
* **Conversational Interaction:** Unified interactive chatters and customer timeline traceability.

### 3. GECO Supply Chain & Operations
* **Multi-Warehouse Optimization:** Distributed stock allocations, dynamic routing, and automated cross-warehouse transfers.
* **Procurement Operations:** Order-type classification, vendor scorecards, and executive analytical dashboards.

### 4. GECO Commercial & Finance
* **Revenue Operations:** Real-time pipeline forecasting, sales commission automation, and dynamic pricing engines.
* **Financial Ledger & Compliance:** Multi-currency ledgers, automated reconciliation, and executive financial health metrics.

### 5. GECO Prime Experience
* **Executive Glassmorphic UI:** Minimalist high-contrast interfaces, smart command palettes, and responsive multi-device layouts.
* **Fluid Lateral Drawer:** Instant fuzzy search across every module, action, and record in milliseconds.

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

### 2. Virtual Environment
```bash
python -m venv .venv
# On Windows PowerShell:
.\.venv\Scripts\Activate.ps1
# On Linux/macOS:
source .venv/bin/activate

pip install --upgrade pip
pip install -r requirements.txt
```

### 3. Launch GECO Platform
Configure your database settings in `gecoerp.conf` and start the server:
```bash
python gecoerp-bin -c gecoerp.conf
```
Access the management console at: `http://localhost:8069`

---

## 🔒 Security & Compliance

For security disclosures or enterprise vulnerability reports, please reach out directly to our security team at [mcabanas@gecoerp.com](mailto:mcabanas@gecoerp.com).

---

## 📜 Intellectual Property & Licensing

GECO Platform and GECO Prime are proprietary technologies developed by **GECOERP (Gestión Empresarial y Competencia Empresarial)**.  
Licensed under the **GNU Lesser General Public License v3.0 (LGPL-3.0)**. See [LICENSE](LICENSE) for full legal terms.

```text
Copyright (c) 2026 GECOERP — Gestión Empresarial y Competencia Empresarial
Corporate Portal: https://www.gecoerp.com
Repository: https://github.com/gecoerp
Contact: mcabanas@gecoerp.com
```

---

<p align="center">
  <strong>GECO Platform</strong> — Empowering Intelligent Enterprise Operations
</p>
