"""Decode world-atlas TopoJSON into plain [lon, lat] rings.

Doing this at build time means the page needs no topojson library at runtime — it
just draws the rings. Coordinates are rounded to two decimals, which is well under
one pixel at any zoom this map offers.
"""
import json, os

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
SRC = os.path.join(ROOT, "docs", "data", "land-110m.json")
DEST = os.path.join(ROOT, "docs", "data", "land.json")

topo = json.load(open(SRC))
tr = topo["transform"]
sx, sy = tr["scale"]
tx, ty = tr["translate"]

# arcs are delta-encoded in quantised integer space
arcs = []
for arc in topo["arcs"]:
    x = y = 0
    pts = []
    for dx, dy in arc:
        x += dx; y += dy
        pts.append([round(x * sx + tx, 2), round(y * sy + ty, 2)])
    arcs.append(pts)


def ring(idxs):
    out = []
    for i in idxs:
        a = arcs[~i][::-1] if i < 0 else arcs[i]
        out.extend(a[1:] if out else a)
    return out


rings = []
for geom in topo["objects"]["land"]["geometries"]:
    if geom["type"] == "Polygon":
        polys = [geom["arcs"]]
    elif geom["type"] == "MultiPolygon":
        polys = geom["arcs"]
    else:
        continue
    for poly in polys:
        for r in poly:
            pts = ring(r)
            if len(pts) > 3:
                rings.append(pts)

rings.sort(key=len, reverse=True)
json.dump(rings, open(DEST, "w"), separators=(",", ":"))
os.remove(SRC)
print(f"{len(rings)} land rings, {sum(len(r) for r in rings):,} points -> "
      f"{os.path.getsize(DEST)/1024:.0f} KB")
