#!/usr/bin/env python3
"""
Descarga el XLS de recaudacion del año en curso desde ARCA y actualiza
BUNDLED_XLS en index.html. Se corre automáticamente via GitHub Actions.
"""
import base64, re, sys
from datetime import datetime
import requests

HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; ACIJ-bot/1.0)"}
XLS_URL = "https://contenidos.afip.gob.ar/institucional/estudios/archivos/serie{year}.xls"
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
    pattern = rf'("{year}"\s*:\s*")[^"]*(")'
    updated, n = re.subn(pattern, rf"\g<1>{b64}\g<2>", content)
    if n == 0:
        print(f"  Aviso: clave {year} no encontrada en BUNDLED_XLS — omitiendo")
        return content, False
    return updated, True


def main():
    now = datetime.utcnow()
    years = [now.year]
    if now.month == 1:
        years.append(now.year - 1)  # en enero, también refresca el año anterior

    with open(INDEX_FILE, "r", encoding="utf-8") as f:
        content = f.read()

    changed = False
    for year in years:
        print(f"\nProcesando {year}...")
        try:
            b64 = fetch_xls(year)
        except Exception as e:
            print(f"  Error al descargar {year}: {e}")
            continue
        content, ok = inject_year(content, year, b64)
        if ok:
            changed = True

    if changed:
        with open(INDEX_FILE, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"\nindex.html actualizado.")
    else:
        print("\nSin cambios en los datos.")


if __name__ == "__main__":
    main()
