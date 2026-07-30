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


def meses_entre(a: str, b: str) -> int:
    ya, ma = (int(x) for x in a.split("-"))
    yb, mb = (int(x) for x in b.split("-"))
    return (yb - ya) * 12 + (mb - ma)


def revisar_anomalias(pares) -> list[str]:
    """Busca señales de que la actualización no es rutinaria.

    Un mes normal mueve el corte un puesto y las cifras un poco. Si algo se sale
    de eso —una serie que pierde meses, un corte que salta, una cifra que da un
    brinco— vale más que lo mire una persona antes de publicarlo.
    """
    avisos = []
    for archivo, nombre in pares:
        a, b = version_en_git(f"public/data/{archivo}"), actual(archivo)
        if not a or not b:
            continue

        if len(b["dates"]) < len(a["dates"]):
            avisos.append(f"**{nombre}** perdió meses: pasó de {len(a['dates'])} a {len(b['dates'])}.")

        salto = meses_entre(a["dates"][-1], b["dates"][-1])
        if salto < 0:
            avisos.append(f"**{nombre}**: el corte retrocedió, de {a['dates'][-1]} a {b['dates'][-1]}.")
        elif salto > 2:
            avisos.append(f"**{nombre}**: el corte saltó {salto} meses, de {a['dates'][-1]} a {b['dates'][-1]}.")

        # saltos bruscos en las series de portada
        series = {"gnc.json": ["copTot", "copInt", "copExt"],
                  "externa.json": ["total", "pub", "priv"]}.get(archivo, [])
        for clave in series:
            va, vb = a.get(clave), b.get(clave)
            if not va or not vb or va[-1] in (None, 0) or vb[-1] is None:
                continue
            cambio = abs(vb[-1] - va[-1]) / abs(va[-1]) * 100
            if cambio > 12:
                avisos.append(f"**{nombre}** · `{clave}` cambió {cambio:.1f} % "
                              f"({va[-1]:,.1f} → {vb[-1]:,.1f}).")

    a, b = version_en_git("public/data/tes.json"), actual("tes.json")
    if a and b and len(b["series"]) != len(a["series"]):
        avisos.append(f"**Tenedores de TES**: cambió el número de grupos, "
                      f"de {len(a['series'])} a {len(b['series'])}.")
    return avisos


def main() -> int:
    verificar = "--verificar" in sys.argv
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

    avisos = revisar_anomalias(pares) if hubo else []

    if not hubo:
        lineas = ["## Sin cambios en los datos", "",
                  "Las fuentes se descargaron pero las cifras son las mismas que ya estaban publicadas."]
    elif avisos:
        lineas += ["---", "", "### Por qué esto no se publicó solo", ""]
        lineas += [f"- {a}" for a in avisos]
        lineas += ["", "Puede ser una revisión legítima de la fuente o un cambio de formato. "
                       "Compruébalo antes de hacer merge.", "",
                   "El boletín de deuda externa se actualiza a mano; si su corte no se movió, es normal."]
    else:
        lineas += ["---", "",
                   "Cambio rutinario: los cortes avanzaron como se esperaba y ninguna cifra dio un "
                   "salto brusco.", "",
                   "El boletín de deuda externa se actualiza a mano; si su corte no se movió, es normal."]

    print("\n".join(lineas))

    # 0 = no hay nada que hacer · 1 = rutinario, se puede publicar · 2 = que lo mire alguien
    if verificar:
        return 0 if not hubo else (2 if avisos else 1)
    return 0


if __name__ == "__main__":
    sys.exit(main())
