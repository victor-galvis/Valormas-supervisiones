/* Valor+ · capa viva de la versión 4: explorador del recaudo y detalles de interacción */
(() => {
  'use strict';
  const doc = document.documentElement;
  const quieto = () => doc.dataset.motion === 'reduce' || doc.dataset.paused === 'true' ||
    window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  const pesos = n => '$' + Math.round(n).toLocaleString('es-CO');
  const compacto = n => n >= 1e9 ? '$' + (n / 1e9).toLocaleString('es-CO', { maximumFractionDigits: 1 }) + ' mil millones'
    : '$' + (n / 1e6).toLocaleString('es-CO', { maximumFractionDigits: 0 }) + ' millones';

  /* ---------- Explorador del recaudo ---------- */
  function recaudo() {
    const fuente = document.getElementById('recaudo-datos');
    const rango = document.getElementById('rec-anio');
    if (!fuente || !rango) return;
    const d = JSON.parse(fuente.textContent);
    const $ = id => document.getElementById(id);
    const salida = $('rec-anio-v'), total = $('rec-total'), vivo = $('rec-vivo');
    const pila = document.querySelectorAll('.rec-pila i');
    const barras = document.querySelectorAll('.rec-anios span');
    const play = document.querySelector('[data-rec-play]');
    let mostrado = 0, anim = 0, temporizador = 0, avisar = 0;

    function contar(destino) {
      cancelAnimationFrame(anim);
      if (quieto()) { mostrado = destino; total.textContent = pesos(destino); return; }
      const desde = mostrado, t0 = performance.now(), dur = 600;
      const paso = t => {
        const k = Math.min(1, (t - t0) / dur), e = 1 - Math.pow(1 - k, 3);
        mostrado = desde + (destino - desde) * e;
        total.textContent = pesos(mostrado);
        if (k < 1) anim = requestAnimationFrame(paso);
      };
      anim = requestAnimationFrame(paso);
    }

    function mostrar(anio, anunciar = true) {
      const i = d.anios.indexOf(+anio);
      if (i < 0) return;
      rango.value = anio;
      salida.textContent = anio;
      const imp = d.impuesto[i], san = d.sancion[i], int = d.intereses[i], tot = d.total[i];
      const suma = imp + san + int || 1;
      contar(tot);
      $('rec-imp').textContent = pesos(imp);
      $('rec-san').textContent = pesos(san);
      $('rec-int').textContent = pesos(int);
      [imp, san, int].forEach((v, k) => { if (pila[k]) pila[k].style.width = (v / suma * 100).toFixed(2) + '%'; });
      barras.forEach(b => b.classList.toggle('activo', +b.dataset.rec === +anio));
      rango.setAttribute('aria-valuetext', `${anio}: ${compacto(tot)}`);
      if (anunciar) {
        clearTimeout(avisar);
        avisar = setTimeout(() => { vivo.textContent = `Año ${anio}: recaudo total ${compacto(tot)}; impuesto ${compacto(imp)}, sanción ${compacto(san)}, intereses ${compacto(int)}.`; }, 450);
      }
    }

    function detener() {
      clearInterval(temporizador); temporizador = 0;
      if (play) { play.classList.remove('activo'); play.setAttribute('aria-label', 'Reproducir la evolución año a año'); play.setAttribute('aria-pressed', 'false'); }
    }
    function reproducir() {
      if (temporizador) return detener();
      let i = 0;
      mostrar(d.anios[0], false);
      play.classList.add('activo');
      play.setAttribute('aria-label', 'Detener la reproducción');
      play.setAttribute('aria-pressed', 'true');
      temporizador = setInterval(() => {
        i++;
        if (i >= d.anios.length) { detener(); mostrar(d.anios[d.anios.length - 1]); return; }
        mostrar(d.anios[i], false);
      }, quieto() ? 1600 : 900);
    }

    rango.addEventListener('input', () => { detener(); mostrar(rango.value); });
    barras.forEach(b => b.addEventListener('click', () => { detener(); mostrar(b.dataset.rec); }));
    if (play) { play.setAttribute('aria-pressed', 'false'); play.addEventListener('click', reproducir); }
    document.addEventListener('vm:pausa', () => { if (doc.dataset.paused === 'true') detener(); });
    mostrar(rango.value, false);
  }

  /* ---------- Brillo que sigue el puntero en tarjetas ---------- */
  function brillo() {
    if (!window.matchMedia('(hover: hover)').matches) return;
    document.addEventListener('pointermove', e => {
      const t = e.target.closest && e.target.closest('.proy-card, .b4, .opo, .red-card, .mv-cards > *');
      if (!t || quieto()) return;
      const r = t.getBoundingClientRect();
      t.style.setProperty('--mx', ((e.clientX - r.left) / r.width * 100).toFixed(1) + '%');
      t.style.setProperty('--my', ((e.clientY - r.top) / r.height * 100).toFixed(1) + '%');
    }, { passive: true });
  }

  /* ---------- Ticker del hero: pausa con la preferencia global ---------- */
  function ticker() {
    const t = document.querySelector('.hero-mapa .ticker');
    if (!t) return;
    const aplicar = () => t.classList.toggle('quieto', quieto());
    ['vm:pausa', 'vm:movimiento'].forEach(ev => document.addEventListener(ev, aplicar));
    aplicar();
  }

  const iniciar = () => { recaudo(); brillo(); ticker(); };
  document.readyState === 'loading' ? document.addEventListener('DOMContentLoaded', iniciar) : iniciar();
})();
