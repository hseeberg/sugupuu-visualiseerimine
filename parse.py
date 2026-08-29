#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import re, json, math, sys

SRC = next((a for a in sys.argv[1:] if a.lower().endswith(".md")), "input.md")

# ---------- geocoding dictionary (parish / village level, approximate) ----------
# key substrings (lowercase) -> (lat, lon). Matched longest-key-first.
PLACES = {
    # --- Tallinn / Harju ---
    "tallinn": (59.437, 24.754),
    "harjumaa": (59.35, 24.9),
    # ===================== COMPREHENSIVE ESTONIA (towns + historical parishes) =====================
    # Towns (linnad)
    "tartu": (58.378, 26.729), "narva": (59.377, 28.190), "pärnu": (58.386, 24.497),
    "kohtla-järve": (59.398, 27.273), "rakvere": (59.346, 26.356), "maardu": (59.476, 25.025),
    "sillamäe": (59.390, 27.755), "kuressaare": (58.253, 22.485), "võru": (57.834, 27.019),
    "haapsalu": (58.943, 23.541), "jõhvi": (59.359, 27.421), "paide": (58.885, 25.557),
    "keila": (59.303, 24.413), "kiviõli": (59.353, 26.970), "tapa": (59.261, 25.958),
    "põlva": (58.060, 27.069), "elva": (58.222, 26.421), "rapla": (59.007, 24.792),
    "jõgeva": (58.746, 26.394), "kärdla": (58.998, 22.749), "saue": (59.319, 24.552),
    "põltsamaa": (58.653, 25.972), "sindi": (58.401, 24.660), "paldiski": (59.356, 24.056),
    "tõrva": (58.003, 25.933), "kunda": (59.500, 26.541), "loksa": (59.578, 25.717),
    "mustvee": (58.849, 26.940), "kallaste": (58.658, 27.163), "abja-paluoja": (58.126, 25.353),
    "antsla": (57.824, 26.542), "kilingi-nõmme": (58.126, 24.966), "mõisaküla": (58.093, 25.184),
    "otepää": (58.058, 26.497), "räpina": (58.098, 27.463), "tamsalu": (59.163, 26.113),
    "püssi": (59.365, 27.045), "kehra": (59.336, 25.324), "narva-jõesuu": (59.457, 28.041),
    # Harjumaa parishes / settlements
    "hageri": (59.10, 24.65), "harju-jaani": (59.30, 25.15), "harju-madise": (59.30, 24.10),
    "madise": (59.30, 24.10), "jõelähtme": (59.42, 25.17), "juuru": (59.03, 24.87),
    "jüri": (59.30, 24.90), "kose": (59.18, 25.17),
    "kuusalu": (59.44, 25.49), "nissi": (59.10, 24.30), "harju-risti": (59.00, 24.05),
    "saku": (59.30, 24.68), "saha": (59.42, 25.02), "kernu": (59.13, 24.42),
    "raasiku": (59.36, 25.19), "aegviidu": (59.263, 25.628), "kolga": (59.50, 25.60),
    "kõue": (59.10, 25.30),
    # Raplamaa
    "kehtna": (58.93, 24.88), "käru": (58.80, 25.10), "hagudi": (58.97, 24.70),
    "järvakandi": (58.77, 24.82), "kaiu": (58.92, 25.05), "raikküla": (58.90, 24.62),
    "vahastu": (58.88, 25.00), "rapla khk": (59.007, 24.792),
    # Järvamaa
    "ambla": (59.18, 25.83), "anna": (58.98, 25.90), "järva-jaani": (59.03, 25.89),
    "järva-madise": (58.95, 25.55), "koeru": (58.97, 26.03), "peetri": (58.79, 25.62),
    "lehtse": (59.20, 25.80), "imavere": (58.83, 25.83), "koigi": (58.85, 25.95),
    "väätsa": (58.88, 25.35), "roosna-alliku": (58.98, 25.62), "kareda": (59.05, 25.75),
    "albu": (59.10, 25.75), "järva-peetri": (58.79, 25.62), "paide khk": (58.885, 25.557),
    # --- fixes: specific Järva / Väike-Maarja manors + German exonyms ---
    "kuksema": (59.017, 25.867), "jürgensberg": (59.017, 25.867),
    "kaltenbrunn": (58.980, 25.620), "kaltenbrun": (58.980, 25.620),
    "liigvalla": (59.000, 26.150), "löwenwolde": (59.000, 26.150),
    "udeva": (58.960, 26.080),
    "öötla": (58.949, 25.736),                       # ~3.5 km SW of Esna (approx)
    "esna": (58.971, 25.779), "esna mõis": (58.971, 25.779),
    # Lääne-Virumaa
    "haljala": (59.42, 26.27), "kadrina": (59.34, 26.13), "simuna": (59.03, 26.42),
    "väike-maarja": (59.121, 26.247), "viru-jaagupi": (59.23, 26.40), "viru-nigula": (59.35, 26.75),
    "vinni": (59.29, 26.43), "sõmeru": (59.33, 26.32), "rakke": (58.98, 26.25),
    "laekvere": (59.15, 26.55), "rägavere": (59.30, 26.65), "avanduse": (59.10, 26.35),
    "kadrina khk": (59.34, 26.13), # Ida-Virumaa
    "iisaku": (59.10, 27.30), "lüganuse": (59.36, 27.02), "vaivara": (59.36, 28.10),
    "tudulinna": (59.10, 27.05), "illuka": (59.22, 27.55), "mäetaguse": (59.23, 27.35),
    "toila": (59.42, 27.51), "voka": (59.42, 27.55), "avinurme": (58.99, 26.90),
    "jõhvi khk": (59.359, 27.421), "kohtla": (59.40, 27.30), "vasknarva": (59.00, 27.72),
    # Jõgevamaa
    "laiuse": (58.80, 26.40), "palamuse": (58.68, 26.55), "torma": (58.87, 26.75),
    "kursi": (58.65, 26.30), "maarja-magdaleena": (58.63, 26.85), "sadala": (58.80, 26.60),
    "kasepää": (58.75, 27.05), "kudina": (58.55, 26.75), "vaimastvere": (58.80, 26.35),
    "kuremaa": (58.75, 26.50), "laiuse khk": (58.80, 26.40),
    # Tartumaa
    "kambja": (58.21, 26.68), "kodavere": (58.60, 27.10), "nõo": (58.28, 26.53),
    "puhja": (58.32, 26.30), "rannu": (58.30, 26.10), "rõngu": (58.15, 26.25),
    "võnnu": (58.28, 27.10), "äksi": (58.55, 26.75), "kavastu": (58.45, 27.00),
    "alatskivi": (58.60, 27.12), "luunja": (58.37, 26.85),
    "kastre": (58.30, 27.00), "ülenurme": (58.32, 26.68), "mäksa": (58.35, 27.05),
    "tartu-maarja": (58.40, 26.75), "nõo khk": (58.28, 26.53), "kursi khk": (58.65, 26.30),
    # Viljandimaa (parishes beyond the Pilistvere cluster)
    "halliste": (58.16, 25.19), "kolga-jaani": (58.51, 25.83), "kõpu": (58.30, 25.30),
    "paistu": (58.28, 25.55), "tarvastu": (58.27, 25.90), "karksi": (58.106, 25.560),
    "suislepa": (58.20, 25.80), "holstre": (58.30, 25.65), "abja": (58.126, 25.353),
    "mõisaküla khk": (58.093, 25.184), "kolga-jaani khk": (58.51, 25.83),
    # Pärnumaa
    "audru": (58.40, 24.35), "halinga": (58.62, 24.50), "pärnu-jaagupi": (58.62, 24.50),
    "häädemeeste": (58.08, 24.50), "mihkli": (58.60, 24.10), "tõstamaa": (58.35, 23.90),
    "tori": (58.48, 24.80), "vändra": (58.653, 25.033), "saarde": (58.20, 24.95),
    "tahkuranna": (58.20, 24.55), "uulu": (58.25, 24.55),
    "surju": (58.20, 24.85), "kihnu": (58.13, 24.00), "koonga": (58.50, 24.10),
    "varbla": (58.48, 23.80), "vändra khk": (58.653, 25.033), "pärnu-jaagupi khk": (58.62, 24.50),
    # Läänemaa extras
    "risti khk": (59.00, 24.05), "palivere": (59.02, 23.85), "kirbla khk": (58.72, 23.87),
    # Saaremaa / Muhu
    "kaarma": (58.28, 22.45), "karja": (58.50, 22.80), "kihelkonna": (58.36, 21.98),
    "kärla": (58.30, 22.30), "mustjala": (58.50, 22.30), "anseküla": (58.10, 22.20),
    "jämaja": (57.95, 22.05), "pöide": (58.53, 23.05), "püha": (58.35, 22.60),
    "valjala": (58.40, 22.80), "orissaare": (58.56, 23.08), "leisi": (58.55, 22.70),
    "salme": (58.13, 22.27), "torgu": (57.98, 22.10), "pihtla": (58.30, 22.60),
    "laimjala": (58.45, 23.00), "muhu": (58.61, 23.20), "ruhnu": (57.80, 23.25),
    "jaani, saare": (58.53, 22.90), "kaarma khk": (58.28, 22.45),
    # Hiiumaa parishes (beyond the Emmaste/Käina village cluster)
    "käina": (58.828, 22.780), "emmaste": (58.717, 22.620), "pühalepa": (58.87, 22.90),
    "reigi": (58.98, 22.55), "kõrgessaare": (58.99, 22.42), "kärdla khk": (58.998, 22.749),
    "hellamaa": (58.85, 22.85), "kõpu, hiiu": (58.92, 22.20), "lauka": (58.95, 22.45),
    "suuremõisa": (58.88, 22.95),
    # Võrumaa / Põlvamaa
    "kanepi": (57.99, 26.75), "karula": (57.75, 26.35), "rõuge": (57.73, 26.91),
    "urvaste": (57.90, 26.50), "vastseliina": (57.73, 27.42), "hargla": (57.60, 26.42),
    "mõniste": (57.65, 26.55), "varstu": (57.68, 26.70), "misso": (57.65, 27.30),
    "haanja": (57.72, 27.03), "orava": (57.95, 27.40), "kõlleste": (58.05, 26.85),
    "räpina khk": (58.098, 27.463), "põlva khk": (58.060, 27.069), "kanepi khk": (57.99, 26.75),
    "veriora": (58.05, 27.30), "ahja": (58.15, 27.05), "mooste": (58.17, 27.25),
    # Valgamaa
    "helme": (58.02, 25.80), "sangaste": (57.93, 26.28), "tõlliste": (57.85, 26.20),
    "hummuli": (57.90, 25.95), "taheva": (57.65, 26.20), "puka": (58.05, 26.20),
    "palupera": (58.10, 26.30), "õru": (57.85, 26.05), "otepää khk": (58.058, 26.497),
    "helme khk": (58.02, 25.80),
    # German exonyms (Kurrent-era records)
    "reval": (59.437, 24.754), "dorpat": (58.378, 26.729), "pernau": (58.386, 24.497),
    "fellin": (58.364, 25.590), "weissenstein": (58.885, 25.557), "wesenberg": (59.346, 26.356),
    "hapsal": (58.943, 23.541), "arensburg": (58.253, 22.485), "werro": (57.834, 27.019),
    "walk": (57.777, 26.047), "oberpahlen": (58.653, 25.972), "leal": (58.680, 23.843),
    "baltischport": (59.356, 24.056), "wenden": (57.31, 25.27),
    # ==============================================================================================
    # --- Viljandimaa: Pilistvere / Kabala / Kõo cluster (from detail crop) ---
    "sagevere": (58.845, 25.520),
    "türi": (58.808, 25.432),
    "paluküla": (58.700, 25.680),
    "suur-villevere": (58.720, 25.460),
    "villevere": (58.720, 25.460),
    "vahamulla": (58.710, 25.560),
    "arussaare": (58.600, 25.600),
    "kobinsaare": (58.590, 25.590),
    "mändla": (58.610, 25.630),
    "venevere": (58.700, 25.860),
    "võrevere": (58.750, 25.780),
    "võisiku": (58.610, 25.870),
    "rassi": (58.700, 25.400),
    "kurla": (58.700, 25.660),
    "koksvere": (58.690, 25.688),
    "kahala": (58.700, 25.470),       # Viljandi Kahala (not Harju)
    "laeva": (58.730, 25.560),        # Laeva küla, Kabala
    "kabala": (58.770, 25.545),
    "kõo": (58.664, 25.762),
    "pilistvere": (58.723, 25.730),
    "võhma": (58.632, 25.553),
    "olustvere": (58.560, 25.550),
    "navesti": (58.500, 25.420),
    "nawwasti": (58.500, 25.420),
    "reegoldi": (58.520, 25.450),
    "paksu": (58.520, 25.450),
    "suure-jaani": (58.536, 25.470),
    "suure- jaani": (58.536, 25.470),
    "taagepera": (58.00, 25.80),
    "valga raj": (57.90, 25.90),
    "valga": (57.78, 26.03),
    "viljandimaa": (58.36, 25.60),
    "viljandi": (58.36, 25.60),
    "järvamaa": (58.88, 25.50),
    "järva": (58.88, 25.50),
    # --- Hiiumaa (Emmaste / Käina, from detail crop) ---
    "vanamõisa": (58.730, 22.560),
    "metsalauka": (58.700, 22.580),
    "härma": (58.700, 22.600),
    "laasma": (58.710, 22.620),
    "leisu": (58.720, 22.650),
    "leiso": (58.720, 22.650),
    "ollima": (58.740, 22.600),
    "tärkma": (58.740, 22.580),
    "terckma": (58.740, 22.580),
    "männamaa": (58.780, 22.615),
    "lelu": (58.755, 22.630),
    "haldi": (58.740, 22.560),
    "mänspe": (58.730, 22.540),
    "tohvri": (58.660, 22.590),
    "külaküla": (58.710, 22.590),
    "risti": (58.700, 22.600),
    "sõru": (58.680, 22.530),
    "nurste": (58.700, 22.560),
    "valgu": (58.720, 22.660),
    "harju, käina": (58.700, 22.650),
    "jausa": (58.740, 22.690),
    "prähnu": (58.800, 22.750),
    "prehno": (58.800, 22.750),
    "selja": (58.760, 22.700),
    "luguse": (58.760, 22.720),
    "putkaste": (58.790, 22.760),
    "vähelelu": (58.830, 22.780),
    "orjaku": (58.800, 22.750),
    "kassari": (58.803, 22.833),
    "esiküla": (58.800, 22.820),
    "harjuküla": (58.820, 22.800),
    "harju, vaemla": (58.840, 22.850),
    "vaemla": (58.850, 22.850),
    "holle": (58.750, 22.700),
    "öngu": (58.800, 22.500),
    "õngu": (58.800, 22.500),
    "kogri": (58.820, 22.780),
    "vana-jõe": (58.800, 22.750),
    "soo, käina": (58.780, 22.720),
    "kärdla": (58.998, 22.749),
    "emmaste": (58.717, 22.620),
    "käina": (58.828, 22.780),
    "pühalepa": (58.870, 22.900),
    "hiiumaa": (58.80, 22.70),
    "läänemaa (hiiumaa)": (58.717, 22.620),
    "läänemaa": (58.95, 23.90),
    # --- Läänemaa (western Estonia): Lihula / Karuse / Hanila / Matsalu cluster ---
    "lihula": (58.680, 23.843),
    "karuse": (58.629, 23.607),
    "hanila": (58.621, 23.545),
    "matsalu": (58.755, 23.700),
    "parivere": (58.660, 23.800),
    "virtsu": (58.573, 23.513),
    "kirbla": (58.723, 23.872),
    "massu": (58.660, 23.780),
    "vatla": (58.600, 23.720),
    "salevere": (58.680, 23.750),
    "saastna": (58.620, 23.650),
    "puise": (58.830, 23.550),
    "ridala": (58.900, 23.620),
    "haapsalu": (58.943, 23.541),
    "taebla": (59.000, 23.720),
    "palivere": (59.020, 23.850),
    "martna": (58.900, 23.570),
    "kullamaa": (58.830, 24.020),
    "vigala": (58.750, 24.350),
    "velise": (58.720, 24.230),
    "nõva": (59.160, 23.680),
    "noarootsi": (59.000, 23.350),
    "pürksi": (59.050, 23.380),
    "sutlepa": (59.030, 23.450),
    "märjamaa": (58.905, 24.017),
    "vana-vigala": (58.760, 24.320),
    "kirna": (58.780, 24.280),
    "haimre": (58.850, 24.230),
    # --- Setumaa / Petseri (from detail crop; some now in Russia) ---
    "tupina": (57.870, 27.520),
    "ступина": (57.870, 27.520),
    "ступино": (57.800, 27.650),
    "stupina": (57.800, 27.650),
    "stupino": (57.800, 27.650),
    "perdaku": (57.870, 27.500),
    "perdagu": (57.870, 27.500),
    "lädinä": (57.830, 27.580),
    "lyadinka": (57.830, 27.580),
    "ledinok": (57.830, 27.580),
    "лядинка": (57.830, 27.580),
    "duravina": (57.820, 27.630),
    "duravino": (57.820, 27.630),
    "turavino": (57.820, 27.630),
    "дуровино": (57.820, 27.630),
    "дуравино": (57.820, 27.630),
    "kostkovo": (57.930, 27.640),
    "värska": (57.950, 27.633),
    "vedernika": (57.860, 27.720),
    "vedernik": (57.860, 27.720),
    "makarova": (57.840, 27.660),
    "lõpolja": (57.750, 27.800),
    "злыполье": (57.750, 27.800),
    "злы́полье": (57.750, 27.800),
    "kulje": (57.760, 27.800),
    "nedsaja": (57.870, 27.430),
    "matsuri": (57.790, 27.500),
    "treski": (57.900, 27.480),
    "obinitsa": (57.780, 27.420),
    "meremäe": (57.720, 27.450),
    "saatse": (57.850, 27.470),
    "petseri": (57.810, 27.615),
    "setumaa": (57.850, 27.470),
    "setomaa": (57.850, 27.470),
    "venemaa": (57.830, 27.700),
    # --- all Estonian counties (low-priority fallback so any "village, County" lands right) ---
    "raplamaa": (58.95, 24.75), "rapla": (59.007, 24.792),
    "pärnumaa": (58.40, 24.55), "pärnu": (58.386, 24.497),
    "tartumaa": (58.42, 26.72), "tartu": (58.378, 26.729),
    "jõgevamaa": (58.75, 26.40), "jõgeva": (58.746, 26.394),
    "põlvamaa": (58.05, 27.05), "põlva": (58.060, 27.069),
    "võrumaa": (57.80, 27.00), "võru": (57.834, 27.019),
    "valgamaa": (57.90, 26.20),
    "lääne-virumaa": (59.30, 26.30), "lääne-viru": (59.30, 26.30), "virumaa": (59.30, 26.80),
    "ida-virumaa": (59.30, 27.40), "ida-viru": (59.30, 27.40),
    "saaremaa": (58.40, 22.55), "saare maakond": (58.40, 22.55),
    "rapla maakond": (58.95, 24.75), "pärnu maakond": (58.40, 24.55),
    "tartu maakond": (58.42, 26.72), "harju maakond": (59.20, 24.90),
    "lääne maakond": (58.90, 23.80), "lääne-viru maakond": (59.30, 26.30),
    "ida-viru maakond": (59.30, 27.40), "jõgeva maakond": (58.75, 26.40),
    "põlva maakond": (58.05, 27.05), "võru maakond": (57.80, 27.00),
    "valga maakond": (57.90, 26.20), "viljandi maakond": (58.36, 25.60),
    "järva maakond": (58.88, 25.50), "hiiu maakond": (58.85, 22.65),
}
# County / country names are the LEAST specific -> only used as fallback.
LOW = {"harjumaa","viljandimaa","viljandi","järvamaa","järva","hiiumaa",
       "läänemaa","läänemaa (hiiumaa)","setumaa","setomaa","venemaa","valga","valga raj",
       "raplamaa","pärnumaa","tartumaa","jõgevamaa","põlvamaa","võrumaa","valgamaa",
       "lääne-virumaa","lääne-viru","virumaa","ida-virumaa","ida-viru","saaremaa",
       "saare maakond","rapla maakond","pärnu maakond","tartu maakond","harju maakond",
       "lääne maakond","lääne-viru maakond","ida-viru maakond","jõgeva maakond",
       "põlva maakond","võru maakond","valga maakond","viljandi maakond",
       "järva maakond","hiiu maakond"}
HIGH_KEYS = sorted([k for k in PLACES if k not in LOW], key=len, reverse=True)
LOW_KEYS  = sorted([k for k in PLACES if k in LOW], key=len, reverse=True)
# Match a key only at a LEFT word boundary (not preceded by a letter), so a Pilistvere-area key
# like "rassi" can't be grabbed from inside another name like "Prassi". A trailing letter is fine,
# so Estonian case endings still match ("Kõos", "Emmastes").
_LB = r'(?<![a-zõäöüšž])'
HIGH_PAT = [(re.compile(_LB + re.escape(k) + r'(?!maa)'), PLACES[k]) for k in HIGH_KEYS]
LOW_PAT  = [(re.compile(_LB + re.escape(k)), PLACES[k]) for k in LOW_KEYS]

# --- foreign birthplaces: TRUE world coords. Keyed on unambiguous city/state/country tokens so
#     they never collide with Estonian names. These are rendered at the map EDGE (see build_html),
#     not snapped back into Estonia, and are not inherited into domestic relatives. ---
FOREIGN = {
    "helsinki": (60.170, 24.938), "finland": (60.170, 24.938), "soome": (60.170, 24.938),
    "ann arbor": (42.281, -83.743), "washtenaw": (42.281, -83.743), "michigan": (42.281, -83.743),
    "lansing": (42.733, -84.556), "ingham": (42.733, -84.556),
    "denver": (39.739, -104.990), "colorado": (39.739, -104.990),
    "kyoto": (35.012, 135.768), "japan": (35.012, 135.768),
    "akureyri": (65.689, -18.126), "iceland": (65.689, -18.126), "island": (65.689, -18.126),
    "tomsk": (56.498, 84.974), "tomski": (56.498, 84.974),
    "perm": (58.011, 56.250), "permi kubermang": (58.011, 56.250),
}
FOREIGN_KEYS = sorted(FOREIGN, key=len, reverse=True)
FOREIGN_PAT  = [(re.compile(_LB + re.escape(k)), FOREIGN[k]) for k in FOREIGN_KEYS]

def _best(pats, p):
    """Leftmost match wins (village is written before parish/county); ties -> longer key."""
    best_key = None; best_coord = None
    for pat, coord in pats:
        m = pat.search(p)
        if m:
            key = (m.start(), -(m.end() - m.start()))   # smaller start first, then longer key
            if best_key is None or key < best_key:
                best_key = key; best_coord = coord
    return best_coord

def geocode(place):
    """Return (coord|None, abroad:bool). Specificity by POSITION: the leftmost token in a
    'village, parish, county' string wins, so a specific village beats its parish."""
    if not place:
        return None, False
    p = place.lower()
    c = _best(HIGH_PAT, p)          # specific Estonian village / parish (leftmost)
    if c: return c, False
    c = _best(FOREIGN_PAT, p)       # foreign city/state/country -> true world coord
    if c: return c, True
    c = _best(LOW_PAT, p)           # Estonian county fallback
    if c: return c, False
    return None, False

# ---------- line parsing ----------
LINE_RE = re.compile(r'^[>\s]*(\d+)\\?\.\s*\[(.*?)\]\((https?://[^)]+)\)(.*)$')

MONTHS = "January|February|March|April|May|June|July|August|September|October|November|December"

def clean_name(s):
    s = s.replace('\\[', '[').replace('\\]', ']').replace('\\.', '.')
    return s.strip()

def parse_birth(rest):
    """Return (year:int|None, approx:bool, place:str|None)."""
    rest = rest.strip()
    # isolate birth clause: from 'b.' up to '; d.' or ';' or end
    m = re.search(r'\bb\.\s*(.*?)(?:;|$)', rest)
    if not m:
        return (None, False, None)
    seg = m.group(1).strip().rstrip(' ,')
    approx = bool(re.search(r'\b(circa|before|between|after)\b', seg, re.I))
    ym = re.search(r'\b(1[5-9]\d\d|20\d\d)\b', seg)
    year = int(ym.group(1)) if ym else None
    # place = seg with the date portion removed
    place = seg
    # remove date patterns
    place = re.sub(r'\b(circa|before|after|between)\b', '', place, flags=re.I)
    place = re.sub(rf'(?:{MONTHS})\s+\d{{1,2}},?\s*', '', place)
    place = re.sub(rf'(?:{MONTHS})\s+', '', place)
    place = re.sub(r'\b1[5-9]\d\d\b|\b20\d\d\b', '', place)
    place = re.sub(r'\band\b', '', place, flags=re.I)
    place = place.replace(',', ' , ')
    place = re.sub(r'\s+', ' ', place)
    place = place.strip(' ,')
    if not place:
        place = None
    return (year, approx, place)

nodes = []
last_at_gen = {}   # gen -> node index
raw_lines = open(SRC, encoding='utf-8').read().splitlines()

for ln in raw_lines:
    m = LINE_RE.match(ln)
    if not m:
        continue
    gen = int(m.group(1))
    name = clean_name(m.group(2))
    url = m.group(3)
    rest = m.group(4)
    year, approx, place = parse_birth(rest)
    parent_idx = last_at_gen.get(gen - 1)   # this node is an ANCESTOR (parent) of parent_idx-node
    idx = len(nodes)
    nodes.append({
        "id": idx,
        "gen": gen,
        "name": name,
        "url": url,
        "byear": year,           # real birth year or None
        "approx": approx,        # date uncertain
        "place": place,          # cleaned place string or None
        "child": parent_idx,     # the descendant this ancestor links up to
        "lat": None, "lon": None,
        "place_inherited": False,
        "year_estimated": False,
        "abroad": False,
    })
    last_at_gen[gen] = idx

print("parsed nodes:", len(nodes))

# ---------- geocode ----------
for n in nodes:
    coord, abroad = geocode(n["place"])
    if coord:
        n["lat"], n["lon"] = coord[0], coord[1]
        n["abroad"] = abroad

geo_known = sum(1 for n in nodes if n["lat"] is not None)
print("geocoded directly:", geo_known, "/", len(nodes))

# report unmatched places (had a place string but no coord)
unmatched = {}
for n in nodes:
    if n["place"] and n["lat"] is None:
        unmatched[n["place"]] = unmatched.get(n["place"], 0) + 1
print("--- unmatched place strings (place present, no coord) ---")
for k, v in sorted(unmatched.items(), key=lambda x: -x[1]):
    print(f"  {v:2d}  {k}")

# ---------- branch tagging (which gen-BRANCH_GEN line each node belongs to) ----------
# ancestors: BRANCH_GEN=3 (grandparent lines).  descendants: BRANCH_GEN=2 (root's children).
DESC = ('--descendants' in sys.argv) or ('--desc' in sys.argv)
BRANCH_GEN = 2 if DESC else 3

children = {}
for n in nodes:
    children.setdefault(n["child"], []).append(n["id"])

def descend_branch(root_id, branch):
    stack = [root_id]
    while stack:
        cur = stack.pop()
        nodes[cur]["branch"] = branch
        for ch in children.get(cur, []):
            stack.append(ch)

for n in nodes:
    n["branch"] = None
for n in nodes:
    if n["gen"] < BRANCH_GEN:
        n["branch"] = "root"
for n in nodes:
    if n["gen"] == BRANCH_GEN and n["branch"] is None:
        descend_branch(n["id"], f'g{BRANCH_GEN}_{n["id"]}')

# names of the branch heads (data-driven; used by the legend, no hard-coding)
heads = [n for n in nodes if n["gen"] == BRANCH_GEN]
branch_names = {}
for n in heads:
    branch_names[f'g{BRANCH_GEN}_{n["id"]}'] = n["name"]
print(f"--- branches (gen {BRANCH_GEN}) ---")
for b, nm in branch_names.items():
    cnt = sum(1 for x in nodes if x.get("branch") == b)
    print(f"  {b}: {nm}  ({cnt} nodes)")

# ---------- inherit location from any coord'd neighbour (works for root too) ----------
# reverse edges: which nodes point to this node as their edge partner
rev = {}
for n in nodes:
    rev.setdefault(n["child"], []).append(n["id"])
changed = True
while changed:
    changed = False
    for n in nodes:
        if n["lat"] is not None: continue
        cands = ([n["child"]] if n["child"] is not None else []) + rev.get(n["id"], [])
        src = None
        for cid in cands:                        # prefer a domestic (non-abroad) neighbour
            if cid is not None and nodes[cid]["lat"] is not None and not nodes[cid].get("abroad"):
                src = cid; break
        if src is None:                          # else any neighbour (may itself be abroad)
            for cid in cands:
                if cid is not None and nodes[cid]["lat"] is not None:
                    src = cid; break
        if src is not None:
            n["lat"], n["lon"] = nodes[src]["lat"], nodes[src]["lon"]
            n["abroad"] = nodes[src].get("abroad", False)   # inherit abroad-ness too (kept off-map)
            n["place_inherited"] = True; changed = True

order = sorted(range(len(nodes)), key=lambda i: nodes[i]["gen"])
still_missing = [n for n in nodes if n["lat"] is None]
print("still missing coords after inherit:", len(still_missing))
for n in still_missing[:20]:
    print("   ", n["gen"], n["name"], "| child:", n["child"])

# ---------- declump jitter + keep island (Hiiumaa) points ON the island ----------
import json as _json
_land = _json.load(open("map.json"))["land"]
# pick the Hiiumaa polygon by bbox
def _bbox(r):
    lo=[p[0] for p in r]; la=[p[1] for p in r]; return min(lo),max(lo),min(la),max(la)
HIIU = None
for r in _land:
    b=_bbox(r)
    if 21.7<b[0]<22.2 and 22.9<b[1]<23.2 and 58.6<b[2]<58.8 and 59.0<b[3]<59.2:
        HIIU = r; break
def pip(lat, lon, ring):
    # ray casting; ring = [[lon,lat],...]
    inside=False; n=len(ring); j=n-1
    for i in range(n):
        xi,yi=ring[i][0],ring[i][1]; xj,yj=ring[j][0],ring[j][1]
        if ((yi>lat)!=(yj>lat)) and (lon < (xj-xi)*(lat-yi)/((yj-yi) or 1e-12)+xi):
            inside=not inside
        j=i
    return inside

# Even, bounded spread for co-located people: everyone sharing a spot is fanned out on a
# sunflower spiral inside a small disk (<= ~3 km). Tight at 1x (near true location), but the
# geographic offset means ZOOMING IN separates them so each person is pickable.
from collections import defaultdict
GOLD = math.pi * (3 - math.sqrt(5))
_buckets = defaultdict(list)
for n in nodes:
    if n["lat"] is None: continue
    _buckets[(round(n["lat"]/0.004), round(n["lon"]/0.004))].append(n["id"])
spread = {}
for key, ids in _buckets.items():
    ids = sorted(ids)
    Nn = len(ids)
    if Nn == 1:
        spread[ids[0]] = (0.0, 0.0); continue
    R = min(0.030, 0.006 + 0.0045*math.sqrt(Nn))      # disk radius in degrees (~ up to 3 km)
    for j, i in enumerate(ids):
        rr = R*math.sqrt((j+0.5)/Nn); a = j*GOLD
        spread[i] = (rr*math.sin(a), rr*math.cos(a)/0.55)  # (dlat, dlon); dlon widened for round disk

hiiu_bbox_ok = lambda la,lo: (21.8<lo<23.15 and 58.6<la<59.15)
CEN=None
if HIIU:
    CEN=(sum(p[1] for p in HIIU)/len(HIIU), sum(p[0] for p in HIIU)/len(HIIU))  # (lat,lon)
clamped=0
for n in nodes:
    if n["lat"] is None: continue
    base=(n["lat"], n["lon"])
    dla,dlo=spread.get(n["id"],(0.0,0.0))
    cand=(base[0]+dla, base[1]+dlo)
    if HIIU and hiiu_bbox_ok(base[0],base[1]):     # any point born on Hiiumaa stays on the island
        placed=False
        for t in (1.0,0.7,0.45,0.25,0.1,0.0):        # 1) shrink spread toward base
            c=(base[0]+dla*t, base[1]+dlo*t)
            if pip(c[0], c[1], HIIU): n["lat"],n["lon"]=c; placed=True; break
        if not placed:                                # 2) base off simplified outline -> move inland
            for s in (0.06,0.12,0.20,0.30,0.45,0.60,0.80):
                c=(base[0]+(CEN[0]-base[0])*s, base[1]+(CEN[1]-base[1])*s)
                if pip(c[0], c[1], HIIU): n["lat"],n["lon"]=c; placed=True; break
        if not placed:
            n["lat"],n["lon"]=base; clamped+=1
    else:
        n["lat"],n["lon"]=cand
print("Hiiumaa polygon found:", HIIU is not None, "| still-outside:", clamped)


# ---------- estimate birth years (direction-aware ~30 yr / generation) ----------
# STEP = year change when moving one generation AWAY from the root
#   ancestor tree: away = older  -> -30 ;  descendant tree: away = younger -> +30
STEP = 30 if DESC else -30
for n in nodes:
    n["dyear"] = n["byear"]            # real year or None
for _ in range(200):
    changed = False
    for n in nodes:
        if n.get("dyear") is not None: continue
        cands = ([n["child"]] if n["child"] is not None else []) + rev.get(n["id"], [])
        for cid in cands:
            m = nodes[cid]
            if m.get("dyear") is not None:
                val = m["dyear"] + STEP * (n["gen"] - m["gen"])
                if val > 2026: val = 2026        # no future births from chained estimates
                n["dyear"] = val
                n["year_estimated"] = True; changed = True; break
    if not changed:
        break

no_year = [n for n in nodes if n.get("dyear") is None]
print("nodes without any display year:", len(no_year))
for n in no_year[:20]:
    print("   ", n["gen"], n["name"])

yrs = [n["dyear"] for n in nodes if n.get("dyear") is not None]
print("year range:", min(yrs), "->", max(yrs))
print("estimated years:", sum(1 for n in nodes if n['year_estimated']))
print("inherited places:", sum(1 for n in nodes if n['place_inherited']))

# ---------- emit ----------
out = []
for n in nodes:
    out.append({
        "id": n["id"], "g": n["gen"], "n": n["name"], "u": n["url"],
        "y": n.get("dyear"), "ye": n["year_estimated"],
        "lat": round(n["lat"], 4) if n["lat"] is not None else None,
        "lon": round(n["lon"], 4) if n["lon"] is not None else None,
        "pi": n["place_inherited"], "c": n["child"], "b": n.get("branch"),
        "ap": n["approx"],
        "ab": 1 if n.get("abroad") else 0,
        "pl": (n["place"] or "") if n.get("abroad") else "",
    })
json.dump({"nodes": out, "branches": branch_names},
          open("nodes.json", "w", encoding="utf-8"), ensure_ascii=False)
print("wrote nodes.json")
