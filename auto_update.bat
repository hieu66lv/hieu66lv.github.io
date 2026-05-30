@echo off
echo ========================================
echo   Auto Update Lien Quan Mobile
echo   %date% %time%
echo ========================================
echo.
echo Chon che do:
echo   1. Chi them tuong moi (nhanh)
echo   2. Kiem tra ca skin moi (cham hon)
echo   3. Crawl lai toan bo
echo.
set /p choice="Nhap lua chon (1/2/3, mac dinh=1): "

cd /d "%~dp0"

if "%choice%"=="2" (
    python auto_update.py --check-skins
) else if "%choice%"=="3" (
    python auto_update.py --full
) else (
    python auto_update.py
)

echo.
echo Hoan tat! Nhan phim bat ky de dong...
pause >nul
