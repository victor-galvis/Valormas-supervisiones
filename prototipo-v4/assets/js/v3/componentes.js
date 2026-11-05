/* ==========================================================================
   Valor+ · Prototipo v1.0 — funciones base (sin dependencias, funciona sin servidor)
   Accesibilidad, menú, apariciones, contadores, pestañas, flujo, formularios y
   gráficas SVG interactivas con tabla de datos equivalente.
   ========================================================================== */
(() => {
  'use strict';
  const doc = document.documentElement;
  const $ = (s, c = document) => c.querySelector(s);
  const $$ = (s, c = document) => [...c.querySelectorAll(s)];
  const guardar = (k, v) => { try { v == null ? localStorage.removeItem('v1.' + k) : localStorage.setItem('v1.' + k, v); } catch { /* sin almacenamiento */ } };
  const leer = k => { try { return localStorage.getItem('v1.' + k); } catch { return null; } };
  const fmt = n => Number(n).toLocaleString('es-CO');

  const vivo = document.createElement('p');
  vivo.className = 'sr-only'; vivo.setAttribute('aria-live', 'polite');
  document.body.append(vivo);
  const anunciar = t => { vivo.textContent = ''; setTimeout(() => { vivo.textContent = t; }, 40); };
  window.VM = Object.assign(window.VM || {}, { anunciar, fmt });

  /* ---------- Apariciones y contadores ---------- */
  const io = new IntersectionObserver(es => es.forEach(e => { if (e.isIntersecting) { e.target.classList.add('visible'); io.unobserve(e.target); } }), { rootMargin: '0px 0px -8% 0px' });
  $$('[data-aparece]').forEach(el => io.observe(el));
  const ioC = new IntersectionObserver(es => es.forEach(e => {
    if (!e.isIntersecting) return;
    ioC.unobserve(e.target);
    const el = e.target, fin = +el.dataset.cuenta;
    if (doc.dataset.motion === 'reduce') { el.textContent = fmt(fin); return; }
    const t0 = performance.now();
    const paso = t => { const k = Math.min(1, (t - t0) / 1600), v = Math.round(fin * (1 - Math.pow(1 - k, 4))); el.textContent = fmt(v); if (k < 1) requestAnimationFrame(paso); };
    requestAnimationFrame(paso);
  }), { threshold: .4 });
  $$('[data-cuenta]').forEach(el => ioC.observe(el));

  /* ---------- Pestañas accesibles ---------- */
  $$('[role="tablist"]').forEach(lista => {
    const tabs = $$('[role="tab"]', lista);
    const elegir = (i, foco) => {
      tabs.forEach((t, j) => {
        t.setAttribute('aria-selected', i === j); t.tabIndex = i === j ? 0 : -1;
        const p = document.getElementById(t.getAttribute('aria-controls')); if (p) p.hidden = i !== j;
      });
      if (foco) tabs[i].focus();
      lista.dispatchEvent(new CustomEvent('vm:tab', { detail: i, bubbles: true }));
    };
    tabs.forEach((t, i) => {
      t.addEventListener('click', () => elegir(i));
      t.addEventListener('keydown', e => {
        if (e.key === 'ArrowRight') elegir((i + 1) % tabs.length, true);
        if (e.key === 'ArrowLeft') elegir((i - 1 + tabs.length) % tabs.length, true);
      });
    });
    lista.__elegir = elegir;
  });

  /* ---------- Flujo de pasos ---------- */
  $$('.flujo').forEach(fl => {
    const btns = $$('button', fl), det = document.getElementById(fl.dataset.detalle);
    btns.forEach(b => b.addEventListener('click', () => {
      btns.forEach(x => x.setAttribute('aria-pressed', x === b));
      if (det) { det.innerHTML = b.dataset.texto; anunciar(b.querySelector('strong').textContent); }
    }));
  });

  /* ---------- Formularios (validación accesible, envío simulado) ---------- */
  $$('form[data-validar]').forEach(f => {
    f.noValidate = true;
    f.addEventListener('submit', e => {
      e.preventDefault();
      let primero = null;
      $$('input, select, textarea', f).forEach(c => {
        const err = document.getElementById(c.id + '-error');
        let msg = '';
        if (c.required && (c.type === 'checkbox' ? !c.checked : !c.value.trim())) msg = 'Este campo es obligatorio.';
        else if (c.type === 'email' && c.value && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(c.value)) msg = 'Escribe un correo válido.';
        c.setAttribute('aria-invalid', !!msg);
        if (err) { err.textContent = msg; err.hidden = !msg; }
        if (msg && !primero) primero = c;
      });
      if (primero) { primero.focus(); anunciar('Revisa los campos marcados'); return; }
      const ok = $('.aviso-ok', f); ok.hidden = false; ok.focus(); f.reset();
    });
  });

  /* ---------- Gráficas SVG interactivas ---------- */
  const NS = 'http://www.w3.org/2000/svg';
  const el = (t, a = {}) => { const n = document.createElementNS(NS, t); for (const k in a) n.setAttribute(k, a[k]); return n; };
  function tooltip(fig) { let t = $('.tip', fig); if (!t) { t = document.createElement('div'); t.className = 'tip'; t.setAttribute('aria-hidden', 'true'); fig.append(t); } return t; }
  function mostrarTip(fig, nodo, html) {
    const t = tooltip(fig), r = nodo.getBoundingClientRect(), rf = fig.getBoundingClientRect();
    t.innerHTML = html; t.style.left = (r.left + r.width / 2 - rf.left) + 'px'; t.style.top = (r.top - rf.top) + 'px'; t.classList.add('visible');
  }

  // Barras horizontales con varias métricas (chips para cambiar de métrica)
  function barras(fig, datos) {
    const svgHost = $('.lienzo', fig), tabla = $('tbody', fig), chips = $$('[data-metrica]', fig);
    let m = 0;
    const W = 640, fila = 38, izq = 150, H = datos.categorias.length * fila + 10;
    const svg = el('svg', { viewBox: `0 0 ${W} ${H}`, role: 'group', 'aria-label': fig.dataset.titulo || '' });
    svgHost.append(svg);
    const filas = datos.categorias.map((c, i) => {
      const y = i * fila + 6;
      const lab = el('text', { x: izq - 12, y: y + 19, 'text-anchor': 'end' }); lab.textContent = c;
      const fondo = el('rect', { x: izq, y, width: W - izq - 60, height: 26, rx: 13, fill: 'var(--bg-2)' });
      const m0 = datos.metricas[0];
      const bar = el('rect', { x: izq, y, width: 0, height: 26, rx: 13, class: 'barra', tabindex: 0, role: 'img', 'aria-label': `${c}: ${fmt(m0.valores[i])} ${m0.unidad}` });
      const titulo = el('title'); titulo.textContent = `${c}: ${fmt(m0.valores[i])} ${m0.unidad}`; bar.append(titulo);
      const val = el('text', { x: izq + 8, y: y + 18, class: 'valor' });
      svg.append(lab, fondo, bar, val);
      const enfocar = () => {
        const mt = datos.metricas[m];
        mostrarTip(fig, bar, `<strong>${c}</strong><br>${fmt(mt.valores[i])} ${mt.unidad}`);
        fig.dispatchEvent(new CustomEvent('vm:categoria', { detail: c, bubbles: true }));
      };
      bar.addEventListener('mouseenter', enfocar); bar.addEventListener('focus', enfocar);
      bar.addEventListener('mouseleave', () => tooltip(fig).classList.remove('visible'));
      bar.addEventListener('blur', () => tooltip(fig).classList.remove('visible'));
      bar.addEventListener('click', enfocar);
      return { bar, val, c };
    });
    function pintar() {
      const mt = datos.metricas[m], max = Math.max(...mt.valores) || 1;
      filas.forEach((f, i) => {
        const w = (W - izq - 60) * mt.valores[i] / max;
        f.bar.style.transition = doc.dataset.motion === 'reduce' ? 'none' : 'width .9s cubic-bezier(.16,1,.3,1)';
        f.bar.setAttribute('width', Math.max(w, 4));
        f.bar.classList.toggle('b2', m === 1);
        f.bar.setAttribute('aria-label', `${f.c}: ${fmt(mt.valores[i])} ${mt.unidad}`); f.bar.firstChild.textContent = `${f.c}: ${fmt(mt.valores[i])} ${mt.unidad}`;
        f.val.setAttribute('x', izq + Math.max(w, 4) + 8); f.val.textContent = fmt(mt.valores[i]);
      });
      if (tabla) tabla.innerHTML = datos.categorias.map((c, i) => `<tr><th scope="row">${c}</th>${datos.metricas.map(x => `<td>${fmt(x.valores[i])}</td>`).join('')}</tr>`).join('');
      chips.forEach((ch, i) => ch.setAttribute('aria-pressed', i === m));
    }
    chips.forEach((ch, i) => ch.addEventListener('click', () => { m = i; pintar(); anunciar('Mostrando ' + datos.metricas[i].nombre); }));
    fig.__resaltar = nombre => filas.forEach(f => f.bar.classList.toggle('activa', f.c === nombre));
    new IntersectionObserver(([e], o) => { if (e.isIntersecting) { pintar(); o.disconnect(); } }, { threshold: .3 }).observe(fig);
  }

  // Dona con segmentos seleccionables
  function dona(fig, datos) {
    const host = $('.lienzo', fig), total = datos.valores.reduce((a, b) => a + b, 0);
    const R = 110, r = 68, C = 140;
    const svg = el('svg', { viewBox: '0 0 280 280', class: 'dona', role: 'group', 'aria-label': fig.dataset.titulo || '' });
    host.append(svg);
    const centro = el('text', { x: C, y: C - 4, 'text-anchor': 'middle', style: 'font:800 34px var(--f-titulo);fill:var(--tinta)' });
    const sub = el('text', { x: C, y: C + 20, 'text-anchor': 'middle' });
    let a0 = -Math.PI / 2;
    const segs = datos.valores.map((v, i) => {
      const a1 = a0 + v / total * Math.PI * 2, gran = a1 - a0 > Math.PI ? 1 : 0;
      const p = (rad, a) => `${C + rad * Math.cos(a)} ${C + rad * Math.sin(a)}`;
      const d = `M ${p(R, a0)} A ${R} ${R} 0 ${gran} 1 ${p(R, a1)} L ${p(r, a1)} A ${r} ${r} 0 ${gran} 0 ${p(r, a0)} Z`;
      const s = el('path', { d, fill: datos.colores[i], class: 'seg', tabindex: 0, role: 'button', 'aria-label': `${datos.etiquetas[i]}: ${fmt(v)} (${Math.round(v / total * 100)} %)` });
      a0 = a1;
      const elegir = () => {
        segs.forEach((x, j) => x.classList.toggle('activa', i === j));
        centro.textContent = fmt(v); sub.textContent = datos.etiquetas[i];
        fig.dispatchEvent(new CustomEvent('vm:segmento', { detail: i, bubbles: true }));
      };
      s.addEventListener('click', elegir);
      s.addEventListener('keydown', e => { if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); elegir(); } });
      s.addEventListener('mouseenter', () => mostrarTip(fig, s, `<strong>${datos.etiquetas[i]}</strong><br>${fmt(v)} · ${Math.round(v / total * 100)} %`));
      s.addEventListener('mouseleave', () => tooltip(fig).classList.remove('visible'));
      svg.append(s);
      return s;
    });
    svg.append(centro, sub);
    centro.textContent = fmt(total); sub.textContent = datos.centro || 'Total';
    fig.__elegir = i => { segs[i].dispatchEvent(new Event('click')); };
    const tb = $('tbody', fig);
    if (tb) tb.innerHTML = datos.etiquetas.map((e, i) => `<tr><th scope="row">${e}</th><td>${fmt(datos.valores[i])}</td><td>${Math.round(datos.valores[i] / total * 100)} %</td></tr>`).join('');
  }
  $$('.grafica[data-datos]').forEach(fig => {
    const datos = JSON.parse(document.getElementById(fig.dataset.datos).textContent);
    (fig.dataset.tipo === 'dona' ? dona : barras)(fig, datos);
  });

  document.querySelectorAll('[data-anio]').forEach(n => { n.textContent = new Date().getFullYear(); });

  /* ---------- Diagnóstico de las escenas 3D ----------
     Si el módulo 3D no arranca (por ejemplo, al abrir el archivo con doble clic),
     el aviso de cada escena explica qué pasó en lugar de dejar el espacio vacío. */
  setTimeout(() => {
    if (window.VM3D) return;
    const msg = location.protocol === 'file:'
      ? 'El 3D no carga al abrir el archivo directamente. Ábrelo desde un servidor: el enlace de Netlify o «python3 -m http.server» en la carpeta del sitio.'
      : 'No se pudo cargar la escena 3D en este navegador. Actualiza la página (Ctrl + Shift + R) o prueba con Chrome, Edge o Firefox actualizados.';
    $$('.aviso-3d').forEach(a => { a.textContent = msg; a.classList.add('error'); });
  }, 6000);
})();
