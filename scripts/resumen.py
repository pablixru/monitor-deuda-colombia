#!/usr/bin/env python3
"""
Resume, en Markdown, qué cambió en los datos respecto a lo que hay en git.

    python scripts/resumen.py

Sirve para el cuerpo del Pull Request mensual: la idea es que revisar la
actualización sea leer diez líneas, no abrir un JSON de setenta kilobytes.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

for _f in (sys.stdout, sys.stderr):
    try:
        _f.reconfigure(encoding="utf-8")
    except Exception:
        pass

ROOT = Path(__file__).resolve().parent.parent
DATOS = ROOT / "public" / "data"


def version_en_git(rel: str):
    try:
        crudo = subprocess.run(["git", "show", f"HEAD:{rel}"], cwd=ROOT,
                               capture_output=True, text=True, encoding="utf-8", check=True).stdout
        return json.loads(crudo)
    except Exception:
        return None


def actual(nombre: str):
    p = DATOS / nombre
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else None


def mil(v, dec=1):
    if v is None:
        return "—"
    return f"{v:,.{dec}f}".replace(",", "·").replace(".", ",").replace("·", ".")


def fila(etiqueta, antes, ahora, sufijo="", dec=1):
    if antes == ahora:
        return None
    flecha = "" if antes is None else " →"
    return f"| {etiqueta} | {mil(antes, dec)}{sufijo} |{flecha} **{mil(ahora, dec)}{sufijo}** |"


def main() -> int:
    lineas = ["## Qué cambió", ""]
    hubo = False

    pares = [("tes.json", "Tenedores de TES"), ("gnc.json", "Deuda del GNC"),
             ("externa.json", "Deuda externa")]

    cortes = []
    for archivo, nombre in pares:
        a, b = version_en_git(f"public/data/{archivo}"), actual(archivo)
        if not b:
            continue
        antes = a["dates"][-1] if a else None
        ahora = b["dates"][-1]
        marca = " ← nuevo corte" if antes and antes != ahora else ""
        cortes.append(f"| {nombre} | {antes or '—'} | **{ahora}**{marca} |")
        if antes != ahora:
            hubo = True

    lineas += ["### Cortes", "", "| Serie | Antes | Ahora |", "|---|---|---|"] + cortes + [""]

    # cifras de portada, que son las que se ven de una
    g_a, g_b = version_en_git("public/data/gnc.json"), actual("gnc.json")
    t_a, t_b = version_en_git("public/data/tes.json"), actual("tes.json")
    x_a, x_b = version_en_git("public/data/externa.json"), actual("externa.json")
    m_a, m_b = version_en_git("public/data/meta.json"), actual("meta.json")

    cifras = []
    if g_b:
        ult = lambda d, k: d[k][-1] if d and d.get(k) else None
        cifras.append(fila("Deuda total del GNC (billones COP)", ult(g_a, "copTot"), ult(g_b, "copTot")))
        cifras.append(fila("Deuda interna (billones COP)", ult(g_a, "copInt"), ult(g_b, "copInt")))
        cifras.append(fila("Deuda externa del GNC (billones COP)", ult(g_a, "copExt"), ult(g_b, "copExt")))
    if t_b:
        tot = lambda d: d["series"]["Total general"][-1] / 1e6 if d else None
        cifras.append(fila("TES clase B en circulación (billones COP)", tot(t_a), tot(t_b)))
    if x_b:
        ult = lambda d, k: d[k][-1] if d and d.get(k) else None
        cifras.append(fila("Deuda externa del país (millones USD)", ult(x_a, "total"), ult(x_b, "total"), dec=0))
        cifras.append(fila("Deuda externa (% del PIB)", ult(x_a, "pibTotal"), ult(x_b, "pibTotal"), " %"))
    if m_b:
        cifras.append(fila("TRM", (m_a or {}).get("trm"), m_b.get("trm"), dec=2))
        cifras.append(fila("PIB (billones COP)", (m_a or {}).get("pibCop"), m_b.get("pibCop"), dec=0))

    cifras = [c for c in cifras if c]
    if cifras:
        hubo = True
        lineas += ["### Cifras de portada", "", "| | Antes | Ahora |", "|---|---|---|"] + cifras + [""]

    if not hubo:
        lineas = ["## Sin cambios en los datos", "",
                  "Las fuentes se descargaron pero las cifras son las mismas que ya estaban publicadas."]
    else:
        lineas += ["---", "",
                   "Revisa que los cortes avancen como esperabas y que ninguna cifra dé un salto "
                   "raro. Si algo no cuadra, **no hagas merge**: puede ser una revisión de la fuente "
                   "o un cambio de formato.", "",
                   "El boletín de deuda externa del Banco de la República se actualiza a mano; si "
                   "su corte no se movió, es normal."]

    print("\n".join(lineas))
    return 0


if __name__ == "__main__":
    sys.exit(main())
