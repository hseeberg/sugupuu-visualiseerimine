# Family Migration Map — Reusable Specification

**Goal.** Give a genealogy export (`.md` ahnentafel) → get a single self‑contained **`.html`**
that animates *where family members were born across a map over time*, always with the same design
and interactions. Works for **ancestor** trees (proband → forebears) and **descendant** trees
(progenitor → descendants). This document specifies the solution so it can be reproduced for any tree.

The reference implementation (three scripts) ships alongside this spec in `pipeline/`.

**No family data is hard‑coded in the scripts.** All names, the title, the legend, the branch
colours and the generation labels are **derived from the input `.md`**. Dropping in a different
family produces a correct result for that family — never "someone else's names".
(The only region‑specific asset is the geocoding dictionary + the country map; see §9.)

---

## 1. Output

- One **self‑contained `.html`** file (only external dependency: Google Fonts CDN).
- Renders an SVG map, animated dots (one per ancestor at their birthplace) and transient
  "courier" arcs, with Play / scrub / speed / zoom controls.
- Variants are produced from the **same** template via build flags (see §4.3):
  direction (forward / backward), names / anonymous, language (Estonian / English).

---

## 2. Input format (the `.md` export)

Ahnentafel, one ancestor per line. Example line:

```
3\. [Johannes Seeberg](https://www.geni.com/profile-94116782) b. October 18, 1914, Kõo v, Pilistvere khk, Viljandimaa; d. May 21, 1967, Taagepera, Valga raj
```

Rules the parser relies on:

- **Leading integer = generation.** A `> > >` prefix is cosmetic.
  - *Ancestor tree:* generation 1 = the **proband**; the number grows toward older forebears
    (birth years **decrease**).
  - *Descendant tree:* generation 1 = the **progenitor**; the number grows toward younger
    descendants (birth years **increase**).
- **Name** is the markdown link text (may contain escaped brackets `\[ \]`).
- **URL** is the markdown link target (Geni profile).
- **Birth** = the `b. …` clause up to `;` or end. Year = first 4‑digit number; `circa` /
  `before` / `between` → mark **approximate**. Place = the clause minus the date tokens.
- **Edge rule (key):** each line links to the **nearest preceding line at generation − 1**.
  This is exactly how a depth‑first ahnentafel/descendant chart nests. The engine decides which
  end of every edge is *older* vs *younger* from the **birth years**, so the same rule serves
  both tree types.
- Place and/or year may be **missing** — handled in §4.2.

---

## 3. Pipeline (three scripts, run in order)

```
build_map.py   → map.json      (country outline + islands + lakes)
parse.py       → nodes.json     (parsed, geocoded, inherited, estimated, branch‑tagged)
build_html.py  → <name>.html    (renders the template; flags select the variant)
```

### 4.1 `build_map.py` → `map.json`

- Source: **Natural Earth 10m** `admin_0_countries_lakes` (land, **islands included**) +
  `10m_lakes` for inland/border lakes (here: Lake Peipus, Lake Pskov/Pihkva, Võrtsjärv).
- Output: `{"land":[ring,…], "lakes":[ring,…]}` where a ring is `[[lon,lat],…]`.
- Land rings are drawn white; lake rings are drawn on top in the water tone (so inland lakes
  and the true Peipsi shoreline read correctly).
- **For a different country:** change the country name filter and the lake names; structure is
  unchanged. Islands come for free from the multipolygon.

### 4.2 `parse.py` → `nodes.json`

1. **Parse** each line → `{id, gen, name, url, byear, approx, place, child}`.
2. **Geocode** `place` via a curated `PLACES` dict (village / parish / county → lat,lon).
   - County / country names are **low priority** (fallback only) so a specific village wins.
   - Keys cover **multilingual variants** where needed (Estonian / German / Russian / Cyrillic).
   - Matching is anchored at a **left word boundary**, so a short key can't be grabbed from inside
     a longer name (`"Prassi"` no longer hits the `rassi` key) while case endings still match
     (`"Kõos"`, `"Emmastes"`). This prevents a stray mis‑match seeding a whole subtree via inheritance.
3. **Inherit location (both directions):** a node with no place takes a coordinate from any
   geolocated neighbour — the partner it points to *or* a relative that points to it — so even the
   root / progenitor gets placed (flag `place_inherited`).
4. **Branch tagging:** each node is tagged by the ancestor it descends from at the **branch
   generation** — **gen 3** for ancestor trees (grandparent lines), **gen 2** for descendant
   trees (`--descendants`). Branch‑head **names** are emitted for the legend; gen < branch‑gen = `root`.
5. **Estimate birth year (direction‑aware):** a node with no year is set from a dated neighbour at
   **∓30 yr per generation** — `−30` toward older kin (ancestor trees), `+30` toward younger kin
   (descendant trees). Estimates are **capped at the present year** so chained descendants are
   never "born in the future" (flag `year_estimated`).
6. **Declump (cluster spread) + land‑clamp:** everyone sharing a spot is fanned out on a bounded
   **sunflower spiral** (≤ ~3 km) so zooming separates them into individual dots; any point that
   lands on an island (here Hiiumaa) is forced **inside the island polygon** (point‑in‑polygon,
   keyed to geography, not to a branch). Cross‑border points are left untouched.
7. **Emit** compact `nodes.json`: keys
   `id, g(gen), n(name), u(url), y(display year), ye(year_estimated), lat, lon,
   pi(place_inherited), c(child id), b(branch), ap(approx)`.

### 4.3 `build_html.py [--forward] [--descendants] [--anon] [--en]` → `.html`

Everything family‑specific is **computed from `nodes.json`** and injected — branch colours
(palette assigned by branch order), generation labels, legend rows, page title and ARIA. No
names are hard‑coded in the template.

- `--descendants` — descendant tree; defaults to **forward** (progenitor → today), gen‑2 branches.
- `--forward` — for ancestor trees, run oldest → today (default there is today → oldest).
- `--anon` — strips **all names except the root/proband** and **all Geni URLs** from the data
  (source included); legend uses generic / relationship labels.
- `--en` — post‑processes the remaining UI strings to English (proper place names kept).
- Output filename encodes the flags (e.g. `index_anon_fwd_en.html`, `index_desc.html`).

---

## 5. Design system

- **Material**‑style. Fonts: **Roboto** (UI) + **Roboto Mono** (year / data).
- Light **sea** radial background; **white land** with a soft drop shadow; **lakes** in a
  water tone; Material elevation shadows on cards and the control bar.
- **Branch colours:** UI accents are fixed (root/proband red `#E53935`, middle grey `#455A64`);
  every **branch colour is assigned from a 16‑colour palette in branch order** at build time and
  injected as a `COLORS` map — nothing is keyed to specific family IDs. (A 4‑grandparent ancestor
  tree therefore comes out blue / green / orange / purple as before.)
- **Uncertainty** (estimated year *or* inherited place) → **dashed ring** on the dot.
- **Layout:** big year read‑out top‑left; branch legend top‑right; Material control bar
  bottom‑centre; zoom hint bottom‑left.

---

## 6. Animation model

- Timeline spans `[min_birth − 8 … 2026]`.
- **Direction:** *backward* (today → oldest) or *forward* (oldest → today).
- A node is **present** when its birth year is on the past side of the cursor.
- **Courier arc** per parent→child edge: a quadratic Bézier that **draws from the
  already‑present endpoint to the newly‑born endpoint, then fades out** (transient), leaving
  only the **dot**. The dot **blooms** (short delay, so the arc lands first) where the courier
  arrives and then **persists**. Result over a full run: a growing field of dots, no arc clutter.
- **Instant** dot (no incoming courier) for any node with **no earlier‑appearing neighbour** —
  computed from birth years, so it is correct for both tree types (the proband/root, or a leaf
  with no linked earlier kin).
- Arc colour = the branch colour. The **frontier** (most recently appeared node) drives the
  caption under the year.

---

## 7. Interactions

- **Play / Pause** (FAB). **Default speed 0.5×**; the speed button cycles **0.5× → 1× → 2× → 4×**.
- **Timeline scrubber** — dragging shows/hides dots instantly and suppresses the courier arcs.
- **Restart** to the start of the timeline.
- **Find a person (search):** a search box **at the top of the legend** filters everyone by name;
  hits drop down as a list (name + generation + birth year), non‑matches on the map dim out, and
  clicking a result **flies to that person** (zoom + pan). This is the reliable way to pick one
  individual out of a dense cluster. (Hidden in anonymous builds, since there are no names.)
- **Hover** shows just that one person's name and outlines their dot — so names never pile up.
- **Zoom & pan** (works during Play or Pause):
  - wheel or **pinch** to zoom (1–9×), **drag** to pan, **double‑click** to reset.
  - **Dots keep a constant screen size** while co‑located people are fanned out on a small,
    bounded spiral (≤ ~3 km); zooming in therefore **separates a crowded cluster into individual,
    hoverable dots** without moving anyone far from where they were born.
- **Tooltip** on hover: name (if named), generation, birth year (`~` if estimated),
  "place inherited from a relative" if applicable, and *click → Geni profile* when a URL exists.
- **Geographic reference layer:** well‑known places are drawn in **grey** for orientation —
  regions and waters (HIIUMAA, SAAREMAA, VÕRTSJÄRV, PEIPSI, …) and major cities are always shown;
  **towns appear as you zoom in (≈1.8×) and villages deeper (≈3.6×)**, so a zoomed‑in cluster is
  always readable against nearby town names. Labels sit behind the people and don't intercept
  clicks. (Estonia‑specific list; swap it with the map for another country — see §9.)
- **Legend (top‑right)** holds, top to bottom: the search box, the branch colours (each with its
  branch‑head name, or a relationship label when anonymous), the dashed‑ring note, and the
  zoom/pan controls hint — so nothing floats loose over the map or the play buttons.

---

## 8. Data‑quality & honesty rules

- Coordinates are **parish / village‑level approximate**, not exact farmsteads.
- Inherited places and estimated years are always marked (**dashed ring**).
- Cross‑border births (e.g. Petseri, now in Russia) render **across the border**, not snapped
  back onto the home country.

---

## 9. Reuse checklist (new family tree)

1. Provide the `.md` export — an **ancestor** ahnentafel (gen 1 = proband) or a **descendant**
   chart (gen 1 = progenitor). Same line format either way.
2. **Extend `PLACES`** in `parse.py` with the new tree's villages / parishes — the main manual
   step. The dictionary now covers **all Estonian counties as a low‑priority fallback** (so any
   `"village, County"` at least lands in the right county) plus village‑level detail for the
   Pilistvere, Hiiumaa, Setu and **Läänemaa** clusters; add village coordinates for other regions
   the same way. (Alternative: wire in a geocoding API and cache results into the same dict.)
   `parse.py` prints any unmatched place strings so you can see what to add.
3. If a **different country:** regenerate `map.json` (swap the country filter + lake names in
   `build_map.py`); review the island land‑clamp bbox in `parse.py`; and swap the grey
   **reference‑place list** (`REFPLACES` in `build_html.py`) for that country's cities/regions.
   The projection frame auto‑fits to the data + map.
4. Nothing else is family‑specific: title, legend labels, branch colours and generation names
   are all derived from the data. Branch colouring auto‑tags at the branch generation (gen 3 for
   ancestors, gen 2 for descendants) and generalises to *N* branches (palette has 16 colours;
   extend if you need more).
5. Run the pipeline:

```bash
# ancestor tree, today → oldest (default)
python3 parse.py mytree.md
python3 build_html.py                         # index.html

# ancestor tree, oldest → today, anonymous, English
python3 build_html.py --forward --anon --en   # index_anon_fwd_en.html

# descendant tree (progenitor → descendants; forward by default)
python3 parse.py mytree.md --descendants
python3 build_html.py --descendants           # index_desc.html
```

6. Ship the resulting `.html`.

---

## 10. Known limitations / TODO

- Geocoding is a **curated dictionary** (region‑specific); arbitrary trees need dictionary
  extension or a geocoder. Places it can't resolve fall back to the county centroid or a relative.
- Dense clusters are fanned out (≤ ~3 km) and separate on **zoom**; use **search / hover** to pick
  a specific person. Extremely large single‑parish clusters can still crowd until zoomed in.
- Estimated birth years are ±30 yr/generation guesses (capped at the present); treat as rough.
- The land‑clamp is Estonia/Hiiumaa‑specific; generalise per island for other geographies.
- **Pedigree collapse** / duplicate individuals are rendered as separate dots.
- Lake fill is a flat tone (doesn't follow the sea gradient) — reads as water, but not pixel‑exact.

---

## 11. File manifest (in `pipeline/`)

| File | Role |
|------|------|
| `build_map.py` | Country outline + islands + lakes → `map.json` |
| `parse.py` | Parse + geocode + inherit + estimate + branch‑tag + land‑clamp → `nodes.json`. Takes `<tree.md> [--descendants]` |
| `build_html.py` | Render the template; `--forward` / `--descendants` / `--anon` / `--en` select the variant |
| `map.json` | Prebuilt Estonia outline (islands + lakes) — reuse to skip the download |
| `sample_descendants.md` | Tiny synthetic descendant tree for testing/demo |

Intermediate artefacts: `nodes.json`, `map.json`.

---

*Reference builds delivered with this spec:*

- **Ancestors** (Hannes's tree): named backward (`…_Hannes.html`), named forward (`…_EDASI.html`),
  anonymous backward (`…_ANONYYM.html`), anonymous English backward (`Ancestor_map_ANONYMOUS_EN.html`),
  anonymous English forward (`Ancestors_to_me_ANONYMOUS_EN.html`).
- **Descendants** (synthetic demo): `Descendants_DEMO.html`, `Descendants_DEMO_EN.html`.

All include zoom (wheel / pinch / drag / double‑click reset), names revealed when zoomed in,
and a default speed of 0.5×.
