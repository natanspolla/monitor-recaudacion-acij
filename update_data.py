#!/usr/bin/env python3
"""
Descarga el XLS de recaudacion del año en curso desde ARCA y el IPC desde
Google Sheets, y actualiza BUNDLED_XLS y BUNDLED_IPC en index.html.
Se corre automáticamente via GitHub Actions.
"""
import base64, json, re
from datetime import datetime
import requests

HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; ACIJ-bot/1.0)"}
XLS_URL = "https://contenidos.afip.gob.ar/institucional/estudios/archivos/serie{year}.xls"
IPC_URL = "https://docs.google.com/spreadsheets/d/1vT5nCBy1lbh4KNxmQhxclhkHsGiO5qB_m0PkyaWtlrs/export?format=csv&gid=0"
INDEX_FILE = "index.html"


def fetch_xls(year):
    url = XLS_URL.format(year=year)
    print(f"  Descargando {url} ...")
    r = requests.get(url, headers=HEADERS, timeout=60)
    r.raise_for_status()
    b64 = base64.b64encode(r.content).decode("ascii")
    print(f"  OK — {len(b64) // 1024} KB (base64)")
    return b64


def inject_year(content, year, b64):
    pattern = rf'({year}:\s*")[^"]*(")'
    updated, n = re.subn(pattern, rf"\g<1>{b64}\g<2>", content)
    if n == 0:
        print(f"  Aviso: clave {year} no encontrada en BUNDLED_XLS — omitiendo")
        return content, False
    return updated, True


def fetch_ipc():
    print(f"  Descargando IPC desde Google Sheets ...")
    r = requests.get(IPC_URL, headers=HEADERS, timeout=30)
    r.raise_for_status()
    rows = [line.split(",") for line in r.text.strip().splitlines()]

    DATE_KW = {"fecha", "periodo", "período", "date", "mes", "month"}
    MULT_KW = {"multiplicador", "coeficiente", "factor", "mult", "ipc", "ajuste", "coef", "acumulado"}

    date_col = mult_col = -1
    for row in rows[:8]:
        for ci, cell in enumerate(row):
            v = cell.strip().strip('"').lower()
            if date_col == -1 and any(kw in v for kw in DATE_KW):
                date_col = ci
            if mult_col == -1 and any(kw in v for kw in MULT_KW):
                mult_col = ci
        if date_col >= 0 and mult_col >= 0:
            break

    if date_col < 0 or mult_col < 0:
        raise ValueError("No se encontraron columnas de fecha/multiplicador en el CSV")

    ipc = {}
    for row in rows:
        if len(row) <= max(date_col, mult_col):
            continue
        raw_date = row[date_col].strip().strip('"')
        raw_mult = row[mult_col].strip().strip('"').replace(",", ".")
        # Normalizar fecha a YYYY-MM
        key = None
        if re.match(r"^\d{4}-\d{1,2}$", raw_date):
            parts = raw_date.split("-")
            key = f"{parts[0]}-{int(parts[1]):02d}"
        elif re.match(r"^\d{1,2}/\d{1,2}/\d{4}$", raw_date):
            parts = raw_date.split("/")
            key = f"{parts[2]}-{int(parts[1]):02d}"
        elif re.match(r"^\d{4}/\d{1,2}$", raw_date):
            parts = raw_date.split("/")
            key = f"{parts[0]}-{int(parts[1]):02d}"
        if not key:
            continue
        try:
            ipc[key] = round(float(raw_mult), 6)
        except ValueError:
            continue

    print(f"  OK — {len(ipc)} períodos IPC ({min(ipc)} → {max(ipc)})")
    return ipc


def inject_ipc(content, ipc):
    new_val = json.dumps(ipc, separators=(",", ":"))
    pattern = r"(const BUNDLED_IPC\s*=\s*)\{[^;]*\}(;)"
    updated, n = re.subn(pattern, rf"\g<1>{new_val}\g<2>", content)
    if n == 0:
        print("  Aviso: BUNDLED_IPC no encontrado en index.html — omitiendo")
        return content, False
    return updated, True


def main():
    now = datetime.utcnow()
    years = [now.year]
    if now.month == 1:
        years.append(now.year - 1)

    with open(INDEX_FILE, "r", encoding="utf-8") as f:
        content = f.read()

    changed = False

    for year in years:
        print(f"\nProcesando XLS {year}...")
        try:
            b64 = fetch_xls(year)
        except Exception as e:
            print(f"  Error al descargar {year}: {e}")
            continue
        content, ok = inject_year(content, year, b64)
        if ok:
            changed = True

    print("\nActualizando IPC...")
    try:
        ipc = fetch_ipc()
        content, ok = inject_ipc(content, ipc)
        if ok:
            changed = True
    except Exception as e:
        print(f"  Error al actualizar IPC: {e}")

    if changed:
        with open(INDEX_FILE, "w", encoding="utf-8") as f:
            f.write(content)
        print("\nindex.html actualizado.")
    else:
        print("\nSin cambios en los datos.")


if __name__ == "__main__":
    main()
