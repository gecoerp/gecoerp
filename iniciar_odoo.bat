@echo off
title Servidor Odoo 18 - GECO V8
chcp 65001 > nul
cd /d "D:\GECO V8"

echo ===================================================
echo           INICIANDO SERVIDOR ODOO 18 (GECO V8)
echo ===================================================
echo.
echo Directorio: D:\GECO V8
echo Entorno:    D:\GECO V8\.venv
echo URL Local:  http://localhost:8069
echo.
echo Presiona Ctrl + C para detener el servidor.
echo ===================================================
echo.

"D:\GECO V8\.venv\Scripts\python.exe" "D:\GECO V8\odoo-18.0\odoo-bin" -c "D:\GECO V8\odoo.conf" --dev=all

pause
