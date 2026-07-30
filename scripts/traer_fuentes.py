#!/usr/bin/env python3
"""
Descarga las fuentes que se pueden traer solas.

    python scripts/traer_fuentes.py

Trae dos de los tres libros desde el portal del Ministerio de Hacienda (IRC):

  · Tenedores de TES  — vive en una dirección fija; el archivo se reemplaza en
    su sitio cada mes y la URL no cambia.
  · Histórico del GNC — la dirección lleva el mes en el nombre, así que se lee
    el listado y se toma el más reciente.

El boletín de deuda externa del Banco de la República NO se descarga aquí: está
en un portal que dispara las descargas por JavaScript y con protección
anti-robot. Ese sigue siendo manual; como sale con dos meses de rezago, no es el
que apura.

Si una descarga falla o devuelve algo que no es un Excel, el archivo que ya está
en `fuentes/` se deja intacto. Vale más un dato viejo que uno roto.
"""

from __future__ import annotations

import argparse
import re
import shutil
import subprocess
import sys
import tempfile
import time
import urllib.error
import urllib.request
from pathlib import Path

# La consola de Windows usa cp1252 y revienta al imprimir «✓» o «·».
for _flujo in (sys.stdout, sys.stderr):
    try:
        _flujo.reconfigure(encoding="utf-8")
    except Exception:
        pass

ROOT = Path(__file__).resolve().parent.parent
FUENTES = ROOT / "fuentes"

IRC = "https://www.irc.gov.co"
TES_URL = f"{IRC}/documents/d/guest/historico-tenedores-tes-2?download=true"
GNC_LISTADO = f"{IRC}/deuda-publica/perfil-deuda-publica-gnc"

MESES = ["enero", "febrero", "marzo", "abril", "mayo", "junio",
         "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre"]

# Sin un User-Agent de navegador, el portal responde con una página de error.
CABECERAS = {
    "User-Agent": ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                   "(KHTML, like Gecko) Chrome/124.0 Safari/537.36"),
    "Accept": "*/*",
    "Accept-Language": "es-CO,es;q=0.9",
}
MINIMO_BYTES = 20_000


class DescargaFallida(RuntimeError):
    pass


def _con_curl(url: str, timeout: int) -> bytes:
    """Descarga con curl.

    El portal del IRC va detrás de un cortafuegos que rechaza a Python con 403
    aunque las cabeceras sean idénticas a las de un navegador: distingue el
    cliente por su huella TLS, no por lo que dice ser. curl pasa sin problema,
    así que se usa como transporte. Está en los runners de GitHub y en Windows
    10 en adelante.
    """
    with tempfile.NamedTemporaryFile(delete=False, suffix=".descarga") as tmp:
        destino = Path(tmp.name)
    try:
        orden = ["curl", "-sS", "--fail", "--location",
                 "--max-time", str(timeout),
                 "--retry", "3", "--retry-delay", "10", "--retry-all-errors",
                 "-A", CABECERAS["User-Agent"], "-o", str(destino), url]
        r = subprocess.run(orden, capture_output=True, text=True)
        if r.returncode != 0:
            detalle = (r.stderr or "").strip().splitlines()
            raise DescargaFallida(f"curl falló ({r.returncode}): {detalle[-1] if detalle else 'sin detalle'}")
        return destino.read_bytes()
    finally:
        destino.unlink(missing_ok=True)


def _con_urllib(url: str, timeout: int) -> bytes:
    req = urllib.request.Request(url, headers=CABECERAS)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.read()
    except urllib.error.HTTPError as e:
        raise DescargaFallida(f"respondió {e.code}") from e
    except Exception as e:
        raise DescargaFallida(str(e)) from e


HAY_CURL = shutil.which("curl") is not None


def pedir(url: str, timeout: int = 180, intentos: int = 3) -> bytes:
    """Pide una URL con reintentos pacientes."""
    espera = 20
    ultimo = None
    for intento in range(1, intentos + 1):
        try:
            return _con_curl(url, timeout) if HAY_CURL else _con_urllib(url, timeout)
        except DescargaFallida as e:
            ultimo = str(e)
            if "404" in ultimo:        # no publicado aún: no hay nada que reintentar
                raise DescargaFallida(f"{url} respondió 404 (aún no está publicado)") from e
        if intento < intentos:
            print(f"    (intento {intento} de {intentos}: {ultimo}; reintento en {espera} s)")
            time.sleep(espera)
            espera *= 2
    raise DescargaFallida(f"{url}: {ultimo} tras {intentos} intentos")


def guardar_excel(datos: bytes, destino: Path, origen: str) -> bool:
    """Escribe sólo si de verdad es un Excel. Devuelve True si cambió el archivo."""
    if not datos.startswith(b"PK"):
        raise DescargaFallida(
            f"{origen} no devolvió un Excel (llegaron {len(datos):,} bytes que "
            f"empiezan por {datos[:8]!r}). Puede ser una página de error.")
    if len(datos) < MINIMO_BYTES:
        raise DescargaFallida(f"{origen} devolvió sólo {len(datos):,} bytes; se esperaba más.")

    anterior = destino.read_bytes() if destino.exists() else b""
    if anterior == datos:
        print(f"  = {destino.name:<26} sin cambios ({len(datos) / 1024:,.0f} kB)")
        return False

    # Se escribe aparte y luego se mueve, para no dejar el archivo a medias.
    with tempfile.NamedTemporaryFile(delete=False, dir=destino.parent, suffix=".parcial") as tmp:
        tmp.write(datos)
        temporal = Path(tmp.name)
    temporal.replace(destino)
    marca = "nuevo" if not anterior else "actualizado"
    print(f"  ✓ {destino.name:<26} {marca} ({len(datos) / 1024:,.0f} kB)")
    return True


def url_gnc_mas_reciente() -> tuple[str, str]:
    """Busca en el listado el «Histórico Total <mes><año>» más nuevo."""
    html = pedir(GNC_LISTADO, timeout=60).decode("utf-8", "ignore")
    encontrados = []
    for m in re.finditer(r'/documents/d/guest/(historico-total-([a-záéíóú]+)(\d{4}))\?download=true',
                         html, re.I):
        slug, mes, anio = m.group(1), m.group(2).lower(), int(m.group(3))
        if mes in MESES:
            encontrados.append((anio, MESES.index(mes) + 1, slug, f"{mes} {anio}"))
    if not encontrados:
        raise DescargaFallida(
            "No se encontró ningún «historico-total-<mes><año>» en el listado del IRC. "
            "Puede que hayan cambiado la página: revisa scripts/traer_fuentes.py.")
    encontrados.sort()
    _, _, slug, etiqueta = encontrados[-1]
    return f"{IRC}/documents/d/guest/{slug}?download=true", etiqueta


def main() -> int:
    ap = argparse.ArgumentParser(description="Descarga las fuentes automatizables.")
    ap.add_argument("--salida", type=Path, default=FUENTES)
    args = ap.parse_args()
    args.salida.mkdir(parents=True, exist_ok=True)

    cambios, fallos = 0, []

    print("Tenedores de TES…")
    try:
        cambios += guardar_excel(pedir(TES_URL), args.salida / "tenedores_tes.xlsx", "El portal del IRC")
    except DescargaFallida as e:
        fallos.append(f"tenedores de TES: {e}")
        print(f"  ✗ {e}")

    print("Histórico del GNC…")
    try:
        url, etiqueta = url_gnc_mas_reciente()
        print(f"  · el más reciente publicado es {etiqueta}")
        cambios += guardar_excel(pedir(url), args.salida / "historico_gnc.xlsx", "El portal del IRC")
    except DescargaFallida as e:
        fallos.append(f"histórico del GNC: {e}")
        print(f"  ✗ {e}")

    print("\nBoletín de deuda externa: se descarga a mano (Banco de la República).")

    if fallos:
        print("\nNo se pudo traer:", file=sys.stderr)
        for f in fallos:
            print(f"  · {f}", file=sys.stderr)
        print("Los archivos que ya estaban en fuentes/ quedaron intactos.", file=sys.stderr)
        # Que fallen las dos es un problema de verdad; que falle una, no tanto.
        return 1 if len(fallos) == 2 else 0

    print(f"\nListo. Archivos que cambiaron: {cambios}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
