/* ==========================================================================
   Valor+ · Prototipo de rediseño — interacción y animación
   Sin dependencias. Todo efecto respeta "reducir movimiento" (sistema o panel).
   ========================================================================== */
(() => {
  'use strict';

  const doc = document.documentElement;
  const ROOT = doc.dataset.root || '';
  const $ = (s, c = document) => c.querySelector(s);
  const $$ = (s, c = document) => [...c.querySelectorAll(s)];
  const clamp = (v, a, b) => Math.min(b, Math.max(a, v));
  const store = {
    get(k) { try { return localStorage.getItem('vm.' + k); } catch { return null; } },
    set(k, v) { try { v === null ? localStorage.removeItem('vm.' + k) : localStorage.setItem('vm.' + k, v); } catch { /* sin almacenamiento */ } }
  };
  const reduced = () => doc.dataset.motion === 'reduce';
  const finePointer = matchMedia('(hover: hover) and (pointer: fine)').matches;

  doc.classList.remove('no-js');
  doc.classList.add('js');

  /* ---------- Preferencias de accesibilidad ---------- */
  const sysReduce = matchMedia('(prefers-reduced-motion: reduce)');
  function applyPrefs() {
    const theme = store.get('theme');
    theme ? doc.dataset.theme = theme : delete doc.dataset.theme;
    const contrast = store.get('contrast');
    contrast ? doc.dataset.contrast = contrast : delete doc.dataset.contrast;
    doc.style.setProperty('--fs-scale', store.get('fs') || '1');
    const motion = store.get('motion');
    doc.dataset.motion = motion || (sysReduce.matches ? 'reduce' : 'full');
    const links = store.get('links');
    links ? doc.dataset.links = links : delete doc.dataset.links;
    const font = store.get('font');
    font ? doc.dataset.font = font : delete doc.dataset.font;
  }
  applyPrefs();
  sysReduce.addEventListener?.('change', applyPrefs);

  /* ---------- Avisos breves ---------- */
  const live = document.createElement('div');
  live.className = 'sr-only'; live.setAttribute('aria-live', 'polite');
  document.body.append(live);
  function toast(msg) {
    $$('.toast').forEach(t => t.remove());
    const t = document.createElement('div');
    t.className = 'toast'; t.textContent = msg; t.setAttribute('role', 'status');
    document.body.append(t);
    setTimeout(() => t.remove(), 2600);
  }
  function announce(msg) { live.textContent = ''; setTimeout(() => { live.textContent = msg; }, 30); }

  /* ---------- Encabezado: ocultar al bajar, mostrar al subir ---------- */
  const header = $('.site-header');
  const progress = $('.scroll-progress');
  const toTop = $('.to-top');
  let lastY = scrollY;
  function onScrollUI() {
    const y = scrollY;
    const max = document.documentElement.scrollHeight - innerHeight;
    if (progress) progress.style.setProperty('--sp', max > 0 ? (y / max).toFixed(4) : 0);
    if (header) {
      const menuOpen = $('.mega.is-open');
      header.classList.toggle('is-hidden', y > 260 && y > lastY && !menuOpen && !header.contains(document.activeElement));
    }
    if (toTop) {
      toTop.classList.toggle('is-visible', y > 900);
      const c = toTop.querySelector('circle.p');
      if (c) c.style.strokeDashoffset = (1 - (max > 0 ? y / max : 0)) * 138;
    }
    lastY = y;
  }
  toTop?.addEventListener('click', () => {
    scrollTo({ top: 0, behavior: reduced() ? 'auto' : 'smooth' });
    ($('#contenido') || document.body).focus({ preventScroll: true });
  });

  /* ---------- Mega menú de Servicios ---------- */
  $$('[data-mega]').forEach(btn => {
    const panel = document.getElementById(btn.getAttribute('aria-controls'));
    if (!panel) return;
    let hoverAt = 0;
    const open = (v, viaHover = false) => {
      if (v && viaHover && btn.getAttribute('aria-expanded') !== 'true') hoverAt = performance.now();
      btn.setAttribute('aria-expanded', v);
      panel.classList.toggle('is-open', v);
      panel.toggleAttribute('inert', !v);
    };
    panel.setAttribute('inert', '');
    btn.addEventListener('click', () => {
      const isOpen = btn.getAttribute('aria-expanded') === 'true';
      // si el panel acaba de abrirse al pasar el mouse, el clic lo deja abierto
      open(!isOpen || performance.now() - hoverAt < 700);
    });
    if (finePointer) {
      let t;
      const li = btn.closest('li');
      li.addEventListener('mouseenter', () => { clearTimeout(t); open(true, true); });
      li.addEventListener('mouseleave', () => { t = setTimeout(() => open(false), 220); });
      panel.addEventListener('mouseenter', () => clearTimeout(t));
      panel.addEventListener('mouseleave', () => { t = setTimeout(() => open(false), 220); });
    }
    document.addEventListener('keydown', e => { if (e.key === 'Escape' && btn.getAttribute('aria-expanded') === 'true') { open(false); btn.focus(); } });
    document.addEventListener('click', e => { if (!panel.contains(e.target) && !btn.contains(e.target)) open(false); });
    panel.addEventListener('focusout', e => { if (!panel.contains(e.relatedTarget) && e.relatedTarget !== btn) open(false); });
  });

  /* ---------- Menú móvil ---------- */
  const mm = $('#menu-movil');
  const mmBtn = $('.nav-toggle');
  function setMobile(v) {
    if (!mm) return;
    mm.classList.toggle('is-open', v);
    mm.toggleAttribute('inert', !v);
    mmBtn?.setAttribute('aria-expanded', v);
    document.body.style.overflow = v ? 'hidden' : '';
    if (v) setTimeout(() => $('.mm-close', mm)?.focus(), 60); else mmBtn?.focus();
  }
  if (mm) {
    mm.setAttribute('inert', '');
    mmBtn?.addEventListener('click', () => setMobile(true));
    $('.mm-close', mm)?.addEventListener('click', () => setMobile(false));
    mm.addEventListener('keydown', e => {
      if (e.key === 'Escape') setMobile(false);
      if (e.key === 'Tab') { // atrapar el foco dentro del menú
        const f = $$('a, button', mm).filter(el => el.offsetParent !== null);
        if (e.shiftKey && document.activeElement === f[0]) { e.preventDefault(); f.at(-1).focus(); }
        else if (!e.shiftKey && document.activeElement === f.at(-1)) { e.preventDefault(); f[0].focus(); }
      }
    });
    $$('a', mm).forEach((a, i) => a.closest('nav > ul > li')?.style.setProperty('--i', i));
  }

  /* ---------- Aparición al hacer scroll ---------- */
  const revealIO = new IntersectionObserver(entries => {
    entries.forEach(e => { if (e.isIntersecting) { e.target.classList.add('is-in'); revealIO.unobserve(e.target); } });
  }, { rootMargin: '0px 0px -8% 0px', threshold: .08 });
  $$('[data-reveal]').forEach(el => revealIO.observe(el));
  // Escalonar hijos
  $$('[data-stagger]').forEach(group => {
    [...group.children].forEach((c, i) => { c.setAttribute('data-reveal', c.dataset.reveal || ''); c.style.setProperty('--d', i * (+group.dataset.stagger || 80)); revealIO.observe(c); });
  });

  /* ---------- Separar palabras (titulares) ---------- */
  function splitWords(el, cls = 'w') {
    if (el.dataset.split) return [];
    el.dataset.split = '1';
    const words = [];
    const walk = (node) => {
      [...node.childNodes].forEach(n => {
        if (n.nodeType === 3) {
          const frag = document.createDocumentFragment();
          n.textContent.split(/(\s+)/).forEach(part => {
            if (!part) return;
            if (/^\s+$/.test(part)) { frag.append(part); return; }
            const s = document.createElement('span'); s.className = cls; s.textContent = part;
            if (node.classList?.contains('hl')) s.classList.add('hl');
            frag.append(s); words.push(s);
          });
          n.replaceWith(frag);
        } else if (n.nodeType === 1) walk(n);
      });
    };
    walk(el);
    words.forEach((w, i) => w.style.setProperty('--i', i));
    return words;
  }
  $$('.split-words').forEach(el => splitWords(el));

  /* ---------- Declaración que se ilumina ---------- */
  const statements = $$('.statement').map(el => ({ el, words: splitWords(el) }));

  /* ---------- Escenario con zoom ---------- */
  const zooms = $$('.zoom-stage').map(stage => ({ stage, card: $('.zoom-card', stage), title: $('.zoom-title', stage) }));

  /* ---------- Paralaje ---------- */
  const parallax = $$('[data-parallax]');

  function onScrollFX() {
    if (reduced()) return;
    const vh = innerHeight;
    statements.forEach(({ el, words }) => {
      const r = el.getBoundingClientRect();
      const p = clamp((vh * .85 - r.top) / (r.height + vh * .35), 0, 1);
      const n = Math.round(p * words.length);
      words.forEach((w, i) => w.classList.toggle('on', i < n));
    });
    zooms.forEach(({ stage, card, title }) => {
      const r = stage.getBoundingClientRect();
      const p = clamp(-r.top / (r.height - vh), 0, 1);
      const eased = 1 - Math.pow(1 - clamp(p * 1.35, 0, 1), 3);
      card?.style.setProperty('--p', eased.toFixed(4));
      title?.style.setProperty('--p', eased.toFixed(4));
    });
    parallax.forEach(el => {
      const r = el.getBoundingClientRect();
      const speed = parseFloat(el.dataset.parallax) || .15;
      el.style.setProperty('--py', ((r.top + r.height / 2 - vh / 2) * -speed).toFixed(1));
    });
  }
  let ticking = false;
  addEventListener('scroll', () => {
    if (ticking) return;
    ticking = true;
    requestAnimationFrame(() => { onScrollUI(); onScrollFX(); ticking = false; });
  }, { passive: true });
  addEventListener('resize', onScrollFX);
  onScrollUI(); onScrollFX();

  /* ---------- Contadores ---------- */
  const fmt = (v, dec) => v.toLocaleString('es-CO', { minimumFractionDigits: dec, maximumFractionDigits: dec });
  const countIO = new IntersectionObserver(entries => {
    entries.forEach(e => {
      if (!e.isIntersecting) return;
      countIO.unobserve(e.target);
      const el = e.target, end = parseFloat(el.dataset.count), dec = +(el.dataset.dec || 0);
      if (reduced()) { el.textContent = fmt(end, dec); return; }
      const t0 = performance.now(), dur = 1800;
      const step = (t) => {
        const k = clamp((t - t0) / dur, 0, 1), eased = 1 - Math.pow(1 - k, 4);
        el.textContent = fmt(end * eased, dec);
        if (k < 1) requestAnimationFrame(step);
      };
      requestAnimationFrame(step);
    });
  }, { threshold: .5 });
  $$('[data-count]').forEach(el => countIO.observe(el));

  /* ---------- Narrativa con panel fijo (servicios) ---------- */
  $$('.scrolly').forEach(sc => {
    const figs = $$('.scrolly-visual figure', sc);
    const steps = $$('.scrolly-step', sc);
    const io = new IntersectionObserver(entries => {
      entries.forEach(e => {
        if (!e.isIntersecting) return;
        const i = steps.indexOf(e.target);
        steps.forEach((s, j) => s.classList.toggle('is-active', i === j));
        figs.forEach((f, j) => f.classList.toggle('is-active', i === j));
      });
    }, { rootMargin: '-45% 0px -45% 0px' });
    steps.forEach(s => io.observe(s));
    steps[0]?.classList.add('is-active'); figs[0]?.classList.add('is-active');
  });

  /* ---------- Carruseles horizontales ---------- */
  $$('.rail-wrap').forEach(wrap => {
    const rail = $('.rail', wrap);
    const bar = $('.rail-progress span', wrap);
    const page = () => rail.clientWidth * .85;
    $('[data-rail="prev"]', wrap)?.addEventListener('click', () => rail.scrollBy({ left: -page(), behavior: reduced() ? 'auto' : 'smooth' }));
    $('[data-rail="next"]', wrap)?.addEventListener('click', () => rail.scrollBy({ left: page(), behavior: reduced() ? 'auto' : 'smooth' }));
    const upd = () => {
      const max = rail.scrollWidth - rail.clientWidth;
      if (bar) { bar.style.width = Math.max(12, rail.clientWidth / rail.scrollWidth * 100) + '%'; bar.style.transform = `translateX(${max ? rail.scrollLeft / max * (100 / (parseFloat(bar.style.width) / 100) - 100) : 0}%)`; }
    };
    rail.addEventListener('scroll', upd, { passive: true }); upd(); addEventListener('resize', upd);
    // Arrastrar con el mouse
    let down = false, sx = 0, sl = 0, moved = false;
    rail.addEventListener('pointerdown', e => { if (e.pointerType !== 'mouse') return; down = true; moved = false; sx = e.clientX; sl = rail.scrollLeft; });
    addEventListener('pointermove', e => { if (!down) return; const dx = e.clientX - sx; if (Math.abs(dx) > 5) { moved = true; rail.classList.add('dragging'); } rail.scrollLeft = sl - dx; });
    addEventListener('pointerup', () => { if (!down) return; down = false; rail.classList.remove('dragging'); });
    rail.addEventListener('click', e => { if (moved) { e.preventDefault(); e.stopPropagation(); moved = false; } }, true);
  });

  /* ---------- Marquesina de clientes ---------- */
  $$('.marquee').forEach(mq => {
    const track = $('.marquee-track', mq);
    [...track.children].forEach(li => {
      const c = li.cloneNode(true); c.setAttribute('aria-hidden', 'true');
      $$('a', c).forEach(a => a.tabIndex = -1);
      $$('img', c).forEach(i => i.alt = '');
      track.append(c);
    });
    const btn = mq.parentElement.querySelector('.pause-btn');
    btn?.addEventListener('click', () => {
      const p = mq.classList.toggle('is-paused');
      btn.setAttribute('aria-pressed', p);
      btn.querySelector('span').textContent = p ? 'Reanudar movimiento' : 'Pausar movimiento';
    });
  });

  /* ---------- Red de partículas del hero ---------- */
  $$('canvas.net').forEach(cv => {
    const ctx = cv.getContext('2d');
    const btn = cv.parentElement.querySelector('.hero-pause');
    let w, h, dpr, pts = [], raf = 0, running = true, visible = true;
    const mouse = { x: -9999, y: -9999 };
    const colors = ['#00c26a', '#00a3e0', '#4f9dff', '#b8d430'];
    function init() {
      dpr = Math.min(devicePixelRatio || 1, 2);
      w = cv.clientWidth; h = cv.clientHeight;
      cv.width = w * dpr; cv.height = h * dpr; ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
      const n = Math.round(clamp(w * h / 14000, 30, 110));
      pts = Array.from({ length: n }, () => ({ x: Math.random() * w, y: Math.random() * h, vx: (Math.random() - .5) * .35, vy: (Math.random() - .5) * .35, r: Math.random() * 1.8 + .8, c: colors[Math.random() * colors.length | 0] }));
    }
    function draw() {
      ctx.clearRect(0, 0, w, h);
      const link = Math.min(150, w / 7);
      for (let i = 0; i < pts.length; i++) {
        const p = pts[i];
        if (running && !reduced()) {
          p.x += p.vx; p.y += p.vy;
          const dx = mouse.x - p.x, dy = mouse.y - p.y, d = Math.hypot(dx, dy);
          if (d < 180) { p.x -= dx / d * .6; p.y -= dy / d * .6; }
          if (p.x < 0 || p.x > w) p.vx *= -1;
          if (p.y < 0 || p.y > h) p.vy *= -1;
        }
        for (let j = i + 1; j < pts.length; j++) {
          const q = pts[j], d = Math.hypot(p.x - q.x, p.y - q.y);
          if (d < link) { ctx.strokeStyle = `rgba(140, 200, 255, ${(1 - d / link) * .28})`; ctx.lineWidth = 1; ctx.beginPath(); ctx.moveTo(p.x, p.y); ctx.lineTo(q.x, q.y); ctx.stroke(); }
        }
        ctx.fillStyle = p.c; ctx.beginPath(); ctx.arc(p.x, p.y, p.r, 0, Math.PI * 2); ctx.fill();
      }
    }
    function loop() { draw(); raf = (running && visible && !reduced()) ? requestAnimationFrame(loop) : 0; }
    function start() { if (!raf) loop(); }
    init(); loop();
    addEventListener('resize', () => { init(); draw(); });
    cv.parentElement.addEventListener('pointermove', e => { const r = cv.getBoundingClientRect(); mouse.x = e.clientX - r.left; mouse.y = e.clientY - r.top; });
    cv.parentElement.addEventListener('pointerleave', () => { mouse.x = mouse.y = -9999; });
    new IntersectionObserver(([e]) => { visible = e.isIntersecting; if (visible) start(); }).observe(cv);
    function setRunning(v) {
      running = v;
      if (btn) {
        btn.setAttribute('aria-pressed', !v);
        btn.setAttribute('aria-label', v ? 'Pausar animación de fondo' : 'Reanudar animación de fondo');
        btn.innerHTML = v ? '<svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><rect x="6" y="5" width="4" height="14" rx="1"/><rect x="14" y="5" width="4" height="14" rx="1"/></svg>' : '<svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M8 5v14l11-7z"/></svg>';
      }
      $$('.aurora span', cv.parentElement).forEach(s => s.style.animationPlayState = v ? '' : 'paused');
      start();
    }
    btn?.addEventListener('click', () => setRunning(!running));
    if (reduced()) setRunning(false);
  });

  /* ---------- Inclinación 3D, brillo y botones magnéticos ---------- */
  if (finePointer) {
    document.addEventListener('pointermove', e => {
      const sp = e.target.closest?.('.spotlight');
      if (sp) { const r = sp.getBoundingClientRect(); sp.style.setProperty('--mx', (e.clientX - r.left) + 'px'); sp.style.setProperty('--my', (e.clientY - r.top) + 'px'); }
    }, { passive: true });
    $$('.tilt').forEach(el => {
      el.addEventListener('pointermove', e => {
        if (reduced()) return;
        const r = el.getBoundingClientRect(), x = (e.clientX - r.left) / r.width - .5, y = (e.clientY - r.top) / r.height - .5;
        el.classList.add('is-tilting');
        el.style.setProperty('--rx', (-y * 7).toFixed(2) + 'deg'); el.style.setProperty('--ry', (x * 9).toFixed(2) + 'deg');
      });
      el.addEventListener('pointerleave', () => { el.classList.remove('is-tilting'); el.style.setProperty('--rx', '0deg'); el.style.setProperty('--ry', '0deg'); });
    });
    $$('[data-magnetic]').forEach(el => {
      el.addEventListener('pointermove', e => {
        if (reduced()) return;
        const r = el.getBoundingClientRect();
        el.style.transform = `translate(${(e.clientX - r.left - r.width / 2) * .25}px, ${(e.clientY - r.top - r.height / 2) * .35}px)`;
      });
      el.addEventListener('pointerleave', () => { el.style.transform = ''; });
    });
  }

  /* ---------- Paleta de búsqueda (Ctrl/⌘ + K) ---------- */
  const palette = $('#paleta');
  let index = null, filter = 'todo', active = -1, results = [];
  const norm = s => (s || '').toLowerCase().normalize('NFD').replace(/[̀-ͯ]/g, '');
  const esc = s => s.replace(/[&<>"]/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));
  const KIND = { pagina: 'Página', servicio: 'Servicio', caso: 'Caso de éxito', doc: 'Transparencia', proceso: 'Contratación' };
  const ICON = {
    pagina: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M4 4h16v16H4z"/><path d="M4 9h16"/></svg>',
    servicio: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="3"/><path d="M12 2v3M12 19v3M2 12h3M19 12h3M4.9 4.9l2.1 2.1M17 17l2.1 2.1M4.9 19.1 7 17M17 7l2.1-2.1"/></svg>',
    caso: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 2l3 7h7l-5.5 4.5 2 7.5L12 16.5 5.5 21l2-7.5L2 9h7z"/></svg>',
    proceso: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M9 11l3 3 8-8"/><path d="M20 12v7a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h9"/></svg>'
  };
  function loadIndex() {
    return new Promise(res => {
      if (window.VM_INDEX) return res(window.VM_INDEX);
      const s = document.createElement('script');
      s.src = ROOT + 'assets/js/indice-busqueda.js';
      s.onload = () => res(window.VM_INDEX || []);
      s.onerror = () => res([]);
      document.head.append(s);
    }).then(ix => { index = ix.map(r => ({ ...r, n: norm(r.t + ' ' + (r.s || '')) , nt: norm(r.t) })); return index; });
  }
  function highlight(text, terms) {
    let out = esc(text);
    terms.forEach(t => {
      if (t.length < 2) return;
      const re = new RegExp('(' + t.replace(/[.*+?^${}()|[\]\\]/g, '\\$&').split('').map(ch => {
        const m = { a: '[aá]', e: '[eé]', i: '[ií]', o: '[oó]', u: '[uúü]', n: '[nñ]' }; return m[ch] || ch;
      }).join('') + ')', 'gi');
      out = out.replace(re, '<mark>$1</mark>');
    });
    return out;
  }
  function search(q) {
    const list = $('.palette-results', palette);
    const terms = norm(q).split(/\s+/).filter(Boolean);
    let pool = index || [];
    if (filter !== 'todo') pool = pool.filter(r => filter === 'servicio' ? (r.k === 'servicio' || r.k === 'caso') : r.k === filter);
    if (!terms.length) {
      results = pool.filter(r => r.k !== 'doc' || filter === 'doc').slice(0, 14);
    } else {
      results = pool.map(r => {
        if (!terms.every(t => r.n.includes(t))) return null;
        let sc = 0; terms.forEach(t => { if (r.nt.startsWith(t)) sc += 6; if (r.nt.includes(t)) sc += 3; else sc += 1; });
        if (r.k === 'pagina' || r.k === 'servicio') sc += 3;
        if (r.k === 'caso') sc += 2;
        return { r, sc };
      }).filter(Boolean).sort((a, b) => b.sc - a.sc).slice(0, 60).map(x => x.r);
    }
    active = results.length ? 0 : -1;
    list.innerHTML = results.length ? results.map((r, i) => {
      const ext = r.k === 'doc' ? (r.f || 'web') : '';
      const ico = r.k === 'doc' ? `<span class="ico">${esc(ext.toUpperCase())}</span>` : `<span class="ico" aria-hidden="true">${ICON[r.k] || ICON.pagina}</span>`;
      const ext_ = /^https?:/.test(r.u);
      return `<li role="option" id="pr-${i}" aria-selected="${i === active}"><a href="${ext_ ? r.u : ROOT + r.u}" class="${i === active ? 'is-active' : ''}"${ext_ ? ' target="_blank" rel="noopener"' : ''}>${ico}<span><span class="ttl">${highlight(r.t, terms)}</span><span class="sub">${esc(KIND[r.k] || '')}${r.s ? ' · ' + esc(r.s) : ''}</span></span></a></li>`;
    }).join('') : `<li class="palette-empty">No encontramos resultados para “${esc(q)}”. Prueba con otra palabra o revisa el <a href="${ROOT}mapa-del-sitio.html">mapa del sitio</a>.</li>`;
    $('input', palette).setAttribute('aria-activedescendant', active >= 0 ? 'pr-' + active : '');
    announce(results.length ? `${results.length} resultados` : 'Sin resultados');
  }
  function moveActive(d) {
    const items = $$('.palette-results a', palette);
    if (!items.length) return;
    items[active]?.classList.remove('is-active'); items[active]?.parentElement.setAttribute('aria-selected', 'false');
    active = (active + d + items.length) % items.length;
    items[active].classList.add('is-active'); items[active].parentElement.setAttribute('aria-selected', 'true');
    items[active].scrollIntoView({ block: 'nearest' });
    $('input', palette).setAttribute('aria-activedescendant', 'pr-' + active);
  }
  async function openPalette(q = '') {
    if (!palette) return;
    const opener = document.activeElement;
    palette.showModal();
    palette.addEventListener('close', () => opener?.focus?.(), { once: true });
    const input = $('input', palette);
    input.value = q;
    input.focus();
    $('.palette-results', palette).innerHTML = '<li class="palette-empty">Cargando índice…</li>';
    if (!index) await loadIndex();
    search(input.value);
  }
  if (palette) {
    const input = $('input', palette);
    input.addEventListener('input', () => search(input.value));
    input.addEventListener('keydown', e => {
      if (e.key === 'ArrowDown') { e.preventDefault(); moveActive(1); }
      if (e.key === 'ArrowUp') { e.preventDefault(); moveActive(-1); }
      if (e.key === 'Enter') { const a = $$('.palette-results a', palette)[active]; if (a) { e.preventDefault(); a.click(); } }
    });
    $$('.palette-filters .chip', palette).forEach(ch => ch.addEventListener('click', () => {
      filter = ch.dataset.f;
      $$('.palette-filters .chip', palette).forEach(c => c.setAttribute('aria-pressed', c === ch));
      search(input.value); input.focus();
    }));
    palette.addEventListener('click', e => { if (e.target === palette) palette.close(); });
    palette.addEventListener('keydown', e => { if (e.key === 'Escape') { e.preventDefault(); palette.close(); } });
    $('[data-close]', palette)?.addEventListener('click', () => palette.close());
  }
  $$('[data-open-search]').forEach(b => b.addEventListener('click', e => { if (palette) { e.preventDefault(); openPalette(); } }));
  document.addEventListener('keydown', e => {
    const typing = /input|textarea|select/i.test(document.activeElement?.tagName) || document.activeElement?.isContentEditable;
    if ((e.key === 'k' || e.key === 'K') && (e.ctrlKey || e.metaKey)) { e.preventDefault(); palette?.open ? palette.close() : openPalette(); }
    else if (e.key === '/' && !typing && palette && !palette.open) { e.preventDefault(); openPalette(); }
  });
  // Página de búsqueda sin JS → con JS usa el mismo índice
  const searchPage = $('#buscar-pagina');
  if (searchPage) {
    const q = new URLSearchParams(location.search).get('q') || '';
    const inp = $('input', searchPage); inp.value = q;
    const out = $('#buscar-resultados');
    const run = async () => {
      if (!index) await loadIndex();
      const terms = norm(inp.value).split(/\s+/).filter(Boolean);
      const res = terms.length ? index.filter(r => terms.every(t => r.n.includes(t))).slice(0, 200) : [];
      out.innerHTML = terms.length ? `<p class="muted">${res.length} resultados</p><ul class="docs">${res.map(r => `<li class="doc"><a href="${/^https?:/.test(r.u) ? r.u : ROOT + r.u}"><span class="ft ${r.f || 'web'}">${(r.f || (KIND[r.k] || '').slice(0, 4)).toUpperCase()}</span><span class="t">${highlight(r.t, terms)}<span class="d">${esc(KIND[r.k] || '')}${r.s ? ' · ' + esc(r.s) : ''}</span></span></a></li>`).join('')}</ul>` : '';
      announce(`${res.length} resultados`);
    };
    searchPage.addEventListener('submit', e => { e.preventDefault(); history.replaceState(null, '', '?q=' + encodeURIComponent(inp.value)); run(); });
    if (q) run();
  }

  /* ---------- Panel de accesibilidad ---------- */
  const a11y = $('#accesibilidad');
  function syncA11y() {
    if (!a11y) return;
    const fs = store.get('fs') || '1';
    $$('[data-fs]', a11y).forEach(b => b.setAttribute('aria-pressed', b.dataset.fs === fs));
    const th = store.get('theme') || 'auto';
    $$('[data-theme-set]', a11y).forEach(b => b.setAttribute('aria-pressed', b.dataset.themeSet === th));
    $('[data-sw="contrast"]', a11y)?.setAttribute('aria-checked', store.get('contrast') === 'high');
    $('[data-sw="motion"]', a11y)?.setAttribute('aria-checked', doc.dataset.motion === 'reduce');
    $('[data-sw="links"]', a11y)?.setAttribute('aria-checked', store.get('links') === 'underline');
    $('[data-sw="font"]', a11y)?.setAttribute('aria-checked', store.get('font') === 'legible');
  }
  if (a11y) {
    $$('[data-fs]', a11y).forEach(b => b.addEventListener('click', () => { store.set('fs', b.dataset.fs === '1' ? null : b.dataset.fs); applyPrefs(); syncA11y(); announce('Tamaño de texto actualizado'); }));
    $$('[data-theme-set]', a11y).forEach(b => b.addEventListener('click', () => { store.set('theme', b.dataset.themeSet === 'auto' ? null : b.dataset.themeSet); applyPrefs(); syncA11y(); }));
    $$('[data-sw]', a11y).forEach(sw => sw.addEventListener('click', () => {
      const k = sw.dataset.sw, on = sw.getAttribute('aria-checked') !== 'true';
      if (k === 'contrast') store.set('contrast', on ? 'high' : null);
      if (k === 'motion') store.set('motion', on ? 'reduce' : 'full');
      if (k === 'links') store.set('links', on ? 'underline' : null);
      if (k === 'font') store.set('font', on ? 'legible' : null);
      applyPrefs(); syncA11y();
      if (k === 'motion') { announce(on ? 'Animaciones detenidas' : 'Animaciones activadas'); if (!on) location.reload(); }
    }));
    $('[data-a11y-reset]', a11y)?.addEventListener('click', () => { ['fs', 'theme', 'contrast', 'motion', 'links', 'font'].forEach(k => store.set(k, null)); applyPrefs(); syncA11y(); announce('Preferencias restablecidas'); });
    $('[data-close]', a11y)?.addEventListener('click', () => a11y.close());
    a11y.addEventListener('click', e => { if (e.target === a11y) a11y.close(); });
    a11y.addEventListener('keydown', e => { if (e.key === 'Escape') { e.preventDefault(); a11y.close(); } });
  }
  $$('[data-open-a11y]').forEach(b => b.addEventListener('click', () => { syncA11y(); a11y?.showModal(); a11y?.addEventListener('close', () => b.focus(), { once: true }); }));
  // Botón rápido de tema
  $$('[data-theme-toggle]').forEach(b => b.addEventListener('click', () => {
    const isDark = doc.dataset.theme === 'dark' || (!doc.dataset.theme && matchMedia('(prefers-color-scheme: dark)').matches);
    store.set('theme', isDark ? 'light' : 'dark'); applyPrefs(); syncA11y();
    announce(isDark ? 'Tema claro activado' : 'Tema oscuro activado');
  }));

  /* ---------- Aviso de cookies (Ley 1581 de 2012) ---------- */
  const cookie = $('#cookies');
  if (cookie && !store.get('cookies')) {
    cookie.hidden = false;
    $$('[data-cookies]', cookie).forEach(b => b.addEventListener('click', () => { store.set('cookies', b.dataset.cookies); cookie.remove(); toast(b.dataset.cookies === 'todas' ? 'Preferencias guardadas: todas las cookies' : 'Preferencias guardadas: solo necesarias'); }));
  }

  /* ---------- Copiar enlace / compartir ---------- */
  async function copy(text) {
    try { await navigator.clipboard.writeText(text); toast('Enlace copiado'); }
    catch { prompt('Copia este enlace:', text); }
  }
  $$('[data-copy]').forEach(b => b.addEventListener('click', () => copy(location.href.split('#')[0] + b.dataset.copy)));
  $$('[data-share]').forEach(b => b.addEventListener('click', async () => {
    const data = { title: document.title, url: location.href };
    if (navigator.share) { try { await navigator.share(data); } catch { /* cancelado */ } } else copy(location.href);
  }));

  /* ---------- Filtro dentro de Transparencia ---------- */
  const tf = $('#t-filtro');
  if (tf) {
    const scope = $(tf.dataset.scope || 'main');
    const out = $('#t-filtro-estado');
    const items = $$('.doc, .t-cats > li', scope);
    let t;
    tf.addEventListener('input', () => {
      clearTimeout(t);
      t = setTimeout(() => {
        const q = norm(tf.value.trim());
        let n = 0;
        items.forEach(it => { const hit = !q || norm(it.textContent).includes(q); it.hidden = !hit; if (hit) n++; });
        $$('details.acc', scope).forEach(d => {
          const any = $$('.doc', d).some(x => !x.hidden);
          d.hidden = q && !any && !norm($('summary', d).textContent).includes(q);
          if (q && any) d.open = true;
        });
        $$('.t-section', scope).forEach(s => { s.hidden = q && !$$('.doc', s).some(x => !x.hidden) && !norm(s.querySelector('h2')?.textContent).includes(q); });
        if (out) out.textContent = q ? `${n} coincidencias para “${tf.value.trim()}”` : '';
      }, 120);
    });
  }

  /* ---------- Filtros con chips (casos, convocatorias) ---------- */
  $$('[data-filter-group]').forEach(group => {
    const target = $(group.dataset.filterGroup);
    const out = $(group.dataset.status || '');
    $$('.chip', group).forEach(ch => ch.addEventListener('click', () => {
      const f = ch.dataset.filter;
      const apply = () => {
        $$('.chip', group).forEach(c => c.setAttribute('aria-pressed', c === ch));
        let n = 0;
        $$('[data-tags]', target).forEach(el => { const hit = f === 'todos' || el.dataset.tags.split(' ').includes(f); el.hidden = !hit; if (hit) n++; });
        if (out) out.textContent = `${n} resultados`;
      };
      if (document.startViewTransition && !reduced()) document.startViewTransition(apply); else apply();
    }));
  });

  /* ---------- Validación de formularios ---------- */
  function validateField(f) {
    const err = document.getElementById((f.type === 'radio' ? f.name : f.id) + '-error');
    let msg = '';
    if (f.type === 'checkbox' && f.required && !f.checked) msg = 'Debes aceptar para continuar.';
    else if (f.type === 'file' && f.required && !f.files.length) msg = 'Adjunta el archivo solicitado.';
    else if (f.type === 'radio' && f.required) {
      const g = $$(`input[name="${f.name}"]`, f.form);
      if (!g.some(x => x.checked)) msg = 'Selecciona una opción.';
    }
    else if (f.required && !f.value.trim()) msg = 'Este campo es obligatorio.';
    else if (f.type === 'email' && f.value && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(f.value)) msg = 'Escribe un correo válido, por ejemplo nombre@dominio.com.';
    else if (f.type === 'tel' && f.value && !/^[\d\s+()-]{7,}$/.test(f.value)) msg = 'Escribe un número de teléfono válido.';
    else if (f.pattern && f.value && !new RegExp('^(?:' + f.pattern + ')$').test(f.value)) msg = f.dataset.patternMsg || 'Revisa el formato.';
    f.setAttribute('aria-invalid', !!msg);
    if (err) { err.hidden = !msg; err.querySelector('span') ? err.querySelector('span').textContent = msg : err.textContent = msg; }
    return !msg;
  }
  function validateIn(container) {
    const fields = $$('input, select, textarea', container).filter(f => f.willValidate !== false && !f.closest('[hidden]'));
    const seen = new Set();
    const bad = fields.filter(f => { if (f.type === 'radio') { if (seen.has(f.name)) return false; seen.add(f.name); } return !validateField(f); });
    if (bad.length) { bad[0].focus(); announce(`Hay ${bad.length} campo${bad.length > 1 ? 's' : ''} por corregir`); }
    return !bad.length;
  }
  $$('form[data-validate]').forEach(form => {
    form.noValidate = true;
    $$('input, select, textarea', form).forEach(f => f.addEventListener('blur', () => { if (f.value || f.getAttribute('aria-invalid') === 'true') validateField(f); }));
    form.addEventListener('submit', e => {
      e.preventDefault();
      if (!validateIn(form)) return;
      const ok = $('.form-alert.ok', form.parentElement) || $('.form-alert.ok', form);
      if (ok) { ok.hidden = false; ok.focus(); }
      form.reset();
      $$('.file-list', form).forEach(l => l.textContent = '');
    });
  });

  /* ---------- Carga de archivos ---------- */
  $$('.dropzone').forEach(dz => {
    const input = $('input[type=file]', dz);
    const list = $('.file-list', dz.parentElement);
    const show = () => { if (list) list.textContent = input.files.length ? 'Seleccionado: ' + [...input.files].map(f => `${f.name} (${Math.ceil(f.size / 1024)} KB)`).join(', ') : ''; };
    input?.addEventListener('change', show);
    ['dragenter', 'dragover'].forEach(ev => dz.addEventListener(ev, e => { e.preventDefault(); dz.classList.add('is-over'); }));
    ['dragleave', 'drop'].forEach(ev => dz.addEventListener(ev, e => { e.preventDefault(); dz.classList.remove('is-over'); }));
    dz.addEventListener('drop', e => { if (input && e.dataTransfer.files.length) { input.files = e.dataTransfer.files; show(); } });
  });

  /* ---------- Asistente de PQRSD (simulación) ---------- */
  const wiz = $('#pqrsd-asistente');
  if (wiz) {
    const panels = $$('.step-panel', wiz);
    const steps = $$('.stepper li', wiz);
    let cur = 0;
    const anon = $('#solicitante', wiz);
    const isAnon = () => anon?.value === 'Anónimo';
    const go = (i, focus = true) => {
      panels.forEach((p, j) => p.hidden = j !== i);
      steps.forEach((s, j) => { s.classList.toggle('done', j < i); j === i ? s.setAttribute('aria-current', 'step') : s.removeAttribute('aria-current'); });
      cur = i;
      const h = panels[i].querySelector('h3'); h?.setAttribute('tabindex', '-1'); if (focus) h?.focus();
      if (i === panels.length - 1) {
        const data = new FormData(wiz);
        $('#pq-resumen', wiz).innerHTML = [
          ['Tipo de solicitud', data.get('tipo')],
          ['Tipo de solicitante', data.get('solicitante')],
          ['Solicitante', isAnon() ? 'Anónimo' : `${data.get('nombre') || ''} ${data.get('apellido') || ''}`],
          ['Correo de respuesta', isAnon() ? '—' : data.get('correo')],
          ['Asunto', data.get('asunto')]
        ].map(([k, v]) => `<li><strong>${k}:</strong> ${esc(String(v || '—'))}</li>`).join('');
      }
    };
    anon?.addEventListener('change', () => $$('[data-identidad]', wiz).forEach(el => { el.hidden = isAnon(); }));
    $$('[data-next]', wiz).forEach(b => b.addEventListener('click', () => { if (validateIn(panels[cur])) go(cur + 1); }));
    $$('[data-prev]', wiz).forEach(b => b.addEventListener('click', () => go(cur - 1)));
    wiz.addEventListener('submit', e => {
      e.preventDefault();
      if (!validateIn(panels[cur])) return;
      const n = 'VM-' + new Date().getFullYear() + '-' + String(Math.floor(Math.random() * 900000) + 100000);
      wiz.hidden = true;
      const done = $('#pq-listo'); done.hidden = false;
      $('#pq-radicado').textContent = n;
      done.focus();
    });
    go(0, false);
  }
  const consulta = $('#pq-consulta');
  consulta?.addEventListener('submit', e => {
    e.preventDefault();
    if (!validateIn(consulta)) return;
    const r = $('#pq-consulta-res'); r.hidden = false; r.focus();
  });

  /* ---------- Menú de categorías de Transparencia: cerrado en pantallas pequeñas ---------- */
  if (matchMedia('(max-width: 999px)').matches) $$('.t-nav details').forEach(d => d.open = false);

  /* ---------- Año actual en el pie ---------- */
  $$('[data-year]').forEach(el => { el.textContent = new Date().getFullYear(); });
})();
