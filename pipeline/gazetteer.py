"""A small hand-built gazetteer.

The settings are free prose ("A Benedictine monastery in northern Italy"), so this
matches place names inside them rather than geocoding an address. Cities are tried
before countries so "Barcelona, Spain" lands on Barcelona, and the *first* place named
wins rather than the longest one anywhere in the string, because a setting reads
primary-place-first.

Anything that resolves to nowhere real — Discworld, a library between life and death —
is left unplaced rather than forced onto a map. A book set in an invented name for a
real place (Hardy's Wessex, Middlemarch) is placed and flagged instead; see
`fiction_marker`.
"""

# name -> (lat, lon, kind, display)
CITIES = {
    "tehran": (35.69, 51.39, "city", "Tehran"), "isfahan": (32.65, 51.67, "city", "Isfahan"),
    "shiraz": (29.59, 52.58, "city", "Shiraz"), "tabriz": (38.08, 46.29, "city", "Tabriz"),
    "abadan": (30.35, 48.30, "city", "Abadan"), "mashhad": (36.30, 59.61, "city", "Mashhad"),
    "saint petersburg": (59.93, 30.34, "city", "Saint Petersburg"),
    "st. petersburg": (59.93, 30.34, "city", "Saint Petersburg"),
    "petersburg": (59.93, 30.34, "city", "Saint Petersburg"),
    "moscow": (55.76, 37.62, "city", "Moscow"), "staraya russa": (57.99, 31.36, "city", "Staraya Russa"),
    "siberia": (60.00, 90.00, "region", "Siberia"),
    "london": (51.51, -0.13, "city", "London"), "oxford": (51.75, -1.26, "city", "Oxford"),
    "cambridge": (52.21, 0.12, "city", "Cambridge"), "bristol": (51.45, -2.59, "city", "Bristol"),
    "newcastle": (54.98, -1.61, "city", "Newcastle"), "cotswolds": (51.83, -1.83, "region", "the Cotswolds"),
    "west country": (50.90, -3.50, "region", "the West Country"),
    "wessex": (50.90, -2.40, "region", "Wessex, Hardy's southwest England"),
    "english midlands": (52.48, -1.90, "region", "the Midlands"), "midlands": (52.48, -1.90, "region", "the Midlands"),
    "yorkshire": (53.96, -1.08, "region", "Yorkshire"), "cornwall": (50.44, -4.90, "region", "Cornwall"),
    "dublin": (53.35, -6.26, "city", "Dublin"), "edinburgh": (55.95, -3.19, "city", "Edinburgh"),
    "paris": (48.86, 2.35, "city", "Paris"), "normandy": (49.18, -0.37, "region", "Normandy"),
    "besançon": (47.24, 6.02, "city", "Besançon"), "verrières": (47.10, 6.50, "city", "Verrières"),
    "marseille": (43.30, 5.37, "city", "Marseille"), "lyon": (45.76, 4.84, "city", "Lyon"),
    "algiers": (36.75, 3.06, "city", "Algiers"), "oran": (35.70, -0.63, "city", "Oran"),
    "barcelona": (41.39, 2.17, "city", "Barcelona"), "madrid": (40.42, -3.70, "city", "Madrid"),
    "andalusia": (37.39, -5.98, "region", "Andalusia"), "seville": (37.39, -5.99, "city", "Seville"),
    "córdoba": (37.89, -4.78, "city", "Córdoba"), "cordoba": (37.89, -4.78, "city", "Córdoba"),
    "berlin": (52.52, 13.40, "city", "Berlin"), "bonn": (50.73, 7.10, "city", "Bonn"),
    "munich": (48.14, 11.58, "city", "Munich"), "hamburg": (53.55, 9.99, "city", "Hamburg"),
    "vienna": (48.21, 16.37, "city", "Vienna"), "prague": (50.08, 14.44, "city", "Prague"),
    "bern": (46.95, 7.45, "city", "Bern"), "zurich": (47.38, 8.54, "city", "Zurich"),
    "geneva": (46.20, 6.14, "city", "Geneva"), "davos": (46.80, 9.84, "city", "Davos"),
    "rome": (41.90, 12.50, "city", "Rome"), "florence": (43.77, 11.26, "city", "Florence"),
    "venice": (45.44, 12.33, "city", "Venice"), "genoa": (44.41, 8.93, "city", "Genoa"),
    "milan": (45.46, 9.19, "city", "Milan"), "naples": (40.85, 14.27, "city", "Naples"),
    "sicily": (37.60, 14.02, "region", "Sicily"), "northern italy": (45.40, 9.50, "region", "northern Italy"),
    "liguria": (44.32, 8.80, "region", "Liguria"),
    "lisbon": (38.72, -9.14, "city", "Lisbon"), "amsterdam": (52.37, 4.90, "city", "Amsterdam"),
    "brussels": (50.85, 4.35, "city", "Brussels"), "copenhagen": (55.68, 12.57, "city", "Copenhagen"),
    "stockholm": (59.33, 18.07, "city", "Stockholm"), "oslo": (59.91, 10.75, "city", "Oslo"),
    "reykjavik": (64.15, -21.94, "city", "Reykjavík"), "helsinki": (60.17, 24.94, "city", "Helsinki"),
    "warsaw": (52.23, 21.01, "city", "Warsaw"), "budapest": (47.50, 19.04, "city", "Budapest"),
    "istanbul": (41.01, 28.98, "city", "Istanbul"), "athens": (37.98, 23.73, "city", "Athens"),
    "crete": (35.24, 24.81, "region", "Crete"),
    "cairo": (30.04, 31.24, "city", "Cairo"), "alexandria": (31.20, 29.92, "city", "Alexandria"),
    "abydos": (26.18, 31.92, "city", "Abydos"), "baghdad": (33.31, 44.37, "city", "Baghdad"),
    "damascus": (33.51, 36.29, "city", "Damascus"), "beirut": (33.89, 35.50, "city", "Beirut"),
    "jerusalem": (31.78, 35.22, "city", "Jerusalem"), "kabul": (34.53, 69.17, "city", "Kabul"),
    "sahara": (23.00, 12.00, "region", "the Sahara"),
    "new york": (40.71, -74.01, "city", "New York City"), "manhattan": (40.78, -73.97, "city", "Manhattan"),
    "brooklyn": (40.68, -73.94, "city", "Brooklyn"), "chicago": (41.88, -87.63, "city", "Chicago"),
    "boston": (42.36, -71.06, "city", "Boston"), "new england": (43.50, -71.50, "region", "New England"),
    "philadelphia": (39.95, -75.17, "city", "Philadelphia"), "pennsylvania": (40.99, -77.60, "region", "Pennsylvania"),
    "california": (36.78, -119.42, "region", "California"), "los angeles": (34.05, -118.24, "city", "Los Angeles"),
    "san francisco": (37.77, -122.42, "city", "San Francisco"), "seattle": (47.61, -122.33, "city", "Seattle"),
    "new orleans": (29.95, -90.07, "city", "New Orleans"), "mississippi": (32.35, -89.40, "region", "Mississippi"),
    "alabama": (32.32, -86.90, "region", "Alabama"), "georgia, usa": (32.17, -82.90, "region", "Georgia"),
    "west virginia": (38.60, -80.45, "region", "West Virginia"), "arizona": (34.05, -111.09, "region", "Arizona"),
    "american midwest": (41.50, -93.00, "region", "the American Midwest"),
    "midwest": (41.50, -93.00, "region", "the American Midwest"),
    "st. louis": (38.63, -90.20, "city", "St. Louis"),
    "saint louis": (38.63, -90.20, "city", "St. Louis"),
    "nevada": (38.80, -116.42, "region", "Nevada"), "american southwest": (34.50, -111.00, "region", "the American Southwest"),
    "maine": (45.25, -69.44, "region", "Maine"), "ohio": (40.42, -82.91, "region", "Ohio"),
    "texas": (31.97, -99.90, "region", "Texas"), "montana": (46.88, -110.36, "region", "Montana"),
    "toronto": (43.65, -79.38, "city", "Toronto"), "montreal": (45.50, -73.57, "city", "Montréal"),
    "mexico city": (19.43, -99.13, "city", "Mexico City"), "comala": (19.20, -103.72, "city", "Comala"),
    "macondo": (10.90, -74.80, "city", "Macondo"), "bogotá": (4.71, -74.07, "city", "Bogotá"),
    "cartagena": (10.39, -75.51, "city", "Cartagena"), "lima": (-12.05, -77.04, "city", "Lima"),
    "buenos aires": (-34.60, -58.38, "city", "Buenos Aires"), "montevideo": (-34.90, -56.16, "city", "Montevideo"),
    "mar del plata": (-38.00, -57.56, "city", "Mar del Plata"),
    "santiago": (-33.45, -70.67, "city", "Santiago"), "rio de janeiro": (-22.91, -43.17, "city", "Rio de Janeiro"),
    "são paulo": (-23.55, -46.63, "city", "São Paulo"), "havana": (23.11, -82.37, "city", "Havana"),
    "tokyo": (35.68, 139.69, "city", "Tokyo"), "kyoto": (35.01, 135.77, "city", "Kyoto"),
    "osaka": (34.69, 135.50, "city", "Osaka"), "hiroshima": (34.39, 132.46, "city", "Hiroshima"),
    "beijing": (39.90, 116.41, "city", "Beijing"), "shanghai": (31.23, 121.47, "city", "Shanghai"),
    "seoul": (37.57, 126.98, "city", "Seoul"), "hong kong": (22.32, 114.17, "city", "Hong Kong"),
    "delhi": (28.61, 77.21, "city", "Delhi"), "mumbai": (19.08, 72.88, "city", "Mumbai"),
    "bombay": (19.08, 72.88, "city", "Bombay"), "calcutta": (22.57, 88.36, "city", "Calcutta"),
    "kolkata": (22.57, 88.36, "city", "Kolkata"), "kerala": (10.85, 76.27, "region", "Kerala"),
    "colombo": (6.93, 79.86, "city", "Colombo"), "kandy": (7.29, 80.64, "city", "Kandy"),
    "bangkok": (13.76, 100.50, "city", "Bangkok"), "jakarta": (-6.21, 106.85, "city", "Jakarta"),
    "sydney": (-33.87, 151.21, "city", "Sydney"), "melbourne": (-37.81, 144.96, "city", "Melbourne"),
    "auckland": (-36.85, 174.76, "city", "Auckland"),
    "lagos": (6.52, 3.38, "city", "Lagos"), "akour": (5.50, 6.50, "city", "Akure"),
    "niger-delta": (5.50, 6.20, "region", "the Niger Delta"), "nairobi": (-1.29, 36.82, "city", "Nairobi"),
    "cape town": (-33.92, 18.42, "city", "Cape Town"), "johannesburg": (-26.20, 28.05, "city", "Johannesburg"),
    "kinshasa": (-4.44, 15.27, "city", "Kinshasa"), "congo river": (-1.00, 18.00, "region", "the Congo"),
    "khartoum": (15.50, 32.56, "city", "Khartoum"), "kabul river": (34.53, 69.17, "region", "Kabul"),
}

COUNTRIES = {
    "iran": (32.43, 53.69), "russia": (61.52, 105.32), "soviet union": (61.52, 105.32),
    "england": (52.36, -1.17), "united kingdom": (54.00, -2.00), "britain": (54.00, -2.00),
    "scotland": (56.49, -4.20), "ireland": (53.41, -8.24), "wales": (52.13, -3.78),
    "france": (46.60, 1.89), "spain": (40.46, -3.75), "portugal": (39.40, -8.22),
    "germany": (51.17, 10.45), "west germany": (50.50, 9.00), "austria": (47.52, 14.55),
    "switzerland": (46.82, 8.23), "italy": (41.87, 12.57), "greece": (39.07, 21.82),
    "turkey": (38.96, 35.24), "netherlands": (52.13, 5.29), "belgium": (50.50, 4.47),
    "denmark": (56.26, 9.50), "sweden": (60.13, 18.64), "norway": (60.47, 8.47),
    "finland": (61.92, 25.75), "iceland": (64.96, -19.02), "poland": (51.92, 19.15),
    "hungary": (47.16, 19.50), "czechoslovakia": (49.82, 15.47), "czech republic": (49.82, 15.47),
    "yugoslavia": (44.02, 20.91), "albania": (41.15, 20.17), "romania": (45.94, 24.97),
    "ukraine": (48.38, 31.17), "egypt": (26.82, 30.80), "algeria": (28.03, 1.66),
    "morocco": (31.79, -7.09), "tunisia": (33.89, 9.54), "nigeria": (9.08, 8.68),
    "kenya": (-0.02, 37.91), "south africa": (-30.56, 22.94), "zimbabwe": (-19.02, 29.15),
    "sudan": (12.86, 30.22), "ethiopia": (9.15, 40.49), "ghana": (7.95, -1.02),
    "united states": (39.83, -98.58), "america": (39.83, -98.58), "usa": (39.83, -98.58),
    "canada": (56.13, -106.35), "mexico": (23.63, -102.55), "colombia": (4.57, -74.30),
    "brazil": (-14.24, -51.93), "argentina": (-38.42, -63.62), "chile": (-35.68, -71.54),
    "peru": (-9.19, -75.02), "cuba": (21.52, -77.78), "uruguay": (-32.52, -55.77),
    "japan": (36.20, 138.25), "china": (35.86, 104.20), "korea": (35.91, 127.77),
    "south korea": (35.91, 127.77), "india": (20.59, 78.96), "pakistan": (30.38, 69.35),
    "afghanistan": (33.94, 67.71), "sri lanka": (7.87, 80.77), "bangladesh": (23.68, 90.36),
    "thailand": (15.87, 100.99), "vietnam": (14.06, 108.28), "indonesia": (-0.79, 113.92),
    "australia": (-25.27, 133.78), "new zealand": (-40.90, 174.89), "israel": (31.05, 34.85),
    "palestine": (31.95, 35.23), "iraq": (33.22, 43.68), "syria": (34.80, 38.997),
    "lebanon": (33.85, 35.86), "saudi arabia": (23.89, 45.08), "nepal": (28.39, 84.12),
    "tuvalu": (-7.11, 177.65), "trinidad": (10.69, -61.22), "jamaica": (18.11, -77.30),
    "caribbean": (15.00, -75.00), "europe": (54.00, 15.00), "africa": (0.00, 20.00),
}

# Words that mark a setting as invented. These do NOT stop a book being placed:
# Hardy's Wessex is southwest England, Middlemarch is in the Midlands, Calvino's
# Ombrosa is in Liguria. Refusing those would be wrong. The marker is carried
# through to the page instead, so the map can say "fictionalised" out loud.
FICTION_MARKERS = [
    "fictional", "fictionalis", "fictionaliz", "imaginary", "invented",
    "allegorical", "metaphysical", "afterlife", "between life and death",
    "between the world of the living", "alternate", "magical world",
    "dream", "limbo", "purgatory", "symbolic",
]


def fiction_marker(text):
    """The word that marks this setting as invented, or None."""
    if not text:
        return None
    t = text.lower()
    for h in FICTION_MARKERS:
        if h in t:
            return h
    return None


def _earliest(text, names):
    """(position, key) of the first gazetteer name to appear in `text`.

    Position first, length second. A setting reads primary-place-first — "The
    American Midwest (Saint Jude...), with later chapters in Philadelphia" is a
    Midwest novel — so taking the longest match anywhere in the string picked the
    wrong place. Among names starting at the same position the longest wins, so
    "mexico city" still beats "mexico".
    """
    best = None
    for name in names:
        i = text.find(name)
        if i < 0:
            continue
        # require a word boundary so "india" does not fire inside "indiana"
        before_ok = i == 0 or not text[i - 1].isalpha()
        end = i + len(name)
        after_ok = end >= len(text) or not text[end].isalpha()
        if not (before_ok and after_ok):
            continue
        if best is None or i < best[0] or (i == best[0] and len(name) > len(best[1])):
            best = (i, name)
    return best


def locate(text):
    """Best (lat, lon, kind, place) for a free-text setting, or None.

    Cities and regions are tried before countries, so "Barcelona, Spain" lands on
    Barcelona. If nothing real is named at all — a library between life and
    death, Discworld — this returns None and the book stays off the map.
    """
    if not text:
        return None
    t = text.lower()

    hit = _earliest(t, CITIES)
    if hit:
        lat, lon, kind, disp = CITIES[hit[1]]
        return {"lat": lat, "lon": lon, "kind": kind, "place": disp}

    hit = _earliest(t, COUNTRIES)
    if hit:
        lat, lon = COUNTRIES[hit[1]]
        return {"lat": lat, "lon": lon, "kind": "country", "place": hit[1].title()}

    return None
