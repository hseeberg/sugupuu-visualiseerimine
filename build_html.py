#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json, sys, re
nodes = json.load(open("nodes.json", encoding="utf-8"))
mapd  = json.load(open("map.json",  encoding="utf-8"))

ANON = '--anon' in sys.argv
DESC = ('--descendants' in sys.argv) or ('--desc' in sys.argv)   # descendant tree
EN   = '--en' in sys.argv
FWD  = ('--forward' in sys.argv) or (DESC and '--backward' not in sys.argv)  # descendants default forward

N = nodes['nodes']
by = {n['id']: n for n in N}
root = by.get(0) or N[0]
root_name = root.get('n') or ''
maxgen = max(n['g'] for n in N)
branch_gen = 3
if any(k.startswith('g2_') for k in nodes['branches']): branch_gen = 2   # parse.py chose the branch generation

if ANON:
    for n in N:
        n['u'] = ''
        if n['id'] != 0: n['n'] = ''      # keep only the root/proband name
    nodes['branches'] = {k: '' for k in nodes['branches']}

# ---- colours: fixed accents + palette assigned to branches in tree order ----
PALETTE = ['#1E88E5','#2E9E5B','#F57C00','#8E24AA','#00897B','#C62828',
           '#5E35B1','#00838F','#9E9D24','#6D4C41','#3949AB','#AD1457',
           '#43A047','#039BE5','#FF7043','#7E57C2']
branch_ids = sorted(nodes['branches'].keys(), key=lambda k: int(k.split('_')[1]))
COLORS = {'me':'#E53935','root':'#455A64'}
for i,b in enumerate(branch_ids): COLORS[b] = PALETTE[i % len(PALETTE)]

# ---- generation names (mode + language) ----
def gen_label(g):
    if DESC:
        base = ({1:'Progenitor',2:'Child',3:'Grandchild',4:'Great-grandchild'} if EN
                else {1:'Tüviisik',2:'Laps',3:'Lapselaps',4:'Lapselapselaps'})
        if g in base: return base[g]
        return (f'{g-2}× great-grandchild' if EN else f'{g-2}× lapselaps')
    else:
        base = ({1:'Root person',2:'Parent',3:'Grandparent',4:'Great-grandparent'} if EN
                else {1:'Lähteisik',2:'Vanem',3:'Vanavanem',4:'Vaarvanem'})
        if g in base: return base[g]
        return (f'{g-3}× great-grandparent' if EN else f'{g-3}× vaarvanem')
GENMAP = {g: gen_label(g) for g in range(1, maxgen+1)}

# ---- legend (data-driven) ----
grey_exists = any(n.get('b')=='root' and n['id']!=0 for n in N)
def branch_label(i, bid):
    if not ANON:
        return nodes['branches'].get(bid) or (('Branch ' if EN else 'Haru ')+str(i+1))
    # anonymous: no names. Standard 4-grandparent ancestor tree -> relationship by order.
    if not DESC and branch_gen==3 and len(branch_ids)==4:
        rel_et = ['Isa isa liin','Isa ema liin','Ema isa liin','Ema ema liin']
        rel_en = ['Paternal grandfather line','Paternal grandmother line',
                  'Maternal grandfather line','Maternal grandmother line']
        return (rel_en if EN else rel_et)[i]
    return ('Branch ' if EN else 'Haru ')+str(i+1)

legend = []
# root / proband row
root_label = root_name if (root_name and not ANON) else GENMAP.get(1, '')
legend.append(['me', root_label, GENMAP.get(1,'')])
# middle grey generations (e.g. parents in an ancestor tree)
if grey_exists:
    legend.append(['root', ('Parents' if EN else 'Vanemad'), '—'])
# one row per branch
for i,bid in enumerate(branch_ids):
    legend.append([bid, branch_label(i,bid), GENMAP.get(branch_gen,'')])

# ---- title / aria (no family data unless a name is intentionally shown) ----
if ANON or not root_name:
    TITLE = 'Family tree map' if EN else 'Sugupuu kaardil'
else:
    TITLE = f'{root_name} · ' + ('family tree' if EN else 'sugupuu')
ARIA = 'Animated family tree map' if EN else 'Animeeritud sugupuu kaardil'

LEGEND = json.dumps(legend, ensure_ascii=False, separators=(",", ":"))
# ---- geographic reference labels (grey) so you stay oriented when zoomed in ----
# [name, lat, lon, tier]  tier 0=region/water, 1=major city, 2=town, 3=village
REFPLACES = [
    ["HIIUMAA",58.87,22.60,0],["SAAREMAA",58.45,22.55,0],["MUHU",58.61,23.20,0],
    ["PEIPSI järv",58.70,27.45,0],["VÕRTSJÄRV",58.28,26.03,0],["LÄÄNEMERI",58.30,22.00,0],
    ["SOOME LAHT",59.62,24.6,0],
    ["Tallinn",59.437,24.754,1],["Tartu",58.378,26.729,1],["Pärnu",58.386,24.497,1],
    ["Narva",59.377,28.19,1],["Viljandi",58.364,25.590,1],["Rakvere",59.346,26.356,1],
    ["Kuressaare",58.253,22.485,1],["Kärdla",58.998,22.749,1],["Võru",57.834,27.019,1],
    ["Valga",57.777,26.047,1],["Haapsalu",58.943,23.541,1],["Paide",58.885,25.557,1],
    ["Jõhvi",59.359,27.421,1],["Põlva",58.060,27.069,1],["Jõgeva",58.746,26.394,1],
    ["Rapla",59.007,24.792,1],["Kohtla-Järve",59.396,27.273,1],
    ["Türi",58.808,25.432,2],["Põltsamaa",58.653,25.972,2],["Elva",58.222,26.421,2],
    ["Otepää",58.058,26.497,2],["Räpina",58.098,27.463,2],["Mustvee",58.849,26.94,2],
    ["Sillamäe",59.390,27.755,2],["Kiviõli",59.353,26.97,2],["Tapa",59.261,25.958,2],
    ["Sindi",58.401,24.66,2],["Lihula",58.680,23.843,2],["Märjamaa",58.905,24.017,2],
    ["Kehra",59.336,25.324,2],["Keila",59.303,24.413,2],["Maardu",59.476,25.025,2],
    ["Tõrva",58.003,25.933,2],["Antsla",57.824,26.542,2],["Kallaste",58.658,27.163,2],
    ["Vändra",58.653,25.033,2],["Käina",58.828,22.78,2],["Suure-Jaani",58.536,25.470,2],
    ["Võhma",58.632,25.553,2],["Kilingi-Nõmme",58.126,24.966,2],["Karksi-Nuia",58.106,25.56,2],
    ["Loksa",59.578,25.717,2],["Kunda",59.500,26.541,2],["Väike-Maarja",59.121,26.247,2],
    ["Pilistvere",58.723,25.730,3],["Kõo",58.664,25.762,3],["Kabala",58.770,25.545,3],
    ["Emmaste",58.717,22.62,3],["Kassari",58.803,22.833,3],["Värska",57.950,27.633,3],
    ["Saatse",57.850,27.470,3],["Obinitsa",57.780,27.420,3],
]
REFJ = json.dumps(REFPLACES, ensure_ascii=False, separators=(",", ":"))
COLORSJ = json.dumps(COLORS, ensure_ascii=False, separators=(",", ":"))
GENMAPJ = json.dumps(GENMAP, ensure_ascii=False, separators=(",", ":"))
DATA = json.dumps(nodes, ensure_ascii=False, separators=(",", ":"))
MAP  = json.dumps(mapd,  ensure_ascii=False, separators=(",", ":"))

HTML = r"""<!DOCTYPE html>
<html lang="et">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>__TITLE__</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;500;700&family=Roboto+Mono:wght@400;500;700&family=Roboto+Flex:opsz,wght@8..144,300..800&display=swap" rel="stylesheet">
<style>
  :root{
    /* Material palette */
    --sea:#DCE3E8; --sea2:#CDD8DF; --land:#F7F9FA; --land-line:#9FB0BA;
    --lake:#D3DCE2; --lake-line:#B4C2CB;
    --surface:#ECEFF1; --on-surface:#263238; --muted:#607D8B;
    --bar:#FFFFFF; --scrim:rgba(38,50,56,.14);
    --b-root:#455A64;   --b-me:#E53935;   /* UI accents; branch colours come from data (COLORS) */
    --elev1:0 1px 2px rgba(0,0,0,.14),0 1px 3px rgba(0,0,0,.10);
    --elev2:0 2px 4px rgba(0,0,0,.16),0 3px 8px rgba(0,0,0,.12);
    --elev3:0 6px 10px rgba(0,0,0,.18),0 10px 24px rgba(0,0,0,.16);
  }
  *{box-sizing:border-box}
  html,body{height:100%;margin:0}
  body{
    font-family:"Roboto","Roboto Flex",system-ui,sans-serif;
    background:var(--surface); color:var(--on-surface);
    overflow:hidden; -webkit-font-smoothing:antialiased;
  }
  #stage{position:fixed; inset:0}
  svg#map{display:block; width:100%; height:100%; cursor:grab; touch-action:none; background:
     radial-gradient(120% 120% at 50% 0%, var(--sea) 0%, var(--sea2) 100%);}
  svg#map:active{cursor:grabbing;}
  .land{fill:var(--land); stroke:var(--land-line); stroke-width:.8; stroke-linejoin:round;
        vector-effect:non-scaling-stroke;
        filter:drop-shadow(0 2px 4px rgba(38,50,56,.12));}
  /* geographic reference labels (grey), behind the people */
  .ref{ pointer-events:none; }
  .ref text{ paint-order:stroke; stroke:#F7F9FA; stroke-width:3px; stroke-linejoin:round;
        font-family:"Roboto",sans-serif; }
  .ref.t0 text{ fill:#AEB9C0; font-weight:700; font-size:13px; letter-spacing:2px; font-style:italic; }
  .ref.t1 text{ fill:#78909C; font-weight:600; font-size:12px; }
  .ref.t2 text{ fill:#90A4AE; font-weight:500; font-size:11px; opacity:0; transition:opacity .2s; }
  .ref.t3 text{ fill:#9AA7AF; font-weight:500; font-size:10px; opacity:0; transition:opacity .2s; }
  .ref circle{ fill:#B0BEC5; }
  #gRef.z2 .ref.t2 text{ opacity:1; }
  #gRef.z4 .ref.t3 text{ opacity:1; }
  .lake{fill:var(--lake); stroke:var(--lake-line); stroke-width:.6; stroke-linejoin:round;
        vector-effect:non-scaling-stroke;}

  /* connector = courier: draws from child to the ancestor's birthplace, then vanishes */
  .link{fill:none; stroke-width:1.7; opacity:0; vector-effect:non-scaling-stroke;
        stroke-dasharray:1; stroke-dashoffset:1;}
  .link.on{ animation:deliver 1.25s cubic-bezier(.4,0,.2,1) forwards; }
  @keyframes deliver{
    0%   { stroke-dashoffset:1; opacity:0; }
    12%  { opacity:.7; }
    55%  { stroke-dashoffset:0; opacity:.7; }   /* fully arrived */
    100% { stroke-dashoffset:0; opacity:0; }     /* courier fades away */
  }

  /* dot = permanent marker left where the arc lands; it stays forever.
     grow via transform scale (CSS 'r' would override the r attribute → invisible) */
  .node circle.dot{ opacity:0; transform:scale(0);
        transform-box:fill-box; transform-origin:center;
        transition:transform .42s cubic-bezier(.2,.7,.3,1.55), opacity .3s; cursor:pointer;
        stroke:#fff; stroke-width:1.5;}
  .node.on circle.dot{ opacity:1; transform:scale(1);
        transition:transform .42s cubic-bezier(.2,.7,.3,1.55) .66s, opacity .3s .66s; }
  .node.on.nolink circle.dot{ transition-delay:0s; }    /* root/proband: no arc → instant */
  .node circle.pulse{ r:0; opacity:0; fill:none; stroke-width:2; pointer-events:none;}
  .node.on circle.pulse{ animation:pulse .8s ease-out .64s 1;}
  .node.on.nolink circle.pulse{ animation-delay:0s;}

  /* while dragging the slider, skip courier arcs — just show/hide the dots */
  .scrub .link{ animation:none!important; opacity:0!important; }
  .scrub .node.on circle.dot{ transition-delay:0s!important; }
  .scrub .node.on circle.pulse{ animation:none!important; }
  @keyframes pulse{ 0%{r:3;opacity:.55} 100%{r:26;opacity:0} }
  .node.est circle.dot{ stroke-dasharray:2.2 2.2; } /* estimated year/place */
  .node .lbl{ font:500 11px/1 "Roboto",sans-serif; fill:var(--on-surface);
        paint-order:stroke; stroke:#fff; stroke-width:3.4px; stroke-linejoin:round;
        opacity:0; transition:opacity .3s; pointer-events:none; }
  .node.on.key .lbl{ opacity:1; }
  .node.match .lbl{ opacity:1; font-weight:700; }              /* search hit: show name */
  .node:hover .lbl{ opacity:1; }                               /* hover: show this one name */
  .node:hover circle.dot{ stroke:#263238; stroke-width:2; }
  .node.match circle.dot{ stroke:#111; stroke-width:2.5; }
  #gNodes.searching .node:not(.match){ opacity:.12; }
  #gNodes.searching .node.match{ opacity:1; }

  #search{ position:relative; margin-bottom:10px; }
  #search input{ width:100%; box-sizing:border-box; font:400 13px "Roboto",sans-serif;
        padding:8px 11px; border:1px solid #CBD3D8; border-radius:9px; outline:none; background:#F7F9FA;}
  #search input:focus{ border-color:var(--b-me); background:#fff;}
  #results{ position:absolute; top:100%; left:0; right:0; margin-top:5px; z-index:6;
        display:none; flex-direction:column; gap:3px; max-height:44vh; overflow:auto;
        background:var(--bar); border-radius:10px; box-shadow:var(--elev2); padding:5px;}
  #results.show{ display:flex; }
  #results button{ text-align:left; font:400 12.5px "Roboto",sans-serif; padding:6px 10px;
        border:none; background:#F2F5F6; border-radius:7px; cursor:pointer; color:var(--on-surface);}
  #results button:hover{ background:#E6EBED; }
  #results button .sub{ color:var(--muted); font-size:11px; }

  /* year read-out (top-left) */
  #hud{ position:fixed; top:0; left:0; padding:18px 22px; pointer-events:none;
        text-shadow:0 1px 2px rgba(255,255,255,.6);}
  #year{ font-family:"Roboto Mono",monospace; font-weight:700;
        font-size:clamp(44px,9vw,88px); line-height:.9; letter-spacing:-.01em;
        color:var(--on-surface); font-variant-numeric:tabular-nums;}
  #phase{ margin-top:6px; font:500 14px/1.3 "Roboto",sans-serif; color:var(--muted);
        max-width:min(60vw,420px);}
  #phase b{color:var(--on-surface); font-weight:700;}
  #count{ margin-top:2px; font:400 13px "Roboto Mono",monospace; color:var(--muted);}

  /* legend (top-right) */
  #legend{ position:fixed; top:14px; right:14px; background:var(--bar);
        border-radius:14px; box-shadow:var(--elev2); padding:12px 14px 11px;
        font-size:12px; max-width:230px;}
  #legend h4{margin:0 0 8px; font:700 12px/1 "Roboto",sans-serif; letter-spacing:.06em;
        text-transform:uppercase; color:var(--muted);}
  #legend .row{display:flex; align-items:center; gap:9px; margin:6px 0; line-height:1.15;}
  #legend .sw{width:13px;height:13px;border-radius:50%;flex:0 0 auto;box-shadow:var(--elev1);}
  #legend .sub{color:var(--muted); font-size:11px;}
  #legend .note{margin-top:9px;padding-top:8px;border-top:1px solid #E0E4E7;
        color:var(--muted);font-size:11px;line-height:1.35;}
  #legend .note .ring{display:inline-block;width:9px;height:9px;border-radius:50%;
        border:1.5px dashed var(--muted);vertical-align:-1px;margin:0 2px;}

  /* bottom control bar */
  #controls{ position:fixed; left:50%; bottom:max(16px,env(safe-area-inset-bottom));
        transform:translateX(-50%); display:flex; align-items:center; gap:14px;
        background:var(--bar); border-radius:36px; box-shadow:var(--elev3);
        padding:10px 18px 10px 10px; width:min(680px,calc(100vw - 28px));}
  #play{ flex:0 0 auto; width:56px;height:56px;border:none;border-radius:50%;
        background:var(--b-me); color:#fff; cursor:pointer; box-shadow:var(--elev2);
        display:grid;place-items:center; transition:transform .15s, background .2s;}
  #play:hover{transform:scale(1.06)} #play:active{transform:scale(.96)}
  #play svg{width:26px;height:26px;fill:#fff}
  #restart{ flex:0 0 auto;width:40px;height:40px;border:none;border-radius:50%;
        background:#EEF1F3;color:var(--muted);cursor:pointer;display:grid;place-items:center;}
  #restart:hover{background:#E3E7EA}
  #restart svg{width:20px;height:20px;fill:currentColor}
  #track{ flex:1 1 auto; -webkit-appearance:none; appearance:none; height:6px;
        border-radius:3px; background:#D6DDE1; outline:none; margin:0 2px;}
  #track::-webkit-slider-thumb{ -webkit-appearance:none; width:18px;height:18px;
        border-radius:50%; background:var(--b-me); cursor:pointer; box-shadow:var(--elev1);}
  #track::-moz-range-thumb{ width:18px;height:18px;border:none;border-radius:50%;
        background:var(--b-me); cursor:pointer;}
  #speed{ flex:0 0 auto; border:none;background:#EEF1F3;color:var(--on-surface);
        font:500 13px "Roboto Mono",monospace;border-radius:18px;padding:8px 12px;cursor:pointer;}
  #speed:hover{background:#E3E7EA}

  /* tooltip */
  #zoomhint{ margin-top:8px; padding-top:8px; border-top:1px solid #E0E4E7;
        font:400 10.5px/1.35 "Roboto",sans-serif; color:var(--muted); }

  #tip{ position:fixed; pointer-events:none; z-index:20; background:#263238; color:#fff;
        font:400 12.5px/1.4 "Roboto",sans-serif; padding:8px 11px; border-radius:8px;
        box-shadow:var(--elev2); max-width:250px; opacity:0; transform:translateY(4px);
        transition:opacity .12s; }
  #tip b{font-weight:700} #tip .m{color:#B0BEC5;font-size:11px}
  #tip.show{opacity:1; transform:none}

  @media (max-width:560px){
    #legend{top:8px; right:8px; max-width:158px; padding:8px 10px; font-size:11px;}
    #legend h4{margin:0 0 5px; font-size:10px}
    #legend .row{margin:3px 0; gap:7px}
    #legend .row br{display:none}          /* label on one line */
    #legend .sw{width:11px;height:11px}
    #legend .sub{display:none}             /* hide region sub-labels on mobile */
    #legend .note{margin-top:6px; padding-top:6px; font-size:10px; line-height:1.3}
    #legend #search{ display:none; }
    #legend #zoomhint{ display:none; }
    #hud{padding:12px 14px}
    #year{font-size:44px}
    #phase{max-width:56vw}
    #controls{gap:9px;padding:8px 12px 8px 8px}
    #speed{padding:7px 9px}
  }
  @media (prefers-reduced-motion:reduce){
    .link.on{animation:none; opacity:0;}
    .node circle.dot{transition:opacity .25s; transform:scale(1)}
    .node.on circle.dot{transition:opacity .25s; transform:scale(1)}
    .node.on circle.pulse{animation:none}
  }
</style>
</head>
<body>
<div id="stage">
  <svg id="map" preserveAspectRatio="xMidYMid meet" role="img"
       aria-label="__ARIA__">
    <g id="mapLayer">
      <g id="gLand"></g>
      <g id="gLinks"></g>
      <text id="setuLbl" font-family="Roboto" font-weight="700" font-size="12"
            fill="#90A4AE" letter-spacing="1"></text>
    </g>
    <g id="gRef"></g>
    <g id="gNodes"></g>
  </svg>
</div>

<div id="hud">
  <div id="year"></div>
  <div id="phase">Täna. Vajuta <b>Esita</b> — aeg liigub tagasi.</div>
  <div id="count">0 esivanemat kaardil</div>
</div>

<div id="legend">
  <div id="search"><input id="searchInput" type="text" placeholder="Otsi isikut…" autocomplete="off"><div id="results"></div></div>
  <h4>Sugupuu harud</h4>
  <div id="legRows"></div>
  <div class="note"><span class="ring"></span> katkendlik ring = sünniaasta või -koht hinnatud (pärit lapselt).</div>
  <div id="zoomhint">Keri = suum &middot; lohista = liiguta &middot; topeltkl&otilde;ps = l&auml;htesta</div>
</div>

<div id="controls">
  <button id="play" aria-label="Esita / peata">
    <svg id="icoPlay" viewBox="0 0 24 24"><path d="M8 5v14l11-7z"/></svg>
    <svg id="icoPause" viewBox="0 0 24 24" style="display:none"><path d="M6 5h4v14H6zM14 5h4v14h-4z"/></svg>
  </button>
  <button id="restart" aria-label="Algusesse"><svg viewBox="0 0 24 24"><path d="M12 5V1L7 6l5 5V7a6 6 0 1 1-6 6H4a8 8 0 1 0 8-8z"/></svg></button>
  <input id="track" type="range" min="0" max="1000" value="0" step="1" aria-label="Ajajoon">
  <button id="speed" aria-label="Kiirus">0.5×</button>
</div>

<div id="tip"></div>

<script>
const DATA = __DATA__;
const MAP  = __MAP__;
const ANON = __ANON__;
const FWD  = __FWD__;
const LEGEND = __LEGEND__;
const COLORS = __COLORS__;
const GENMAP = __GENMAP__;
const BRANCHGEN = __BRANCHGEN__;
const REFPLACES = __REFPLACES__;
const NODES = DATA.nodes, BRANCHES = DATA.branches;
const byId = {}; NODES.forEach(n=>byId[n.id]=n);

const colorOf = n => (n.id===0) ? COLORS.me : (n.b==='root' ? COLORS.root : (COLORS[n.b]||'#607D8B'));

/* ---------- projection: fit rings+points into viewBox ---------- */
const VBW=1000, VBH=760, PAD=46;
let bb={lo:1e9,LO:-1e9,la:1e9,LA:-1e9};
function ext(lon,lat){bb.lo=Math.min(bb.lo,lon);bb.LO=Math.max(bb.LO,lon);
                      bb.la=Math.min(bb.la,lat);bb.LA=Math.max(bb.LA,lat);}
MAP.land.forEach(r=>r.forEach(p=>ext(p[0],p[1])));
NODES.forEach(n=>{ if(n.lon!=null) ext(n.lon,n.lat); });
// pad frame a little (land extent only; lakes may spill east into background harmlessly)
bb.LO+=0.08; bb.lo-=0.12; bb.la-=0.08; bb.LA+=0.08;
const latMid=(bb.la+bb.LA)/2, kx=Math.cos(latMid*Math.PI/180);
const spanX=(bb.LO-bb.lo)*kx, spanY=(bb.LA-bb.la);
const s=Math.min((VBW-2*PAD)/spanX,(VBH-2*PAD)/spanY);
const offX=(VBW-spanX*s)/2, offY=(VBH-spanY*s)/2;
function proj(lon,lat){
  return [ offX+(lon-bb.lo)*kx*s , offY+(bb.LA-lat)*s ];
}
// deterministic jitter so co-located dots declump
function jit(id){ const a=(id*137.508)*Math.PI/180, r=(id%7)*0.006+0.004;
  return [Math.sin(a)*r, Math.cos(a)*r*0.62]; }

/* ---------- draw land ---------- */
const SVGNS="http://www.w3.org/2000/svg";
const gLand=document.getElementById('gLand');
function ringPath(r){ return "M"+r.map(p=>{const q=proj(p[0],p[1]);
  return q[0].toFixed(1)+","+q[1].toFixed(1);}).join("L")+"Z"; }
MAP.land.forEach(r=>{
  const path=document.createElementNS(SVGNS,'path');
  path.setAttribute('d',ringPath(r)); path.setAttribute('class','land'); gLand.appendChild(path);
});
// lakes (Peipsi, Pihkva, Võrtsjärv) painted in water colour on top of land
MAP.lakes.forEach(r=>{
  const path=document.createElementNS(SVGNS,'path');
  path.setAttribute('d',ringPath(r)); path.setAttribute('class','lake'); gLand.appendChild(path);
});
// (no hard-coded region label — generic across trees)

/* ---------- geographic reference labels (grey orientation layer) ---------- */
const gRef=document.getElementById('gRef');
const REF=[];
REFPLACES.forEach(([name,lat,lon,tier])=>{
  const q=proj(lon,lat);
  const g=document.createElementNS(SVGNS,'g'); g.setAttribute('class','ref t'+tier);
  if(tier>=1){ const c=document.createElementNS(SVGNS,'circle'); c.setAttribute('r',tier===1?2.2:1.6);
    c.setAttribute('cx',0); c.setAttribute('cy',0); g.appendChild(c); }
  const t=document.createElementNS(SVGNS,'text');
  t.setAttribute('x', tier===0?0:5); t.setAttribute('y', tier===0?0:3.5);
  t.setAttribute('text-anchor', tier===0?'middle':'start');
  t.textContent=name; g.appendChild(t);
  gRef.appendChild(g); REF.push({g, bx:q[0], by:q[1]});
});

/* ---------- precompute screen coords ---------- */
NODES.forEach(n=>{
  if(n.lon==null){n.px=null;return;}
  const q=proj(n.lon, n.lat);      // coords already declumped + land-checked at build time
  n.px=q[0]; n.py=q[1];            // screen coords (n.y stays = birth year)
});

/* ---------- build links (courier arc between ancestor and descendant) ---------- */
const gLinks=document.getElementById('gLinks');
NODES.forEach(n=>{
  if(n.c==null) return;
  const c=byId[n.c]; if(c.px==null||n.px==null) return;
  // older endpoint (smaller year) vs younger; courier draws toward the newly-born one
  const older = (n.y<=c.y)? n : c, younger = (n.y<=c.y)? c : n;
  const a = FWD ? older : younger, b = FWD ? younger : older;
  const x1=a.px,y1=a.py,x2=b.px,y2=b.py;
  const mx=(x1+x2)/2,my=(y1+y2)/2, dx=x2-x1,dy=y2-y1;
  const len=Math.hypot(dx,dy)||1, nx=-dy/len, ny=dx/len;
  const bow=Math.min(len*0.28, 60);            // arc height
  const cx=mx+nx*bow, cy=my+ny*bow;
  const path=document.createElementNS(SVGNS,'path');
  path.setAttribute('d',`M${x1.toFixed(1)},${y1.toFixed(1)} Q${cx.toFixed(1)},${cy.toFixed(1)} ${x2.toFixed(1)},${y2.toFixed(1)}`);
  path.setAttribute('pathLength','1');
  path.setAttribute('class','link');
  path.style.stroke=colorOf(n);
  n._link=path; gLinks.appendChild(path);
});

/* ---------- build nodes ---------- */
const gNodes=document.getElementById('gNodes');
// neighbour birth years -> a node pops instantly if it has no earlier-appearing neighbour
const NBR=new Map();
NODES.forEach(n=>{ if(n.c==null) return; const c=byId[n.c]; if(!c||n.y==null||c.y==null) return;
  const ra=NBR.get(n.id)||{min:Infinity,max:-Infinity}; ra.min=Math.min(ra.min,c.y); ra.max=Math.max(ra.max,c.y); NBR.set(n.id,ra);
  const rb=NBR.get(c.id)||{min:Infinity,max:-Infinity}; rb.min=Math.min(rb.min,n.y); rb.max=Math.max(rb.max,n.y); NBR.set(c.id,rb);
});
const KEY_GENS=new Set([1,2,3]);   // always-labelled
NODES.forEach(n=>{
  if(n.px==null) return;
  const g=document.createElementNS(SVGNS,'g');
  let cls='node'; if(n.ye||n.pi) cls+=' est';
  if(n.g===1 || (!ANON && n.g===BRANCHGEN)) cls+=' key';   // root + branch heads; ANON: only root
  g.setAttribute('class',cls);
  g.setAttribute('transform',`translate(${n.px.toFixed(1)},${n.py.toFixed(1)})`);
  const col=colorOf(n);
  const R = n.g===1?9 : n.g===2?7 : n.g===3?6 : Math.max(3, 6 - n.g*0.26);
  const pulse=document.createElementNS(SVGNS,'circle');
  pulse.setAttribute('class','pulse'); pulse.style.stroke=col;
  const dot=document.createElementNS(SVGNS,'circle');
  dot.setAttribute('class','dot'); dot.setAttribute('r',R); dot.style.fill=col;
  if(!n.u) dot.style.cursor='default';
  const lbl=document.createElementNS(SVGNS,'text');
  lbl.setAttribute('class','lbl');
  lbl.setAttribute('x',R+4); lbl.setAttribute('y',4); lbl.setAttribute('text-anchor','start');
  lbl.textContent=n.n.length>26?n.n.slice(0,25)+'…':n.n;
  g.appendChild(pulse); g.appendChild(dot); g.appendChild(lbl);
  g._dot=dot; g._R=R; n._g=g;
  // no incoming courier arc -> dot pops instantly.
  //  back: only the proband/root.  FWD: leaf nodes (no linked earlier kin)
  // no earlier-appearing neighbour -> instant dot (root/proband, or a leaf with no linked kin)
  const nb=NBR.get(n.id);
  const instant = FWD ? !(nb && nb.min < n.y-0.001) : !(nb && nb.max > n.y+0.001);
  if(instant) g.classList.add('nolink');
  // interactions
  g.addEventListener('mouseenter',e=>showTip(e,n));
  g.addEventListener('mousemove',e=>moveTip(e));
  g.addEventListener('mouseleave',hideTip);
  g.addEventListener('click',()=>{ if(n.u) window.open(n.u,'_blank','noopener'); });
  gNodes.appendChild(g);
});

/* ---------- legend ---------- */
(function(){
  const rows=document.getElementById('legRows');
  const defs=LEGEND;
  defs.forEach(([k,t,sub])=>{
    const c=COLORS[k]||'#607D8B';
    const row=document.createElement('div'); row.className='row';
    row.innerHTML=`<span class="sw" style="background:${c}"></span>`+
      `<span>${t}<br><span class="sub">${sub}</span></span>`;
    rows.appendChild(row);
  });
})();

/* ---------- timeline / animation ---------- */
const years=NODES.filter(n=>n.y!=null).map(n=>n.y);
const yrMin=Math.min(...years), yrMax=Math.max(...years);
const NOW=new Date().getFullYear();               // end at the user's current year (their computer)
const YMIN=yrMin-8, YMAX=Math.max(NOW, yrMax);
const START = FWD ? YMIN : YMAX;                  // where playback begins
const END   = FWD ? YMAX : YMIN;                  // where playback ends
const DIR   = FWD ? +1 : -1;                      // time direction while playing
const SPAN  = END - START;                        // signed
let cur=START, playing=false, speed=0.5, last=0;   // default 0.5×
const SPEEDS=[0.5,1,2,4], BASE=34;                 // years per second (×0.5 .. ×4)

const elYear=document.getElementById('year');
const elPhase=document.getElementById('phase');
const elCount=document.getElementById('count');
const track=document.getElementById('track');
const tipEl=document.getElementById('tip');

function yearToSlider(y){ return Math.round((y-START)/SPAN*1000); }
function sliderToYear(v){ return START + v/1000*SPAN; }
// a node is "present" if its birth year is on the past side of cur
const visible = n => FWD ? (n.y <= cur+0.001) : (cur <= n.y+0.001);

function genName(g){ return GENMAP[g] || (''+g); }
let lastPhase='';
function render(){
  const y=Math.max(YMIN, Math.min(YMAX, Math.round(cur)));
  elYear.textContent = y;
  let cnt=0, frontier=null;    // frontier = most recently appeared node
  NODES.forEach(n=>{
    if(n.px==null) return;
    const on = visible(n);
    const g=n._g, lk=n._link;
    if(on){
      cnt++;
      if(!frontier || (FWD ? n.y>frontier.y : n.y<frontier.y)) frontier=n;
      if(!g.classList.contains('on')) g.classList.add('on');
    }else{
      if(g.classList.contains('on')) g.classList.remove('on');
    }
    // a courier arc shows only once BOTH its endpoints are present
    if(lk){
      const both = on && n.c!=null && visible(byId[n.c]);
      if(both){ if(!lk.classList.contains('on')) lk.classList.add('on'); }
      else    { if(lk.classList.contains('on'))  lk.classList.remove('on'); }
    }
  });
  elCount.textContent = cnt + (cnt===1?' inimene kaardil':' inimest kaardil');
  let ph;
  if(!frontier){
    ph = FWD ? 'Vajuta <b>Esita</b> — aeg liigub vanimast noorimani.'
             : 'Täna. Vajuta <b>Esita</b> — aeg liigub tagasi.';
  }else{
    const tag = (frontier.ye?'s. ~':'s. ')+frontier.y;
    if(frontier.id===0)      ph=`<b>${frontier.n||genName(1)}</b><br>${genName(1)} · ${tag}`;
    else if(ANON)            ph=`<b>${genName(frontier.g)}</b> · ${tag}`;
    else                     ph=`<b>${frontier.n}</b><br>${genName(frontier.g)} · ${tag}`;
  }
  if(ph!==lastPhase){ elPhase.innerHTML=ph; lastPhase=ph; }
  track.value=yearToSlider(cur);
}

function loop(ts){
  if(!playing){ return; }
  if(!last) last=ts;
  const dt=(ts-last)/1000; last=ts;
  cur += DIR*BASE*speed*dt;
  const done = DIR>0 ? cur>=END : cur<=END;
  if(done){ cur=END; render(); setPlaying(false); return; }
  render(); requestAnimationFrame(loop);
}
function setPlaying(p){
  playing=p; last=0;
  if(p) document.body.classList.remove('scrub');   // enable courier arcs during play
  document.getElementById('icoPlay').style.display=p?'none':'';
  document.getElementById('icoPause').style.display=p?'':'none';
  const atEnd = DIR>0 ? cur>=END-0.5 : cur<=END+0.5;
  if(p){ if(atEnd){cur=START;} requestAnimationFrame(loop); }
}
document.getElementById('play').onclick=()=>setPlaying(!playing);
document.getElementById('restart').onclick=()=>{ cur=START; render(); if(playing){last=0;requestAnimationFrame(loop);} };
document.getElementById('speed').onclick=(e)=>{
  const i=(SPEEDS.indexOf(speed)+1)%SPEEDS.length; speed=SPEEDS[i]; e.target.textContent=speed+'×';
};
track.addEventListener('input',()=>{ document.body.classList.add('scrub');
  cur=sliderToYear(+track.value);
  if(playing) setPlaying(false); render(); });

/* ---------- tooltip ---------- */
function showTip(e,n){
  const named = !(ANON && n.id!==0);
  const title = named ? (n.n || genName(n.g)) : genName(n.g);
  let meta=[];
  if(named) meta.push(genName(n.g));
  meta.push((n.ye?'sünd ~':'sünd ')+n.y + (n.ap?' (u.)':''));
  if(n.pi) meta.push('koht pärit lapselt');
  let html=`<b>${title}</b><br><span class="m">${meta.join(' · ')}</span>`;
  if(n.u) html+=`<br><span class="m">klõps → Geni profiil</span>`;
  tipEl.innerHTML=html;
  tipEl.classList.add('show'); moveTip(e);
}
function moveTip(e){
  const p=e.touches?e.touches[0]:e;
  let x=p.clientX+14, y=p.clientY+14;
  const w=tipEl.offsetWidth,h=tipEl.offsetHeight;
  if(x+w>innerWidth-8) x=p.clientX-w-14;
  if(y+h>innerHeight-8) y=p.clientY-h-14;
  tipEl.style.left=x+'px'; tipEl.style.top=y+'px';
}
function hideTip(){ tipEl.classList.remove('show'); }

/* ---------- pan & zoom (nodes keep constant size so individuals separate) ---------- */
const svgEl=document.getElementById('map');
const mapLayer=document.getElementById('mapLayer');
let k=1, tx=0, ty=0;
function clampView(){
  tx=Math.min(0, Math.max(VBW*(1-k), tx));
  ty=Math.min(0, Math.max(VBH*(1-k), ty));
}
function applyView(){
  mapLayer.setAttribute('transform',`translate(${tx.toFixed(2)},${ty.toFixed(2)}) scale(${k.toFixed(4)})`);
  gRef.classList.toggle('z2', k>=1.8);
  gRef.classList.toggle('z4', k>=3.6);
  for(const r of REF){ r.g.setAttribute('transform',`translate(${(k*r.bx+tx).toFixed(1)},${(k*r.by+ty).toFixed(1)})`); }
  for(const n of NODES){ if(n.px==null) continue;
    n._g.setAttribute('transform',`translate(${(k*n.px+tx).toFixed(1)},${(k*n.py+ty).toFixed(1)})`);
  }
}
function svgPoint(cx,cy){ const p=svgEl.createSVGPoint(); p.x=cx; p.y=cy;
  return p.matrixTransform(svgEl.getScreenCTM().inverse()); }
function zoomAt(cx,cy,factor){
  const p=svgPoint(cx,cy);
  const wx=(p.x-tx)/k, wy=(p.y-ty)/k;
  k=Math.min(9, Math.max(1, k*factor));
  tx=p.x-wx*k; ty=p.y-wy*k; clampView(); applyView();
}
svgEl.addEventListener('wheel',e=>{ e.preventDefault();
  zoomAt(e.clientX,e.clientY, Math.exp(-e.deltaY*0.0016)); },{passive:false});
svgEl.addEventListener('dblclick',()=>{ k=1;tx=0;ty=0; applyView(); });
// pointer drag + pinch
const pts=new Map(); let pinchD=0, panLast=null;
svgEl.addEventListener('pointerdown',e=>{
  if(e.target.closest('.node')) return;                 // let node hover/click work
  pts.set(e.pointerId,{x:e.clientX,y:e.clientY});
  if(pts.size===1) panLast={x:e.clientX,y:e.clientY};
  svgEl.setPointerCapture(e.pointerId);
});
svgEl.addEventListener('pointermove',e=>{
  if(!pts.has(e.pointerId)) return;
  pts.set(e.pointerId,{x:e.clientX,y:e.clientY});
  const arr=[...pts.values()];
  if(arr.length>=2){                                    // pinch zoom
    const d=Math.hypot(arr[0].x-arr[1].x, arr[0].y-arr[1].y);
    const mx=(arr[0].x+arr[1].x)/2, my=(arr[0].y+arr[1].y)/2;
    if(pinchD) zoomAt(mx,my, d/pinchD);
    pinchD=d; panLast=null;
  }else if(panLast){                                    // drag pan
    const p1=svgPoint(e.clientX,e.clientY), p0=svgPoint(panLast.x,panLast.y);
    tx+=(p1.x-p0.x); ty+=(p1.y-p0.y); panLast={x:e.clientX,y:e.clientY};
    clampView(); applyView();
  }
});
function endPtr(e){ pts.delete(e.pointerId); if(pts.size<2) pinchD=0;
  if(pts.size===1){ const v=[...pts.values()][0]; panLast={x:v.x,y:v.y}; }
  if(pts.size===0) panLast=null; }
svgEl.addEventListener('pointerup',endPtr);
svgEl.addEventListener('pointercancel',endPtr);

/* ---------- search: pick a specific person out of a dense cluster ---------- */
const gNodesEl=document.getElementById('gNodes');
const searchWrap=document.getElementById('search');
const searchInput=document.getElementById('searchInput');
const resultsEl=document.getElementById('results');
const searchable = NODES.filter(n=>n.px!=null && n.n);   // needs a name (empty in anon)
if(!searchable.length && searchWrap){ searchWrap.style.display='none'; }

function clearMatches(){
  gNodesEl.classList.remove('searching');
  NODES.forEach(n=>n._g && n._g.classList.remove('match'));
  resultsEl.innerHTML=''; resultsEl.classList.remove('show');
}
function flyTo(n){
  k=Math.max(k,4.5);
  tx=VBW/2 - k*n.px; ty=VBH/2 - k*n.py; clampView(); applyView();
}
function runSearch(q){
  q=q.trim().toLowerCase();
  clearMatches();
  if(q.length<2) return;
  const hits=searchable.filter(n=>n.n.toLowerCase().includes(q)).slice(0,40);
  resultsEl.classList.add('show');
  if(!hits.length){ resultsEl.innerHTML='<button disabled>—</button>'; return; }
  gNodesEl.classList.add('searching');
  hits.forEach(n=>n._g.classList.add('match'));
  hits.slice(0,10).forEach(n=>{
    const btn=document.createElement('button');
    btn.innerHTML=`${n.n}<br><span class="sub">${genName(n.g)} · ${n.ye?'s. ~':'s. '}${n.y}</span>`;
    btn.onclick=()=>{ flyTo(n); gNodesEl.classList.remove('searching');
      NODES.forEach(x=>x._g&&x._g.classList.remove('match')); n._g.classList.add('match');
      gNodesEl.appendChild(n._g); };
    resultsEl.appendChild(btn);
  });
  if(hits.length===1) flyTo(hits[0]);
}
if(searchInput){
  searchInput.addEventListener('input',()=>runSearch(searchInput.value));
  searchInput.addEventListener('keydown',e=>{ if(e.key==='Escape'){ searchInput.value=''; clearMatches(); }});
}

/* ---------- go ---------- */
applyView();
render();
</script>
</body>
</html>
"""

HTML = (HTML.replace("__DATA__", DATA).replace("__MAP__", MAP).replace("__LEGEND__", LEGEND)
        .replace("__COLORS__", COLORSJ).replace("__GENMAP__", GENMAPJ)
        .replace("__TITLE__", TITLE).replace("__ARIA__", ARIA)
        .replace("__BRANCHGEN__", str(branch_gen)).replace("__REFPLACES__", REFJ)
        .replace("__ANON__", "true" if ANON else "false")
        .replace("__FWD__", "true" if FWD else "false"))

if EN:
    tr = [
        # phase captions (HTML initial + JS)
        ("T\u00e4na. Vajuta <b>Esita</b> \u2014 aeg liigub tagasi.",
         "Today. Press <b>Play</b> \u2014 time runs backwards."),
        ("Vajuta <b>Esita</b> \u2014 aeg liigub vanimast noorimani.",
         "Press <b>Play</b> \u2014 time runs from oldest to youngest."),
        ("Kerin aega tagasi\u2026", "Winding time back\u2026"),
        ("0 esivanemat kaardil", "0 people on the map"),
        ("Sugupuu harud", "Family tree branches"),
        ("katkendlik ring = s\u00fcnniaasta v\u00f5i -koht hinnatud (p\u00e4rit lapselt).",
         "dashed ring = birth year or place estimated (inherited from a relative)."),
        ('aria-label="Esita / peata"', 'aria-label="Play / pause"'),
        ('aria-label="Algusesse"',     'aria-label="To start"'),
        ('aria-label="Ajajoon"',       'aria-label="Timeline"'),
        ('aria-label="Kiirus"',        'aria-label="Speed"'),
        ("Keri = suum &middot; lohista = liiguta &middot; topeltkl&otilde;ps = l&auml;htesta",
         "Scroll = zoom &middot; drag = pan &middot; double-click = reset"),
        # counts / tooltip / year tag
        ("(frontier.ye?'s. ~':'s. ')", "(frontier.ye?'b. ~':'b. ')"),
        ("(cnt===1?' inimene kaardil':' inimest kaardil')",
         "(cnt===1?' person on the map':' people on the map')"),
        ("(n.ye?'s\u00fcnd ~':'s\u00fcnd ')", "(n.ye?'b. ~':'b. ')"),
        ("' (u.)'", "' (approx.)'"),
        ("'koht p\u00e4rit lapselt'", "'place inherited from a relative'"),
        ("kl\u00f5ps \u2192 Geni profiil", "click \u2192 Geni profile"),
        # geographic reference labels (water/regions)
        ('"PEIPSI j\u00e4rv"', '"LAKE PEIPUS"'),
        ('"V\u00d5RTSJ\u00c4RV"', '"LAKE V\u00d5RTSJ\u00c4RV"'),
        ('"L\u00c4\u00c4NEMERI"', '"BALTIC SEA"'),
        ('"SOOME LAHT"', '"GULF OF FINLAND"'),
    ]
    for a, b in tr:
        HTML = HTML.replace(a, b)
    HTML = HTML.replace('<html lang="et">', '<html lang="en">')

outname = ("index_anon" if ANON else "index") + ("_desc" if DESC else "") + ("_fwd" if FWD and not DESC else "") + ("_en" if EN else "") + ".html"
open(outname, "w", encoding="utf-8").write(HTML)
print("wrote", outname, len(HTML), "bytes | ANON=", ANON, "DESC=", DESC, "FWD=", FWD, "EN=", EN)
