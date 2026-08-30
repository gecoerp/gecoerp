@echo off
title Actualizar Módulos GECOERP - GECO V8
chcp 65001 > nul
cd /d "D:\GECO V8"

echo ===================================================
echo     ACTUALIZANDO MODULOS GECOERP EN BASE DE DATOS v8
echo ===================================================
echo.

"D:\GECO V8\.venv\Scripts\python.exe" "D:\GECO V8\odoo-18.0\odoo-bin" -c "D:\GECO V8\odoo.conf" -d v8 -u purchase_order_type,purchase_order_type_dashboard,sale_order_type,sale_order_type_dashboard,geco_purchase_multi_warehouse,geco_ai_core,geco_mcp,geco_whatsapp,account_invoice_multi_payment,account_line_views,account_due_date_adjustment,sale_order_line_views,purchase_order_line_views,audit_security_log,base_branding_core,geco_license_marketplace,geco_ui_theme_core --stop-after-init

echo.
echo ===================================================
echo           ACTUALIZACION FINALIZADA CON EXITO
echo ===================================================
pause
