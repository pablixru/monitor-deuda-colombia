# Deep Intel — Design System

A portable design brief for building new web pages in the style of Pablo Ruiz
Carrizosa's portfolio. Hand this whole file to an AI (or a designer) and ask it
to build in "the Deep Intel style." It is self-contained: every token, rule and
component recipe needed to reproduce the look lives here.

> **The one-line essence.** Editorial, data-first, dark by default. Layered
> near-blacks, one confident orange, a single grotesk typeface, tight headlines,
> generous space, and restraint everywhere. It should feel like a quiet, precise
> intelligence brief — not a colorful SaaS landing page.

---

## 1. Principles (read these first)

1. **Dark is home; light is a faithful inversion.** The canvas is near-black.
   A light theme exists, built as "light chrome + dark islands": backgrounds,
   text and text-cards invert, but media blocks (figures, code, hero) keep a
   dark frame. Never assume one theme — every color comes from a token so both
   themes work from the same markup.
2. **One accent, used sparingly.** Orange `#ff5c00` marks actions, key trends,
   the current nav item, and one word in the hero. If everything is orange,
   nothing is. Most of the surface is neutral black/ink.
3. **One typeface.** Hanken Grotesk for *everything* — headings, body, labels,
   numbers. No secondary display font. Hierarchy comes from weight, size and
   spacing, not from mixing families. (Monospace appears only inside code blocks.)
4. **Tight, confident type.** Big headlines are heavy and negatively tracked.
   Labels are small, uppercase and widely tracked. The contrast between the two
   carries the design.
5. **Small radii, hairline borders, almost no shadow.** Elevation is expressed
   with *tonal layers* (slightly lighter blacks), not drop shadows. Shadows are
   reserved for genuinely floating things.
6. **Space is a material.** Sections breathe (≈88px vertical rhythm). Text lines
   are capped at ~62 characters. Don't crowd.
7. **Motion is intentional and quiet.** Ease-out expo curves, short durations,
   reveal-on-scroll, one or two marquees. Always honor `prefers-reduced-motion`.
8. **No slop.** No stock gradients-on-text, no glassmorphism by default, no
   identical card grids, no tiny tracked eyebrow above every section, no
   decorative stripes. See §11.

---

## 2. Color

Drop this token block into `:root`. Dark is the default; the `[data-theme="light"]`
block overrides only what changes. Set the theme with a tiny inline script in
`<head>` (before paint) that reads `localStorage.theme` and sets
`document.documentElement.dataset.theme` (default `"dark"`).

```css
:root {
  /* Tonal blacks — elevation without shadows (level 0 → 3) */
  --bg: #0a0a0a;            /* canvas */
  --bg-deep: #0e0e0e;       /* recessed bands (ticker, footer) */
  --surface: #171717;       /* cards */
  --surface-high: #202020;  /* hover / raised panels */
  --surface-glass: rgba(255, 255, 255, 0.03);

  /* Ink (text) — three weights */
  --ink: #e5e2e1;           /* primary text, headings */
  --ink-soft: #b6b2b0;      /* secondary text */
  --ink-faint: #878280;     /* labels, muted, disabled */

  /* Hairlines */
  --line: #2e2c2b;
  --line-soft: #222020;

  /* Accents */
  --accent: #ff5c00;        /* PRIMARY — actions, key trend, current nav */
  --accent-soft: #ffb59a;   /* accent as *text* on dark (kickers, links) */
  --accent-deep: #a73a00;
  --red: #ff5449;           /* negatives, alerts */
  --red-soft: #ffb4a8;
  --blue: #0096fd;          /* tertiary, cool contrast (data viz only) */
  --blue-soft: #a0c9ff;
  --glow: rgba(255, 92, 0, 0.22);

  /* Paper — for figures/charts that sit on a light card inside the dark site */
  --paper-hi: #f4f2f0;
  --paper-lo: #e9e6e3;

  /* Type */
  --font-body: "Hanken Grotesk", -apple-system, "Segoe UI", sans-serif;
  --font-code: Consolas, "Cascadia Mono", monospace; /* code blocks only */

  /* Space & shape */
  --sp-1: 8px; --sp-2: 16px; --sp-3: 28px; --sp-4: 48px; --sp-5: 88px;
  --maxw: 1680px;
  --pad-x: clamp(24px, 4vw, 56px);
  --measure: 62ch;
  --radius: 8px;
  --radius-sm: 4px;

  /* Motion */
  --ease: cubic-bezier(0.16, 1, 0.3, 1);  /* ease-out, exponential feel */
  --dur-fast: 0.22s; --dur-med: 0.4s; --dur-slow: 0.85s;

  /* Shadow — floating elements only */
  --shadow: 0 4px 12px rgba(0, 0, 0, 0.5);
  --shadow-lift: 0 12px 32px -8px rgba(0, 0, 0, 0.6);
}

:root[data-theme="light"] {
  --bg: #f5f4f2; --bg-deep: #eceae7;
  --surface: #ffffff; --surface-high: #f1efec;
  --surface-glass: rgba(0, 0, 0, 0.03);
  --ink: #1b1a19; --ink-soft: #46433f; --ink-faint: #6d6763;
  --line: #dbd7d3; --line-soft: #e7e3df;
  --accent-soft: #b8420a;   /* deep orange stays legible on light */
  --red: #d23a2e; --red-soft: #b0342a;
  --blue: #0a72c9; --blue-soft: #135f9e;
  --glow: rgba(255, 92, 0, 0.16);
  --shadow: 0 4px 14px rgba(23, 20, 18, 0.10);
  --shadow-lift: 0 14px 34px -10px rgba(23, 20, 18, 0.16);
}
```

**Usage rules**
- `--accent` (`#ff5c00`) is a *fill* color (buttons, the active nav pill, a data
  line). For accent **text** use `--accent-soft` — it's legible on both themes
  (light peach on dark, deep burnt-orange on light). Never put `#ff5c00` text on
  black; it fails contrast.
- Body text must clear 4.5:1. Prefer `--ink`/`--ink-soft` for anything you must
  read; `--ink-faint` is for labels and decoration only.
- `--blue` is a *data-viz* color (a second series), not a UI color. Don't make
  links or buttons blue.
- **"Dark islands" in light theme:** figures, code blocks and the hero re-declare
  the dark tokens inside themselves so their media reads correctly on a light
  page. If you add a media block, give it the dark token set locally.

---

## 3. Typography

**One family: Hanken Grotesk.** Load 400/500/600/700/800 (+ italic 400/600):

```html
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Hanken+Grotesk:ital,wght@0,400;0,500;0,600;0,700;0,800;1,400;1,600&display=swap" rel="stylesheet">
```

| Role | Size | Weight | Tracking | Notes |
|---|---|---|---|---|
| **Hero / display** | `clamp(3.2rem, 9.6vw, 9.4rem)` | 800 | `-0.045em` | line-height `0.95`; one word in `--accent`. Ceiling ~9.4rem — never bigger. |
| **H2 (section)** | `clamp(1.8rem, 2.7vw, 2.7rem)` | 700–800 | `-0.025em` | paired with a rule + `§` index (see §7). |
| **H3** | ~1.15–1.25rem | 700 | `-0.015em` | card / group titles. |
| **Lede** | `clamp(1.1rem, 1.6vw, 1.5rem)` | 600 | `-0.01em` | intro paragraph under a heading. |
| **Body** | 1rem (~16px) | 400–500 | normal | line-height 1.5–1.6, `max-width: var(--measure)`. |
| **Kicker / label** | 0.7–0.92rem | 600 | `0.22em`, UPPERCASE | color `--accent-soft` or `--ink-faint`. |
| **Micro / tag** | 0.72rem | 600–700 | `0.04em` | tags, ticker terms. |

Rules:
- Use `text-wrap: balance` on h1–h3; `text-wrap: pretty` on long body.
- Display tracking floor is `-0.045em` here (brand choice — it's heavy Grotesk).
  Don't go tighter, and don't loosen big headings toward 0.
- Numbers are set in the same font (no tabular mono for figures unless in a table).

---

## 4. Layout & spacing

- Page max width `--maxw` (1680px); gutters `--pad-x` (`clamp(24px,4vw,56px)`).
  A `.wrap` centers content: `max-width:var(--maxw); margin:0 auto; padding:0 var(--pad-x)`.
- Vertical rhythm: sections use `padding: 88px 0` (`--sp-5`); a hairline
  `border-top: 1px solid var(--line-soft)` separates stacked sections.
- Text column capped at `--measure` (62ch).
- Radii: `--radius` (8px) for cards/figures, `--radius-sm` (4px) for small
  controls, `999px` for pills (nav, "more" buttons, toggles), 9–11px for logo
  chips. Nothing rounder — no 24px+ blobs.
- Responsive: prefer fluid `clamp()` over breakpoints. Grids collapse to 1
  column on small screens. Test copy at 320 / 375 / 768 / 1280+.

---

## 5. Motion

- Curve: `--ease: cubic-bezier(0.16, 1, 0.3, 1)` (ease-out, exponential). No
  bounce, no elastic.
- Durations: `--dur-fast` (0.22s) for hovers, `--dur-med` (0.4s) for reveals /
  toggles, `--dur-slow` (0.85s) for big entrances.
- **Reveal on scroll:** elements get a `.reveal` class that starts
  `opacity:0; translateY(~16px)` and animates in when they enter the viewport
  (IntersectionObserver), optionally staggered (`.reveal-delay-1/2`). The
  content must be visible by default if JS/observer never runs (don't gate real
  content on a class that might not fire).
- **Marquees** (see §7) loop by rendering the set twice and translating the
  track `-50%`; pause on hover.
- Every animation needs a `@media (prefers-reduced-motion: reduce)` fallback
  (kill the transform/animation, keep the end state).

---

## 6. Elevation

Express raised surfaces with **tonal layers**, not shadows:
`--bg` → `--surface` → `--surface-high`. Use `--shadow` / `--shadow-lift` only
for things that truly float (a slider knob, a lifted card on hover, a figure on
a light page). Never pair a 1px border *and* a big soft shadow on the same
element — pick one.

---

## 7. Component recipes

**Sticky header — pill nav.** Translucent header (`rgba(10,10,10,.78)` +
`backdrop-filter: blur(16px)`), hairline bottom border. Nav links live in a
"liquid-glass" pill: a rounded-999px container with a faint inner highlight;
the current page is a solid `--accent` pill with near-black text. On the right:
a language slider, a theme slider, a "Download CV"/CTA outline button. On mobile
(≤880px) the links collapse into a dropdown behind a hamburger; the brand becomes
logo-only under ~430px so the row fits.

**Sliding toggles (theme & language).** A 28px-tall pill "switch": a knob
(`background: var(--ink)`) slides between two ends; the *active* end's icon/label
sits on the knob in `--bg` (max contrast), the inactive one is `--ink-faint`.
Theme toggle = sun/moon icons (52×28); language toggle = ES/EN labels (58×28),
driven by `html[lang]`, and is actually a link to the other language. Both honor
reduced-motion (no knob slide).

**Buttons.**
```css
.btn { display:inline-flex; align-items:center; gap:9px; padding:13px 24px;
  border-radius:var(--radius-sm); font-weight:650; font-size:.93rem;
  border:1px solid transparent; transition: all var(--dur-med) var(--ease); }
.btn-primary { background:var(--accent); color:#140800; }
.btn-primary:hover { background:#ff7a2e; transform:translateY(-2px);
  box-shadow:0 10px 30px -10px var(--glow); }
.btn-outline { border-color:var(--line); color:var(--ink);
  background:rgba(255,255,255,.02); }
.btn-outline:hover { border-color:var(--accent); color:var(--accent-soft);
  background:rgba(255,92,0,.06); transform:translateY(-2px); }
```
When several CTAs sit together, give them equal width (`min-width`) and center
their content so the row reads as a set.

**Section head.** Title + a flexible hairline rule + a small `§ 03` index, on
one baseline:
```css
.section-head { display:flex; align-items:baseline; justify-content:space-between;
  gap:26px; margin-bottom:44px; flex-wrap:wrap; }
.section-head::after { content:""; order:1; flex:1 1 60px; height:1px;
  background:var(--line-soft); align-self:center; }         /* the rule */
.section-head .index { color:var(--accent); font-size:.85rem; letter-spacing:.14em; }
```
`§ 0N` numbers are a deliberate, whole-site sequence — not an eyebrow on every
block.

**Kicker.** `text-transform:uppercase; letter-spacing:.22em; font-size:.92rem;
font-weight:600; color:var(--accent-soft)`. Used once at the top of a page/hero,
not above every section.

**"More" / pill link.** Rounded-999px, faint accent tint:
`padding:9px 18px; color:var(--accent-soft); background:rgba(255,92,0,.09);
border:1px solid rgba(255,92,0,.34)`.

**Tags / chips.** Tiny 2px-radius outlined tags for keywords:
```css
.tag { font-size:.72rem; padding:4px 10px; border:1px solid var(--line);
  border-radius:2px; color:var(--ink-soft); background:rgba(255,255,255,.02);
  letter-spacing:.04em; }
.tag-accent { border-color:rgba(255,92,0,.5); color:var(--accent-soft);
  background:rgba(255,92,0,.09); }
```

**Cards / panels.** `--surface` background, `--line` border, `--radius`, generous
padding; on hover lift to `--surface-high` (± a small `translateY` + `--shadow`).
Avoid identical repeating card grids; vary content and size. Never nest cards.

**Figures / "exhibit".** Charts sit on a warm paper card so they read on the dark
canvas: `background:linear-gradient(160deg,var(--paper-hi),var(--paper-lo));
border:1px solid var(--line); border-radius:var(--radius); box-shadow:var(--shadow)`.
Generate the charts themselves in the SAME typeface (Hanken Grotesk) with a
matching palette (orange primary series, muted grays, blue/red secondaries) so
figures feel native, not pasted.

**Marquee (logos or terms).** Overflow-hidden strip with an edge fade
(`mask-image: linear-gradient(90deg, transparent, #000 7%, #000 93%, transparent)`),
a flex track animated `translateX(0 → -50%)`, set duplicated twice, `pause on
hover`. For platform *logos*, each sits in a small light chip (needed so dark/
colored logos read on black): height ~44–62px, `background:#f3f1ed` (dark) /
`#fff` (light), radius ~10px, soft shadow, logo ~21–29px tall. Government seals /
baked-background logos that don't reduce cleanly are shown as text chips instead.

**Category summary (typographic, no boxes).** For grouping without heavy cards:
a 3-col grid where each column is just a hairline top-border + an H3 + a one-line
description (`--ink-soft`) + a sources line in `--accent-soft`. Clean, editorial,
collapses to 1 column ≤760px.

**CTA band.** One full-width orange gradient block near the page end:
`background:linear-gradient(115deg,var(--accent),#e04c00 55%,var(--accent-deep))`,
radius `calc(var(--radius)+4px)`, big padding, headline + button. Use at most one
per page. In light mode, brighten it slightly so it doesn't go muddy.

**Footer.** Recessed `--bg-deep` band, compact columns (nav / channels / CV),
the brand mark + name, a short "Built with HTML, CSS and data." line. shadcn-ish
restraint — no newsletter, no clutter.

**Ticker (optional).** A thin `--bg-deep` band of small uppercase tracked terms
separated by an accent `/`, slowly scrolling — used for "methods & data" flavor.

---

## 8. Voice & content

- Editorial and precise. Short, concrete claims; real numbers; no hype words,
  no "revolutionary/seamless/cutting-edge." Say the specific thing.
- Bilingual by default: Spanish is primary, English lives under `/en/` as a real
  mirror (same structure, faithful translation, a language toggle that links
  counterpart↔counterpart). Keep proper nouns; translate the rest 1:1.
- Labels are calm nouns ("Featured work", "At a glance", "Topics I can discuss"),
  not marketing verbs.
- Accessibility is content: real alt text, visible focus rings
  (`outline:2px solid var(--accent); outline-offset:2px`), a skip link, semantic
  landmarks. Decorative strips (marquees) are `aria-hidden` with the real info
  available elsewhere.

---

## 9. Starter skeleton

```html
<!DOCTYPE html>
<html lang="es" class="no-js">
<head>
  <meta charset="UTF-8">
  <script>(function(){try{var t=localStorage.getItem("theme");if(t!=="light"&&t!=="dark")t="dark";document.documentElement.setAttribute("data-theme",t);}catch(e){}})();</script>
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>…</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Hanken+Grotesk:ital,wght@0,400;0,500;0,600;0,700;0,800;1,400;1,600&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="style.css">   <!-- the :root block from §2 + components -->
</head>
<body>
  <a class="skip-link" href="#main">Skip to content</a>
  <header class="site-header"> … pill nav + toggles … </header>
  <main id="main"> … sections (.wrap, .section-head, .reveal) … </main>
  <footer class="site-footer"> … </footer>
</body>
</html>
```

Base rules to set once: `*{box-sizing:border-box}`,
`body{background:var(--bg); color:var(--ink); font-family:var(--font-body); -webkit-font-smoothing:antialiased}`,
`body{overflow-x:hidden}`, images `max-width:100%`, a semantic z-index scale
(dropdown < sticky < modal < toast < tooltip — never 9999).

---

## 10. Build & verify

- Static HTML/CSS/vanilla JS, no build step. Deployable as flat files.
- Verify every change in **both themes** and at 320 / 375 / 768 / 1280px, and
  with reduced-motion on. Check body text contrast ≥4.5:1 in both themes.

---

## 11. Do / Don't

**Do**
- Start dark; make light a token inversion.
- Let one orange carry the accent; keep the rest neutral.
- One typeface, hierarchy by weight/size/tracking.
- Tonal layers for depth; hairlines for separation.
- Big generous space; capped line length.
- Quiet ease-out motion with reduced-motion fallbacks.

**Don't**
- ❌ Gradient-filled text (`background-clip:text`). Emphasis = weight/size/color.
- ❌ Glassmorphism as decoration (the nav's subtle blur is the only place).
- ❌ Side-stripe borders (`border-left` accent) on cards/callouts.
- ❌ Identical repeating icon+heading+text card grids; nested cards.
- ❌ A tiny uppercase tracked eyebrow above *every* section (kicker is once).
- ❌ Numbered `01/02/03` markers unless it's a real sequence (the `§` index is
  the one deliberate exception).
- ❌ Over-rounded corners (24px+ blobs), or a 1px border **and** a heavy shadow
  together.
- ❌ Accent (`#ff5c00`) text on black (use `--accent-soft`); light-gray body text
  on tinted near-white (fails contrast).
- ❌ Headline copy that overflows its container at any breakpoint.
- ❌ Multicolor logo walls on the dark canvas — if you must show third-party
  logos, put them on small light chips or render them monochrome.

---

*This system is realized in this repo's `assets/css/style.css` (`:root` tokens)
and pages. The auto-generated Material-3 token export in `DESIGN.md` is a
secondary reference; the values above are the ones actually in use.*
