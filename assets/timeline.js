// Timeline page logic. Data (ERAS, E, SLUGS) is inlined into timeline.html by build.py.
const out = document.getElementById('out'), eraBox = document.getElementById('eraChips'),
  sel = document.getElementById('legendSel'), majorBtn = document.getElementById('majorBtn'), count = document.getElementById('count'),
  rail = document.getElementById('rail'), hdrEl = document.querySelector('header.site'), ctlEl = document.querySelector('.controls'),
  root = document.documentElement;
const q = new URLSearchParams(location.search);
let eraOn = q.has('era') ? +q.get('era') : null, majorOnly = q.get('major') === '1', legend = q.get('legend') || '';
const names = [...new Set(E.flatMap(e => e.l || []))].sort();
names.forEach(n => { const o = document.createElement('option'); o.value = n; o.textContent = n; sel.appendChild(o) });
sel.value = names.includes(legend) ? legend : (legend = '');
const esc = s => s.replace(/[&<>"]/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));

// Vertical space between events grows with the years between them (log-scaled, capped).
function gapPx(dy) { if (!(dy > 0)) return 0; if (dy < 10) return dy * 5; return 50 + Math.min(70, Math.log2(dy / 10 + 1) * 30) }

function chip(label, color, on, fn) {
  const b = document.createElement('button'); b.type = 'button'; b.className = 'chip'; b.setAttribute('aria-pressed', on);
  b.innerHTML = (color ? `<span class="dot" style="background:var(${color})"></span>` : '') + label; b.onclick = fn; return b;
}
function drawChips() {
  eraBox.innerHTML = '';
  eraBox.appendChild(chip('All eras', null, eraOn === null, () => { eraOn = null; render() }));
  ERAS.forEach((er, i) => eraBox.appendChild(chip(esc(er.n), '--e' + i, eraOn === i, () => { eraOn = eraOn === i ? null : i; render() })));
}
function render() {
  drawChips(); majorBtn.setAttribute('aria-pressed', majorOnly);
  const list = E.filter(e => (eraOn === null || e.e === eraOn) && (!majorOnly || e.m) && (!legend || (e.l || []).includes(legend)));
  count.textContent = list.length + ' event' + (list.length === 1 ? '' : 's');
  if (!list.length) { out.innerHTML = '<div class="empty">No events match these filters.</div>'; setVars(); layout(); return }
  let html = '';
  ERAS.forEach((er, i) => {
    const items = list.filter(e => e.e === i); if (!items.length) return;
    html += `<section class="era" id="era-${i}" style="--c:var(--e${i})"><div class="era-head"><h2>${esc(er.n)}</h2><span>${er.r}</span></div><p class="era-note">${esc(er.t)}</p><div class="spine">`;
    items.forEach((e, k) => {
      const tags = [];
      if (e.m) tags.push('<span class="tag maj">Major</span>');
      if (e.s != null) tags.push(`<a class="tag" href="seasons.html#s${e.s}">Season ${e.s}</a>`);
      if (e.f) tags.push(`<span class="tag flag">${e.f==='Disputed'?'Date disputed':e.f==='Implied'?'Implied, not stated':/^approx/.test(e.f)?'Date approximate':esc(e.f)}</span>`);
      (e.l || []).forEach(n => tags.push(SLUGS[n] ? `<a class="tag" href="legends/${SLUGS[n]}.html">${esc(n)}</a>` : `<span class="tag">${esc(n)}</span>`));
      const yr = e.y ? `${e.y}${e.d ? `<small>${esc(e.d)}</small>` : ''}` : '<span class="na">Year unknown</span>';
      const prev = items[k - 1], dy = (prev && prev.y && e.y) ? e.y - prev.y : 0, same = prev && e.y && prev.y === e.y;
      let mt = 0;
      if (dy >= 10) html += `<div class="jump" style="height:${gapPx(dy)}px"><span>+${dy} years</span></div>`;
      else mt = gapPx(dy);
      html += `<article class="ev ${e.m ? 'major' : 'minor'}${same ? ' same' : ''}" style="--c:var(--e${i})${mt ? `;margin-top:${mt}px` : ''}"><div class="yr">${yr}</div><div class="card"><h3>${esc(e.t)}</h3><p>${esc(e.x)}</p><div class="meta">${tags.join('')}</div></div></article>`;
    });
    html += '</div></section>';
  });
  out.innerHTML = html;
  setVars(); layout();
}

// ---- sticky offsets (header + filter bar; on phones only the header, to save space) ----
function setVars() {
  const h = hdrEl ? hdrEl.offsetHeight : 57, c = ctlEl ? ctlEl.offsetHeight : 0, narrow = innerWidth <= 700;
  root.style.setProperty('--hdr', h + 'px');
  root.style.setProperty('--stick', (narrow ? h : h + c) + 'px');
}

// ---- year rail: a clickable mini-map of the whole list ----
let outTop = 0, H = 1, rin = null, win = null, now = null, ticking = false, dragging = false;
const stickPx = () => parseFloat(getComputedStyle(root).getPropertyValue('--stick')) || 150;
function layout() {
  if (!rail || !rail.isConnected) return cleanup();
  const evs = out.querySelectorAll('.ev');
  const wide = innerWidth >= 1180;
  if (wide && sheetOpen) closeSheet();
  if (btn) btn.hidden = wide || !evs.length;
  rail.hidden = !(evs.length && (wide || sheetOpen));
  if (rail.hidden) { update(); return }
  outTop = out.getBoundingClientRect().top + scrollY; H = Math.max(1, out.offsetHeight);
  let h = '';
  out.querySelectorAll('.era').forEach(s => {
    const t = (s.getBoundingClientRect().top + scrollY - outTop) / H * 100, i = s.id.replace('era-', '');
    const yr = ((ERAS[i].r.match(/\d{4}/) || [])[0]) || '';
    h += `<span class="rl" style="top:${t}%;--c:var(--e${i})">${yr}</span>`;
  });
  evs.forEach(e => {
    const t = (e.getBoundingClientRect().top + scrollY - outTop + 22) / H * 100;
    h += `<i class="rt ${e.classList.contains('major') ? 'maj' : ''}" style="top:${t}%;--c:${e.style.getPropertyValue('--c')}"></i>`;
  });
  h += '<div class="rwin"></div><div class="rnow"></div>';
  rin.innerHTML = h; win = rin.querySelector('.rwin'); now = rin.querySelector('.rnow');
  update();
}
function update() {
  ticking = false;
  if (!rail || !rail.isConnected) return cleanup();
  if (btn && !btn.hidden) {
    const past = scrollY + innerHeight * .4 > out.getBoundingClientRect().top + scrollY;
    btn.classList.toggle('show', past || sheetOpen);
    const c = curYear(); btnYr.textContent = c || 'Years'; btn.setAttribute('aria-label', 'Jump to a year' + (c ? ', now at ' + c : ''));
  }
  if (rail.hidden || !win) return;
  const st = stickPx(), top = Math.min(1, Math.max(0, (scrollY + st - outTop) / H)), vis = Math.min(1, (innerHeight - st) / H);
  win.style.top = top * 100 + '%'; win.style.height = Math.max(2.5, vis * 100) + '%';
  const y = curYear();
  now.textContent = y || ''; now.style.top = top * 100 + '%'; now.style.display = y ? '' : 'none';
}
function curYear() {
  const st = stickPx(), hh = (document.querySelector('.era-head') || {}).offsetHeight || 0;
  for (const e of out.querySelectorAll('.ev')) if (e.getBoundingClientRect().bottom > st + hh + 4) return (e.querySelector('.yr').textContent.match(/\d{3,4}/) || [])[0] || '';
  return '';
}
const onScroll = () => { if (!ticking) { ticking = true; requestAnimationFrame(update) } };
const onResize = () => { setVars(); layout() };
function cleanup() { removeEventListener('scroll', onScroll); removeEventListener('resize', onResize); if (ro) ro.disconnect() }
function seek(ev) {
  const r = rin.getBoundingClientRect(), f = Math.min(1, Math.max(0, (ev.clientY - r.top) / r.height));
  scrollTo({ top: outTop + f * H - stickPx(), behavior: 'instant' });
}
// ---- phone version: a floating year button that opens the same map as a bottom sheet ----
let sheetOpen = false, btn = null, btnYr = null, shade = null, sheetHead = null;
function openSheet() { sheetOpen = true; rail.classList.add('sheet'); shade.hidden = false; btn.setAttribute('aria-expanded', 'true'); layout(); sheetHead.querySelector('button').focus() }
function closeSheet() { sheetOpen = false; rail.classList.remove('sheet'); if (shade) shade.hidden = true; if (btn) { btn.setAttribute('aria-expanded', 'false') } layout() }
if (rail) {
  btn = document.createElement('button'); btn.type = 'button'; btn.id = 'railBtn'; btn.hidden = true;
  btn.setAttribute('aria-expanded', 'false'); btn.setAttribute('aria-controls', 'rail');
  btn.innerHTML = '<span class="rb-k">Jump</span><b></b>'; btnYr = btn.querySelector('b');
  btn.onclick = () => sheetOpen ? closeSheet() : openSheet();
  shade = document.createElement('div'); shade.id = 'railShade'; shade.hidden = true; shade.onclick = closeSheet;
  sheetHead = document.createElement('div'); sheetHead.className = 'sheet-head';
  sheetHead.innerHTML = '<span>Drag or tap to jump through the years</span><button type="button">Done</button>';
  sheetHead.querySelector('button').onclick = closeSheet;
  rail.parentNode.insertBefore(shade, rail); rail.parentNode.insertBefore(btn, rail); rail.appendChild(sheetHead);
  addEventListener('keydown', e => { if (e.key === 'Escape' && sheetOpen && rail.isConnected) closeSheet() });
  rin = document.createElement('div'); rin.className = 'rail-in'; rail.appendChild(rin);
  rin.addEventListener('pointerdown', e => { dragging = true; rin.setPointerCapture(e.pointerId); seek(e) });
  rin.addEventListener('pointermove', e => { if (dragging) seek(e) });
  rin.addEventListener('pointerup', () => { dragging = false });
  rin.addEventListener('pointercancel', () => { dragging = false });
}
addEventListener('scroll', onScroll, { passive: true });
addEventListener('resize', onResize);
addEventListener('load', onResize);
if (document.fonts && document.fonts.ready) document.fonts.ready.then(onResize);
const ro = (window.ResizeObserver && ctlEl) ? new ResizeObserver(() => { setVars(); layout() }) : null;
if (ro) { ro.observe(ctlEl); ro.observe(out) }

sel.onchange = () => { legend = sel.value; render() };
majorBtn.onclick = () => { majorOnly = !majorOnly; render() };
render();
