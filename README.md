# Deuda Colombia

**→ [deudacolombia.site](https://deudacolombia.site)**

Página pública para consultar **quién es dueño de la deuda de Colombia**: quién
tiene los TES, a quién le debe el país por fuera y cómo está compuesta la deuda
del Gobierno Nacional Central. Bilingüe (ES/EN), tema claro y oscuro, sin
dependencias externas en tiempo de ejecución.

Los datos vienen de tres publicaciones oficiales y se actualizan **una vez al
mes**, a fin de mes.

---

## Cómo actualizar los datos cada mes

1. **Descarga las tres publicaciones nuevas** y guárdalas en `fuentes/`
   *conservando exactamente estos nombres* (reemplaza los que están):

   | Archivo en `fuentes/` | Publicación | Dónde se consigue |
   |---|---|---|
   | `tenedores_tes.xlsx` | Histórico de tenedores de TES clase B | MinHacienda / DCV — Banco de la República |
   | `boletin_deuda_externa.xlsx` | Boletín de deuda externa | Banco de la República |
   | `historico_gnc.xlsx` | Datos históricos de la deuda del GNC | MinHacienda — Crédito Público |

2. **Reconstruye los datos**:

```bash
python scripts/build_data.py --trm 3621.86 --pib 1928
```

   `--trm` es la TRM del día de corte del boletín de deuda externa y `--pib` el
   PIB nominal en billones de pesos. Si los omites, se conservan los del mes
   anterior y el script te lo recuerda al terminar.

3. **Revisa el resultado en local**:

```bash
npx serve public
```

4. **Publica**. Al hacer push a `main`, Vercel despliega solo:

```bash
git add -A && git commit -m "Datos a <mes> de <año>" && git push
```

Los títulos, los pies de fuente y los rangos de años de la página **se mueven
solos**: se derivan de las fechas que traen los propios JSON, así que ningún
texto puede quedar desfasado respecto a las gráficas. Lo único que se escribe a
mano cada mes es `--trm` y `--pib`.

### Requisitos

```bash
pip install -r requirements.txt
```

### Comprobación opcional en CI

En `.github/workflows/verificar-datos.yml` hay una acción que reconstruye los
JSON en cada push y falla si no coinciden con los Excel — atrapa el olvido más
probable de la rutina: reemplazar las fuentes y no volver a correr el script.
Está sin publicar porque subir un workflow exige un permiso extra de GitHub.
Para activarla, en una terminal:

```bash
gh auth refresh -s workflow && git add .github && git commit -m "Verificación de datos en CI" && git push
```

---

## Estructura

```
public/                 lo que se publica (Vercel sirve esta carpeta)
  index.html            la página entera: markup, estilos y lógica
  assets/               runtime, React y las fuentes Hanken Grotesk (locales)
  data/                 los cuatro JSON que consume la página
fuentes/                los tres Excel oficiales, tal como los publican
scripts/build_data.py   Excel → JSON
vercel.json             configuración del despliegue
DESIGN-SYSTEM.md        el sistema de diseño de la página
```

La página tiene cuatro vistas, **cada una con su propia URL** — `/`, `/interna`,
`/externa` y `/guia` —, con su título, su descripción y su canónica. Vercel
reescribe esas rutas a `index.html` y el botón atrás del navegador funciona.
Si añades una vista, hay que tocar tres sitios: el mapa `RUTAS`, el objeto
`META` y `public/sitemap.xml`.

Las vistas son: **Total GNC**, **Interna**, **Externa** y
**Guía**. Esta última es el glosario: define los conceptos con su fuente
autorizada, explica por qué importa el nivel de deuda, recoge las notas
metodológicas numeradas y lista las referencias. Los términos subrayados en el
resto del sitio y los numeritos en volandas junto a las cifras enlazan allí.

La página es HTML, CSS y JavaScript planos: **no hay paso de compilación**.
React y las tipografías se sirven desde `assets/`, así que el sitio no hace
ninguna petición a terceros.

### Los datos

| Archivo | Contenido | Unidad |
|---|---|---|
| `data/tes.json` | Saldo de TES por tipo de tenedor, mensual desde 2010 | COP millones |
| `data/externa.json` | Deuda externa bruta del país, mensual desde 2001, más la foto de deudores, acreedores y monedas | USD millones |
| `data/gnc.json` | Deuda del GNC: saldos, fuentes, tasa, moneda, indicadores y perfil de vencimientos | COP millones / USD millones |
| `data/meta.json` | TRM, PIB y fechas de corte | — |

---

## Por qué las tres vistas no se suman

Es la advertencia central de la página y conviene tenerla presente al leer los
datos:

- **Hacienda** clasifica un TES como deuda **interna** aunque lo tenga un
  extranjero — lo que importa es dónde se emitió el título.
- **El Banco de la República** cuenta ese mismo TES como deuda **externa** —
  lo que importa es dónde vive el acreedor.

Por eso el mismo papel aparece en dos cuentas distintas y los totales de las
tres vistas no son sumables entre sí.

Además, los cortes no coinciden: el boletín de deuda externa se publica con unos
dos meses de rezago frente a las otras dos fuentes, así que es normal que la
vista de deuda externa vaya un par de meses atrás.

---

## Notas sobre la construcción de los datos

`scripts/build_data.py` lee los Excel por posición de fila y **verifica las
etiquetas** antes de leer las cifras: si el Ministerio o el Banco cambian el
formato del archivo, el script falla con un mensaje explícito en vez de producir
cifras equivocadas en silencio. También comprueba que la suma de los tenedores
de TES cuadre con el «Total general» publicado, para que ningún tipo de tenedor
nuevo quede fuera de las gráficas.

Al reconstruir los datos desde los Excel actuales aparecieron tres correcciones
frente a la versión anterior de la página:

- En la composición de la deuda interna, **Bonos Fogafín** y **Bonos Ley 546/99**
  estaban intercambiados entre diciembre de 2017 y abril de 2020.
- En los primeros catorce meses de la serie (2001-2002), las columnas de
  **duración** y **vida media** estaban corridas una posición.
- El grupo «Otros tenedores» de TES no incluía **Proveedores de
  Infraestructura**, así que el área apilada no llegaba al total publicado.

### El cambio de metodología de la deuda externa (enero de 2026)

Desde enero de 2026 el Banco de la República publica la deuda externa con una
metodología armonizada con los estándares internacionales, y movió el boletín al
Portal de Estadísticas Económicas. La serie anterior quedó marcada como
**«Datos descontinuados»** y termina en septiembre de 2025.

El cambio no es cosmético. En el último mes comparable, septiembre de 2025:

| Septiembre 2025 | Serie descontinuada | Serie vigente | Diferencia |
|---|---|---|---|
| Total | US$211.584 M | US$236.581 M | +24.997 M |
| Sector público | US$118.135 M | US$143.170 M | +25.035 M |
| Sector privado | US$93.449 M | US$93.411 M | −38 M |
| % del PIB | 48,6 % | 54,1 % | +5,5 pp |

Toda la diferencia está en el sector público; el privado es idéntico. El Banco
**reconstruyó la historia** con la metodología nueva —la revisión de nivel llega
al menos hasta diciembre de 2024—, así que la serie de 25 años no tiene un
escalón artificial en el punto del cambio. La portada de la vista de deuda
externa lleva una nota que explica esto.

Si alguien compara la cifra de la página contra un boletín anterior a septiembre
de 2025 va a ver un hueco de unos 25 mil millones de dólares: son dos
metodologías distintas, no un error.

---

Datos: Ministerio de Hacienda y Crédito Público · Banco de la República.
Esta página no es una publicación oficial.
