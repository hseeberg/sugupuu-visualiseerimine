# sugupuu-visualiseerimine
Näe oma Geni.com sugupuu andmeid Eesti kaardil
Mõeldud Claude kasutajatele!

1. ÜLEVAADE

Kasuta neid faile Claudes, et visualiseerida sinu Eestist pärit otseste esivanemate või nende järeltulijate andmeid Eesti kaardi peal. HTML failis töötaval kaardi abil on võimalik näha, mis asukohaandmed on puudu või vajavad täpsustamist. Iga isiku peale tema on võimalik klikata ning saada otseviide tema Geni.com profiilile, kiirendades sedasi andmete muutmist. 


2. KUIDAS KASUTADA?
   
2.1.1. Kui soovid visualiseerida oma esivanema järeltulijaid:
     -> vali Geni.com'ist välja oma esivanem.
     -> üleval nupust "Actions" vali "Descendant report".
     -> vali kõik põlvkonnad
     -> vali kursoriga tekkinud ülevaade järeltulijatest ja kopeeri
     -> kleebi andmed Word wõi Google Doc dokumenti
     -> salvesta .md failina

2.1.2. Kui soovid visualiseerida oma esivanemaid:
     -> vali Geni.com'ist oma profiil
     -> üleval nupust "Actions" vali "Ancestor report".
     -> vali kõik põlvkonnad
     -> vali kursoriga tekkinud ülevaade järeltulijatest ja kopeeri
     -> kleebi andmed Word wõi Google Doc dokumenti
     -> salvesta .md failina

2.2. Loo Claudes Project ja impordi failid sinna:
     -> kõik failid siin (v.a. readme.md) + instructions (all) + punktis 2.1. loodud .md file -> Claudele anna nüüd käsk "Visualiseeri!".

----
"Instructions: 
Kui lisan .md sugupuu-ekspordi:
1. Kopeeri /mnt/project/ pipeline-skriptid (build_map.py, parse.py, build_html.py)
   ja map.json töökausta.
2. Jooksuta parse.py (uue .md peal), siis build_html.py.
Kasuta olemasolevat map.json — ära lae kaarti uuesti, kui pole vaja.
3. Vaikimisi: nimedega, edasisuunaline (esivanematest tänase päeva järglaseni), 0.5x, suum nupuga (kasutaja ise kasutab vajadusel). 
Küsi ainult siis, kui variant on ebaselge (tagurpidi / anon / inglise).

4. Anna tulemus alati .html failina.
Reeglid: koordinaadid ligikaudsed juhul kui on vaid talunimi teada; puuduvad kohad pärida lapselt; puuduvad aastad hinnata ~30 a/põlvkond; piiriülesed sünnid jäta piiri taha.

----

2.3 Kirjuta Claude Projekti "Visualiseeri!" ja naudi kaardi abil avastusi! 
  
