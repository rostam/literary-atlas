const $ = s => document.querySelector(s);
const svg = $('#canvas');
const NS = 'http://www.w3.org/2000/svg';

const state = { mode: 'map', books: [], land: [], sel: null, minRating: 1, era: -800, q: '',
                view: { x: 0, y: 0, k: 1 } };

const el = (tag, attrs = {}, kids = []) => {
  const n = document.createElementNS(NS, tag);
  for (const [k, v] of Object.entries(attrs)) if (v != null) n.setAttribute(k, v);
  for (const c of [].concat(kids)) n.append(c);
  return n;
};

// --- data -------------------------------------------------------------------

async function boot() {
  const [atlas, land] = await Promise.all([
    fetch('data/atlas.json').then(r => r.json()),
    fetch('data/land.json').then(r => r.json()),
  ]);
  state.books = atlas.books;
  state.history = atlas.history || {};
  state.land = land;

  const placed = state.books.filter(b => b.place).length;
  const dated = state.books.filter(b => b.setting_start != null).length;
  $('#stats').innerHTML = [
    ['Reviews', state.books.length],
    ['Placed on the map', placed],
    ['With a setting date', dated],
    ['Distinct settings', new Set(state.books.filter(b => b.place).map(b => b.place)).size],
  ].map(([k, v]) => `<div><dt>${k}</dt><dd>${v}</dd></div>`).join('');
  $('#unplacedNote').textContent =
    `${state.books.length - placed} reviews are not on the map: some have no setting profile, `
    + `and some are set nowhere real — Discworld, a library between life and death, an unnamed `
    + `dystopia. Those are left off rather than pinned to a guess.`;

  wire();
  render();
}

const visible = () => state.books.filter(b => {
  if ((b.rating ?? 0) < state.minRating) return false;
  if (state.era > -800 && (b.setting_start == null || b.setting_start < state.era)) return false;
  if (state.q) {
    const hay = `${b.title_en} ${b.title_fa} ${b.author} ${b.place || ''} ${b.country}`.toLowerCase();
    if (!hay.includes(state.q.toLowerCase())) return false;
  }
  return true;
});

// --- projections --------------------------------------------------------------

const size = () => {
  const r = $('#viewport').getBoundingClientRect();
  return { w: Math.max(320, r.width), h: Math.max(260, r.height) };
};

function mapProj(w, h) {
  const { x, y, k } = state.view;
  const sc = Math.min(w / 360, h / 180) * k;
  const cx = w / 2 + x, cy = h / 2 + y;
  return {
    pt: (lon, lat) => [cx + lon * sc, cy - lat * sc],
    sc,
  };
}

// --- rendering ------------------------------------------------------------------

function render() {
  const { w, h } = size();
  svg.setAttribute('viewBox', `0 0 ${w} ${h}`);
  svg.replaceChildren();
  $('#modeNote').textContent = state.mode === 'map'
    ? 'Each mark sits where its book takes place. Size is how long the book is, colour is how it was rated. Drag to pan, scroll to zoom.'
    : 'Every book plotted by when it is set against when it was written. The dashed line is the present tense — the further above it, the further back the author reached.';

  (state.mode === 'map' ? drawMap : drawReach)(w, h);
  const vis = visible();
  const shown = vis.filter(b => state.mode === 'map' ? b.place : (b.setting_start != null && b.year != null));
  $('#readout').innerHTML =
    `<span>Showing <b>${shown.length}</b> of <b>${state.books.length}</b> books</span>` +
    (state.mode === 'reach' ? `<span>Median reach back: <b>${medianReach(shown)}</b> years</span>` : '') +
    `<span>Click a mark to read the entry</span>`;
}

function medianReach(bs) {
  const g = bs.map(b => b.year - b.setting_start).filter(Number.isFinite).sort((a, b) => a - b);
  return g.length ? g[Math.floor(g.length / 2)] : 0;
}

const ratingColor = r => {
  if (r == null) return 'var(--ink-faint)';
  // one hue, lightness carries the rating — keeps the map calm
  const t = Math.max(0, Math.min(1, (r - 4) / 6));
  return `color-mix(in srgb, var(--sig) ${25 + t * 75}%, var(--ink-faint))`;
};
const radius = b => 3 + Math.min(6, Math.sqrt((b.pages || 200) / 60));

function drawMap(w, h) {
  const { pt, sc } = mapProj(w, h);
  const g = el('g');

  for (let lon = -180; lon <= 180; lon += 30) {
    const a = pt(lon, -85), b = pt(lon, 85);
    g.append(el('path', { class: 'graticule', d: `M${a[0]},${a[1]}L${b[0]},${b[1]}` }));
  }
  for (let lat = -60; lat <= 60; lat += 30) {
    const a = pt(-180, lat), b = pt(180, lat);
    g.append(el('path', { class: 'graticule', d: `M${a[0]},${a[1]}L${b[0]},${b[1]}` }));
  }

  for (const ring of state.land) {
    let d = '';
    for (let i = 0; i < ring.length; i++) {
      const [x, y] = pt(ring[i][0], ring[i][1]);
      d += (i ? 'L' : 'M') + x.toFixed(1) + ',' + y.toFixed(1);
    }
    g.append(el('path', { class: 'land', d: d + 'Z' }));
  }
  svg.append(g);

  // jitter books sharing a setting so a stack of 10 Tokyo novels is visible as 10
  const byPlace = new Map();
  for (const b of visible()) {
    if (!b.place) continue;
    if (!byPlace.has(b.place)) byPlace.set(b.place, []);
    byPlace.get(b.place).push(b);
  }
  const marks = el('g');
  for (const [place, bs] of byPlace) {
    const [cx, cy] = pt(bs[0].lon, bs[0].lat);
    bs.forEach((b, i) => {
      const ang = (i / bs.length) * Math.PI * 2;
      const off = bs.length > 1 ? 5 + Math.sqrt(bs.length) * 2.2 : 0;
      marks.append(dot(b, cx + Math.cos(ang) * off, cy + Math.sin(ang) * off));
    });
    if (bs.length >= 3 && sc > 2) {
      marks.append(el('text', { class: 'place-label', x: cx, y: cy - 13, 'text-anchor': 'middle' }, place));
    }
  }
  svg.append(marks);
}

/* Both axes share one scale, so the "written when it happened" diagonal stays a
   straight line. A linear year axis would crush 90% of the books into the top
   corner — almost everything here is post-1800 — so the scale is piecewise:
   antiquity is compressed, the last two centuries get most of the room. */
const BREAKS = [[-800, 0], [0, 0.10], [1000, 0.18], [1500, 0.27],
                [1800, 0.42], [1900, 0.58], [1950, 0.72], [2000, 0.90], [2030, 1]];

function warpYear(y) {
  if (y <= BREAKS[0][0]) return 0;
  if (y >= BREAKS[BREAKS.length - 1][0]) return 1;
  for (let i = 1; i < BREAKS.length; i++) {
    const [y0, f0] = BREAKS[i - 1], [y1, f1] = BREAKS[i];
    if (y <= y1) return f0 + ((y - y0) / (y1 - y0)) * (f1 - f0);
  }
  return 1;
}

function drawReach(w, h) {
  const pad = { l: 72, r: 20, t: 20, b: 46 };
  const bs = visible().filter(b => b.setting_start != null && b.year != null);

  const X = y => pad.l + warpYear(y) * (w - pad.l - pad.r);
  const Y = y => h - pad.b - warpYear(y) * (h - pad.t - pad.b);

  const g = el('g');
  for (const [yr] of BREAKS.slice(1, -1)) {
    g.append(el('path', { class: 'graticule', d: `M${X(yr)},${pad.t}L${X(yr)},${h - pad.b}` }));
    g.append(el('path', { class: 'graticule', d: `M${pad.l},${Y(yr)}L${w - pad.r},${Y(yr)}` }));
  }
  g.append(el('path', { class: 'diag', d: `M${X(-800)},${Y(-800)}L${X(2030)},${Y(2030)}` }));
  g.append(el('path', { class: 'axis', d: `M${pad.l},${h - pad.b}L${w - pad.r},${h - pad.b}` }));
  g.append(el('path', { class: 'axis', d: `M${pad.l},${pad.t}L${pad.l},${h - pad.b}` }));

  const label = y => (y < 0 ? `${-y} BC` : String(y));
  for (const [yr] of BREAKS) {
    g.append(el('text', { class: 'tick', x: X(yr), y: h - pad.b + 15, 'text-anchor': 'middle' }, label(yr)));
    g.append(el('text', { class: 'tick', x: pad.l - 8, y: Y(yr) + 3, 'text-anchor': 'end' }, label(yr)));
  }
  g.append(el('text', { class: 'axis-label', x: w - pad.r, y: h - pad.b + 33, 'text-anchor': 'end' },
    'when the story is set \u2192'));
  const ly = pad.t + (h - pad.t - pad.b) / 2;
  g.append(el('text', { class: 'axis-label', x: 14, y: ly, 'text-anchor': 'middle',
                        transform: `rotate(-90 14 ${ly})` }, 'when it was written \u2192'));
  svg.append(g);

  const marks = el('g');
  // draw the biggest reaches last so they sit on top of the modern cluster
  for (const b of [...bs].sort((p, q) => (p.year - p.setting_start) - (q.year - q.setting_start))) {
    marks.append(dot(b, X(b.setting_start), Y(b.year)));
  }
  svg.append(marks);
}

function dot(b, x, y) {
  const g = el('g', { class: 'dot' + (state.sel === b.slug ? ' sel' : ''), tabindex: '0',
                      role: 'button', 'aria-label': `${b.title_en}, ${b.author}` });
  g.append(el('circle', { cx: x.toFixed(1), cy: y.toFixed(1), r: radius(b),
                          fill: ratingColor(b.rating), 'fill-opacity': 0.82 }));
  g.append(el('title', {}, `${b.title_en}\n${b.author}${b.place ? '\n' + b.place : ''}`));
  const open = () => { state.sel = b.slug; showPanel(b); render(); };
  g.addEventListener('click', open);
  g.addEventListener('keydown', e => { if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); open(); } });
  return g;
}

// --- panel -----------------------------------------------------------------------

function showPanel(b) {
  const p = $('#panel');
  const reach = (b.year != null && b.setting_start != null) ? b.year - b.setting_start : null;
  const era = y => y == null ? '—' : (y < 0 ? `${-y} BC` : String(y));

  const hist = findHistory(b);
  p.innerHTML = `
    <button class="close" aria-label="Close">×</button>
    <h2>${esc(b.title_en || b.title_fa)}</h2>
    <p class="fa">${esc(b.title_fa)}</p>
    <p class="byline">${esc(b.author)}${b.country ? ' · ' + esc(b.country) : ''}</p>
    <dl class="meta">
      <dt>Published</dt><dd>${era(b.year)}</dd>
      <dt>Set in</dt><dd>${esc(b.place || '—')}</dd>
      <dt>Set during</dt><dd>${b.deep_time ? 'deep time' : (b.setting_start != null ? `${era(b.setting_start)}–${era(b.setting_end)}` : '—')}</dd>
      <dt>Rated</dt><dd>${b.rating ?? '—'}/10</dd>
      <dt>Length</dt><dd>${b.pages ? b.pages + ' pp' : '—'}</dd>
    </dl>
    ${reach != null && reach > 25 ? `<div class="gap-note">Written <b>${reach}</b> years after the moment it describes.</div>` : ''}
    ${b.setting ? `<h3>Setting</h3><p class="body">${esc(b.setting)}</p>` : ''}
    ${b.synopsis ? `<h3>What happens</h3><p class="body">${esc(b.synopsis)}</p>` : ''}
    ${b.backdrop ? `<h3>The world around it</h3><p class="body">${esc(b.backdrop)}</p>` : ''}
    ${hist ? `<h3>${esc(hist.label)}</h3><p class="body">${esc(hist.text)}</p>` : ''}
    ${b.themes?.length ? `<h3>Themes</h3><div class="themes">${b.themes.map(t => `<span>${esc(t)}</span>`).join('')}</div>` : ''}
    <a class="read" href="${b.url}" target="_blank" rel="noopener">Read the full review</a>`;
  p.hidden = false;
  p.querySelector('.close').onclick = () => { p.hidden = true; state.sel = null; render(); };
}

/* The history files are keyed by Persian country name and decade. */
function findHistory(b) {
  if (!b.country || b.year == null) return null;
  const dec = Math.floor(b.year / 10) * 10;
  const key = `${b.country.replace(/\s+/g, '_')}_${dec}`;
  const h = state.history[key];
  if (!h) return null;
  const text = typeof h === 'string' ? h
    : (h.summary || h.text || (Array.isArray(h.events) ? h.events.map(e => e.event || e).join(' · ') : null));
  return text ? { label: `${b.country} in the ${dec}s`, text: String(text).slice(0, 700) } : null;
}

const esc = s => String(s ?? '').replace(/[&<>"]/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));

// --- interaction --------------------------------------------------------------------

function wire() {
  $('#mode').onclick = e => {
    const b = e.target.closest('button'); if (!b) return;
    state.mode = b.dataset.v;
    [...$('#mode').children].forEach(x => x.setAttribute('aria-pressed', String(x === b)));
    render();
  };
  $('#minRating').oninput = e => { state.minRating = +e.target.value; $('#minRatingVal').textContent = e.target.value; render(); };
  $('#era').oninput = e => {
    state.era = +e.target.value;
    $('#eraVal').textContent = state.era <= -800 ? 'any' : (state.era < 0 ? `${-state.era} BC` : state.era);
    render();
  };
  $('#q').oninput = e => { state.q = e.target.value.trim(); render(); };
  $('#reset').onclick = () => {
    state.minRating = 1; state.era = -800; state.q = '';
    $('#minRating').value = 1; $('#minRatingVal').textContent = '1';
    $('#era').value = -800; $('#eraVal').textContent = 'any';
    $('#q').value = '';
    render();
  };

  let drag = null;
  svg.addEventListener('pointerdown', e => {
    if (state.mode !== 'map') return;
    drag = { x: e.clientX, y: e.clientY, ox: state.view.x, oy: state.view.y };
    svg.classList.add('dragging'); svg.setPointerCapture(e.pointerId);
  });
  svg.addEventListener('pointermove', e => {
    if (!drag) return;
    state.view.x = drag.ox + (e.clientX - drag.x);
    state.view.y = drag.oy + (e.clientY - drag.y);
    render();
  });
  const end = e => { drag = null; svg.classList.remove('dragging'); if (e.pointerId != null) try { svg.releasePointerCapture(e.pointerId); } catch {} };
  svg.addEventListener('pointerup', end);
  svg.addEventListener('pointercancel', end);
  svg.addEventListener('wheel', e => {
    if (state.mode !== 'map') return;
    e.preventDefault();
    const f = e.deltaY < 0 ? 1.15 : 1 / 1.15;
    state.view.k = Math.max(1, Math.min(14, state.view.k * f));
    render();
  }, { passive: false });

  addEventListener('resize', render);
  addEventListener('keydown', e => { if (e.key === 'Escape') { $('#panel').hidden = true; state.sel = null; render(); } });
}

boot().catch(e => {
  $('#readout').innerHTML = `<span>Could not load the atlas: ${esc(e.message)}. Serve this folder over HTTP.</span>`;
});
