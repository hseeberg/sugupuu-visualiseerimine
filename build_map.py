import json
C=json.load(open('ne_10m_admin_0_countries_lakes.json'))
est=[f for f in C['features'] if f['properties'].get('NAME')=='Estonia'][0]
polys=est['geometry']['coordinates']
land=[[[round(p[0],4),round(p[1],4)] for p in poly[0]] for poly in polys]  # outer rings

L=json.load(open('ne_10m_lakes.json'))
want={'Lake Peipus','Lake Pskov','Võrtsjärv'}
lakes=[]
for f in L['features']:
    nm=f['properties'].get('name')
    if nm in want:
        g=f['geometry']
        ring=g['coordinates'][0] if g['type']=='Polygon' else g['coordinates'][0][0]
        lakes.append([[round(p[0],4),round(p[1],4)] for p in ring])
json.dump({'land':land,'lakes':lakes},open('map.json','w'))
print('land polys:',len(land),'sizes',[len(r) for r in land])
print('lakes:',len(lakes),'sizes',[len(r) for r in lakes])
print('bytes',len(open('map.json').read()))
