"""Detailkarte Limón Indanza – Maikiuants für die Startseite (_includes/map-region.html).

Daten: © OpenStreetMap-Mitwirkende (ODbL), geladen über die Overpass-API und in vendor/osm
zwischengespeichert. Neu erzeugen:  python3 scripts/make_region_map.py
(vorher vendor/osm/*.json löschen, um aktuelle Daten zu laden)
"""
import json, math, heapq, os, subprocess

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CACHE = os.path.join(ROOT, 'vendor', 'osm')
OUT = os.path.join(ROOT, '_includes', 'map-region.html')
BBOX = '(-3.32,-78.60,-2.88,-78.08)'
QUERIES = {
    'raw.json': '[out:json][timeout:90];('
                'way["waterway"="river"]' + BBOX + ';'
                'way["highway"~"^(primary|secondary|tertiary|unclassified|track|residential)$"]' + BBOX + ';'
                'node["place"~"^(city|town|village|hamlet)$"]' + BBOX + ';);out geom tags;',
    'parks.json': '[out:json][timeout:120];relation["boundary"~"protected_area|national_park"]'
                  '(-3.25,-78.60,-2.88,-78.08);out geom;',
}
def load(name):
    path = os.path.join(CACHE, name)
    if not os.path.exists(path):
        os.makedirs(CACHE, exist_ok=True)
        subprocess.run(['curl', '-s', '-m', '200', '-A', 'KampuntinWebsiteMap/1.0', '-H', 'Accept: application/json',
                        '-o', path, '--data-urlencode', 'data=' + QUERIES[name],
                        'https://overpass-api.de/api/interpreter'], check=True)
    return json.load(open(path))
raw, parks = load('raw.json'), load('parks.json')

# Ausschnitt und Projektion (flächentreu genug für 40 km)
LON0, LON1, LAT0, LAT1 = -78.592, -78.108, -3.259, -2.891
COS = math.cos(math.radians(3.07))
W = 640
K = W / ((LON1 - LON0) * COS)
H = round((LAT1 - LAT0) * K)
def P(lat, lon): return ((lon - LON0) * K * COS, (LAT1 - lat) * K)

def rdp(pts, eps):
    if len(pts) < 3: return pts
    (x1, y1), (x2, y2) = pts[0], pts[-1]
    dx, dy = x2 - x1, y2 - y1
    L = math.hypot(dx, dy)
    best, dmax = 0, -1
    for k in range(1, len(pts) - 1):
        x, y = pts[k]
        d = abs(dy * x - dx * y + x2 * y1 - y2 * x1) / L if L else math.hypot(x - x1, y - y1)
        if d > dmax: best, dmax = k, d
    if dmax > eps:
        return rdp(pts[:best + 1], eps)[:-1] + rdp(pts[best:], eps)
    return [pts[0], pts[-1]]
def rdp_ring(pts, eps):
    mid = len(pts) // 2
    return rdp(pts[:mid + 1], eps)[:-1] + rdp(pts[mid:], eps)

def inside(x, y, m=40): return -m <= x <= W + m and -m <= y <= H + m
def segments(geom, eps=0.7):
    out, cur = [], []
    for p in geom:
        x, y = P(p['lat'], p['lon'])
        if inside(x, y): cur.append((x, y))
        elif cur: out.append(cur); cur = []
    if cur: out.append(cur)
    return [rdp(s, eps) for s in out if len(s) > 1]
def d_attr(segs, close=False):
    return ' '.join('M' + ' L'.join(f'{x:.1f} {y:.1f}' for x, y in s) + (' Z' if close else '') for s in segs)

# Schutzgebiete: Außenringe aus den Wegen zusammensetzen
def rings(rel):
    ways = [[(g['lat'], g['lon']) for g in m['geometry']] for m in rel['members']
            if m['type'] == 'way' and m['role'] == 'outer' and m.get('geometry')]
    res = []
    while ways:
        ring = ways.pop(0)
        joined = True
        while joined and ring[0] != ring[-1]:
            joined = False
            for i, w in enumerate(ways):
                if w[0] == ring[-1]: ring = ring + w[1:]
                elif w[-1] == ring[-1]: ring = ring + w[::-1][1:]
                elif w[-1] == ring[0]: ring = w[:-1] + ring
                elif w[0] == ring[0]: ring = w[::-1][:-1] + ring
                else: continue
                ways.pop(i); joined = True; break
        res.append(ring)
    return res
park_paths = []
for rel in parks['elements']:
    segs = [rdp_ring([P(a, b) for a, b in r], 0.8) for r in rings(rel)]
    segs = [s for s in segs if len(s) > 3]
    if segs: park_paths.append((rel['tags'].get('name', ''), d_attr(segs, close=True)))

# Flüsse, Straßen, Straßengraph für den Weg
MAJOR_RIVERS = {'Río Zamora', 'Río Santiago', 'Río Namangoza', 'Río Coangos'}
rivers_major, rivers_minor = [], []
roads = {'major': [], 'tertiary': [], 'minor': [], 'track': []}
graph = {}
def add_edge(a, b):
    d = math.hypot((a[0] - b[0]) * 111.32, (a[1] - b[1]) * 111.32 * COS)
    graph.setdefault(a, []).append((b, d)); graph.setdefault(b, []).append((a, d))
for e in raw['elements']:
    if e['type'] != 'way': continue
    t = e.get('tags', {})
    if t.get('waterway') == 'river':
        (rivers_major if t.get('name') in MAJOR_RIVERS else rivers_minor).extend(segments(e['geometry']))
    elif 'highway' in t:
        g = [(round(p['lat'], 7), round(p['lon'], 7)) for p in e['geometry']]
        for a, b in zip(g, g[1:]): add_edge(a, b)
        h = t['highway']
        cls = {'primary': 'major', 'secondary': 'major', 'tertiary': 'tertiary',
               'unclassified': 'minor', 'track': 'track'}.get(h)
        if cls: roads[cls].extend(segments(e['geometry']))
places = {e['tags']['name']: (e['lat'], e['lon']) for e in raw['elements']
          if e['type'] == 'node' and 'name' in e.get('tags', {})}

def nearest(pt): return min(graph, key=lambda n: (n[0] - pt[0]) ** 2 + (n[1] - pt[1]) ** 2)
src, dst = nearest(places['Limón Indanza']), nearest(places['Maikiuants'])
dist, prev, pq = {src: 0}, {}, [(0, src)]
while pq:
    d, n = heapq.heappop(pq)
    if n == dst: break
    if d > dist.get(n, 1e18): continue
    for m, w in graph[n]:
        if d + w < dist.get(m, 1e18): dist[m] = d + w; prev[m] = n; heapq.heappush(pq, (d + w, m))
route = [dst]
while route[-1] != src: route.append(prev[route[-1]])
route_d = d_attr([rdp([P(a, b) for a, b in route[::-1]], 0.6)])

def river_label(name, frac):
    segs = []
    for e in raw['elements']:
        if e['type'] == 'way' and e.get('tags', {}).get('name') == name:
            segs += [s for s in segments(e['geometry'], 0.4) if all(10 <= x <= W - 10 and 10 <= y <= H - 10 for x, y in s)]
    if not segs: return None
    s = max(segs, key=lambda s: sum(math.hypot(b[0] - a[0], b[1] - a[1]) for a, b in zip(s, s[1:])))
    i = max(1, min(len(s) - 2, int(len(s) * frac)))
    (x1, y1), (x2, y2) = s[i - 1], s[i + 1]
    ang = math.degrees(math.atan2(y2 - y1, x2 - x1))
    ang = ang - 180 if ang > 90 else ang + 180 if ang < -90 else ang
    return s[i][0], s[i][1], ang

o = []
o.append('{%- comment -%} Detailkarte Limón Indanza – Maikiuants. Daten: © OpenStreetMap-Mitwirkende (ODbL). '
         'Erzeugt mit scripts/make_region_map.py – Beschriftungen aus den Sprachdateien. {%- endcomment -%}')
o.append(f'<svg class="map map--region" viewBox="0 0 {W} {H}" role="img" aria-labelledby="map-region-title">')
o.append('  <title id="map-region-title">{{ include.labels.title }}</title>')
o.append(f'  <rect class="mr__land" width="{W}" height="{H}"/>')
for name, d in park_paths:
    o.append(f'  <path class="mr__park" fill-rule="evenodd" d="{d}"><title>{name}</title></path>')
o.append(f'  <path class="mr__river" d="{d_attr(rivers_minor)}"/>')
o.append(f'  <path class="mr__river mr__river--major" d="{d_attr(rivers_major)}"/>')
for cls in ('track', 'minor', 'tertiary', 'major'):
    o.append(f'  <path class="mr__road mr__road--{cls}" d="{d_attr(roads[cls])}"/>')
o.append(f'  <path class="mr__route-casing" d="{route_d}"/>')
o.append(f'  <path class="mr__route" d="{route_d}"/>')
for name, frac in (('Río Zamora', .55), ('Río Coangos', .5)):
    lab = river_label(name, frac)
    if lab:
        x, y, a = lab
        o.append(f'  <text class="mr__river-label" transform="translate({x:.1f} {y - 6:.1f}) rotate({a:.0f})" text-anchor="middle">{name}</text>')
SHOW = [('Limón Indanza', 'town', 'end'), ('San Juan Bosco', 'town', 'start'), ('Indanza', 'village', 'start'),
        ('Yunkumas', 'village', 'start'), ('Warintza', 'village', 'start')]
for name, kind, anchor in SHOW:
    if name not in places: continue
    x, y = P(*places[name])
    r, dx = (5.5, 10) if kind == 'town' else (4.5, 9)
    if anchor == 'end': dx = -dx
    o.append(f'  <circle class="mr__place mr__place--{kind}" cx="{x:.1f}" cy="{y:.1f}" r="{r}"/>'
             f'<text class="mr__label mr__label--{kind}" x="{x + dx:.1f}" y="{y + 7:.1f}" text-anchor="{anchor}">{name}</text>')
mx, my = P(*places['Maikiuants'])
o.append(f'  <circle class="map__pulse" cx="{mx:.1f}" cy="{my:.1f}" r="20"/>')
o.append(f'  <circle class="mr__marker" cx="{mx:.1f}" cy="{my:.1f}" r="10"/>')
o.append(f'  <text class="mr__marker-label" x="{mx + 4:.1f}" y="{my - 20:.1f}" text-anchor="middle">Maikiuants</text>')
km10 = 10 / 111.32 * K * COS
o.append(f'  <g class="mr__scale" transform="translate(22 {H - 24})"><rect width="{km10:.1f}" height="4"/>'
         f'<text x="{km10 + 8:.1f}" y="5" >10 km</text></g>')
o.append(f'  <text class="mr__credit" x="{W - 12}" y="{H - 12}" text-anchor="end">© OpenStreetMap</text>')
o.append('</svg>')
open(OUT, 'w', encoding='utf-8').write('\n'.join(o) + '\n')
print(f'{OUT}: {W}×{H}, Weg {dist[dst]:.1f} km, {len(park_paths)} Schutzgebiete, Maikiuants bei {mx:.0f}/{my:.0f}')
