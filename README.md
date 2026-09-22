# Literary Atlas

191 Persian book reviews, placed where the books are *set* rather than where they were
published — as a map and as a timeline.

**[Open the atlas →](https://rostam.github.io/literary-atlas/)**

The reviews come from [سفر در کتاب‌ها](https://travel-in-books.github.io) (Travel in
Books), which already records publication year and country for every book. That is not
the same thing as where a book takes place: *The Name of the Rose* is an Italian novel
published in 1980 and set in a monastery in 1327. The atlas joins the reviews to the
per-book setting profiles built by
[temporal_literature_investigator](https://github.com/rostam/temporal_literature_investigator)
and puts the books where they actually happen.

## The two views

**Map** — every book at its setting. Ten books in Tokyo, eight in London, seven in
Saint Petersburg, four in Tehran. Colour is the rating, size is the page count.

**Reach** — every book plotted by when it is set against when it was written. The
dashed diagonal is the present tense. Most of the cloud hugs it, which is what you would
expect: novelists mostly write about their own moment. The interest is in the distance
above the line. Median reach across the collection is **14 years**; *The Name of the
Rose* reaches back 653, and Nezami's *Khosrow and Shirin* 590.

Because almost everything here is post-1800, a linear year axis would crush the whole
collection into one corner. Both axes use the same piecewise scale — antiquity
compressed, the last two centuries given most of the room — so the diagonal stays
straight and the modern cluster stays readable.

## What is not on the map

42 of the 191 reviews have no pin. Some have no setting profile yet. The rest are set
nowhere real: Discworld, a hotel between the living and the dead, a library between
life and death, an unnamed near-future suburb. Those are left off rather than pinned
to the author's home country, because "where is this set" genuinely has no answer for
them — and the count is shown on the page rather than quietly hidden.

Settings are free prose ("A Benedictine monastery in northern Italy"), so placing them
means matching place names against a hand-built gazetteer of about 250 cities, regions
and countries, preferring the most specific match. It gets 149 of 191.

## Building it

Needs the two sibling repositories checked out next to this one:

```
kara/
  travel-in-books.github.io/_posts/        191 reviews
  temporal_literature_investigator/data/   profiles, history, books.jsonl
  literary-atlas/
```

```bash
python pipeline/01_build.py    # parse reviews, join profiles, geocode  -> docs/data/atlas.json
python pipeline/02_land.py     # decode world-atlas TopoJSON            -> docs/data/land.json
python -m http.server -d docs 8803
```

`02_land.py` turns the TopoJSON coastline into plain `[lon, lat]` rings at build time,
so the page draws the map with no mapping library at all — the whole thing is one SVG
and about 500 lines of JavaScript.

## Layout

```
pipeline/
  gazetteer.py   ~250 places, plus the rules for "this is set nowhere real"
  01_build.py    reviews + profiles + history -> atlas.json
  02_land.py     TopoJSON -> plain rings
docs/
  js/app.js      map projection, reach chart, book panel
  data/          atlas.json (0.6 MB), land.json (74 KB)
```

## Caveats

- Settings and their dates were extracted by a language model in the upstream project
  and are not hand-checked. Each profile carries a confidence field; treat the
  antiquity end of the timeline as approximate.
- A book with several settings gets one pin, at the first place the gazetteer matches.
- The gazetteer is hand-built and Eurocentric in the way the collection itself is.
