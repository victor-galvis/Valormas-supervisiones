/* ==========================================================================
   Conexión entre escenas 3D e interfaz: buscador de municipios (combobox ARIA),
   ficha del municipio, capas, enlaces con las gráficas y arranque por página.
   ========================================================================== */
import { crearMapa, MUNICIPIOS, DATOS, webglDisponible } from './mapa3d.js';

const $ = (s, c = document) => c.querySelector(s);
const $$ = (s, c = document) => [...c.querySelectorAll(s)];
const fmt = n => Number(n).toLocaleString('es-CO');
const norm = s => s.normalize('NFD').replace(/[̀-ͯ]/g, '').toLowerCase();
const anunciar = t => window.VM?.anunciar(t);

/* ---------- Buscador de municipios accesible ---------- */
function buscador(input, lista, alElegir) {
  let opciones = [], activo = -1;
  const pintar = () => {
    const q = norm(input.value.trim());
    opciones = q ? MUNICIPIOS.filter(m => norm(m.n).includes(q)).slice(0, 8) : [];
    lista.innerHTML = opciones.map((m, i) => `<li role="option" id="${lista.id}-${i}" aria-selected="${i === activo}">${m.n}<small>${m.r}</small></li>`).join('');
    lista.hidden = !opciones.length;
    input.setAttribute('aria-expanded', !!opciones.length);
    input.setAttribute('aria-activedescendant', activo >= 0 ? `${lista.id}-${activo}` : '');
    $$('li', lista).forEach((li, i) => li.addEventListener('mousedown', e => { e.preventDefault(); elegir(i); }));
  };
  const elegir = i => { const m = opciones[i]; if (!m) return; input.value = m.n; lista.hidden = true; input.setAttribute('aria-expanded', 'false'); activo = -1; alElegir(m); };
  input.addEventListener('input', () => { activo = -1; pintar(); });
  input.addEventListener('keydown', e => {
    if (e.key === 'ArrowDown') { e.preventDefault(); activo = Math.min(opciones.length - 1, activo + 1); pintar(); }
    else if (e.key === 'ArrowUp') { e.preventDefault(); activo = Math.max(0, activo - 1); pintar(); }
    else if (e.key === 'Enter') { e.preventDefault(); elegir(activo >= 0 ? activo : 0); }
    else if (e.key === 'Escape') { lista.hidden = true; input.setAttribute('aria-expanded', 'false'); }
  });
  input.addEventListener('blur', () => setTimeout(() => { lista.hidden = true; input.setAttribute('aria-expanded', 'false'); }, 120));
}

function pintarFicha(ficha, { m, con, seg }, modo = 'todos') {
  const filas = [];
  if (modo !== 'seguridad') filas.push(`<div><dt>Sedes educativas conectadas</dt><dd>${fmt(con ? con.s : 0)}</dd></div>`);
  if (modo === 'conectividad') filas.push(`<div><dt>Por satélite / radioenlace</dt><dd>${con ? `${con.sat} / ${con.rad}` : '0 / 0'}</dd></div>`);
  if (modo !== 'conectividad') filas.push(`<div><dt>Cámaras integradas al nodo</dt><dd>${fmt(seg)}</dd></div>`);
  ficha.innerHTML = `<h3>${m.n}</h3><p class="sub">Subregión ${m.r} · ${fmt(m.a)} km²</p><dl>${filas.join('')}</dl>`;
  ficha.hidden = false;
  anunciar(`${m.n}: ${ficha.querySelector('dl').textContent.replace(/\s+/g, ' ')}`);
}

window.VM3D = 'iniciado';
// Aviso visible dentro de cada escena: desaparece al cargar o explica el problema
function aviso(host, texto) {
  const a = host && host.querySelector('.aviso-3d');
  if (!a) return;
  if (texto) { a.textContent = texto; a.classList.add('error'); } else a.hidden = true;
}
function protegido(host, fn) {
  try { const r = fn(); aviso(host); return r; }
  catch (e) { console.error(e); aviso(host, 'No se pudo cargar la escena 3D (' + e.message + '). La información está disponible en las gráficas y tablas de esta página.'); return null; }
}
function montarMapa(escenaHost, panel, modo) {
  if (!webglDisponible()) {
    aviso(escenaHost, 'Tu navegador no tiene WebGL activo, por eso no se muestra el mapa 3D. La información está en las gráficas y tablas de esta página.');
    return null;
  }
  const mapa = protegido(escenaHost, () => crearMapa(escenaHost, { capa: modo === 'inicio' ? 'todos' : modo, arcosEnTodos: false, distancia: modo === 'inicio' ? 56 : 70 }));
  if (!mapa) return null;
  const ficha = panel && $('.ficha-mpio', panel);
  let capaVista = modo === 'inicio' ? 'todos' : modo;
  escenaHost.addEventListener('vm:municipio', e => { if (ficha) pintarFicha(ficha, e.detail, capaVista); });
  if (panel) {
    $$('[data-capa]', panel).forEach(ch => ch.addEventListener('click', () => {
      capaVista = ch.dataset.capa; mapa.capa(capaVista);
      $$('[data-capa]', panel).forEach(x => x.setAttribute('aria-pressed', x === ch));
      anunciar('Mapa: ' + ch.textContent.trim());
    }));
    const inp = $('input[role="combobox"]', panel);
    if (inp) buscador(inp, document.getElementById(inp.getAttribute('aria-controls')), m => mapa.seleccionar(m.c, true));
  }
  const ctl = escenaHost.parentElement.querySelector('.control-3d') || escenaHost.querySelector('.control-3d');
  if (ctl) {
    $('[data-zoom="mas"]', ctl)?.addEventListener('click', () => mapa.acercar(.8));
    $('[data-zoom="menos"]', ctl)?.addEventListener('click', () => mapa.acercar(1.25));
    $('[data-zoom="centro"]', ctl)?.addEventListener('click', () => mapa.enfocar(null));
  }
  return mapa;
}

/* ---------- Arranque según la página ---------- */
const pagina = document.body.dataset.pagina;
const heroMapa = $('#mapa-hero');
if (heroMapa) montarMapa(heroMapa, $('#panel-mapa'), pagina === 'inicio' ? 'inicio' : pagina);

const mapaSec = $('#mapa-seccion');
if (mapaSec) montarMapa(mapaSec, $('#panel-seccion'), mapaSec.dataset.capa);

if (pagina === 'conectividad' && webglDisponible()) {
  const { crearEscenaAntena } = await import('./antena3d.js');
  protegido($('#escena-antena'), () => crearEscenaAntena($('#escena-antena'), $$('#relato-antena .paso')));
}

if (pagina === 'seguridad' && webglDisponible()) {
  // relato: mapa de la red con focos por paso
  const host = $('#escena-red');
  const red = protegido(host, () => crearMapa(host, { capa: 'seguridad', autoRotar: true, distancia: 64 }));
  const focos = [null, DATOS.seguridad.nodos[0].c, DATOS.seguridad.nodos[1].c, null];
  const io = new IntersectionObserver(es => es.forEach(e => {
    if (!e.isIntersecting) return;
    const i = +e.target.dataset.paso;
    $$('#relato-red .paso').forEach((p, j) => p.classList.toggle('activo', i === j));
    if (!red) return;
    red.enfocar(focos[i], i === 1 ? 26 : 34);
    if (focos[i]) red.seleccionar(focos[i]);
  }), { rootMargin: '-45% 0px -45% 0px' });
  $$('#relato-red .paso').forEach(p => io.observe(p));
  // visor de cámaras sincronizado con pestañas y dona
  const { crearVisor } = await import('./camaras3d.js');
  const visor = protegido($('#visor-camaras'), () => crearVisor($('#visor-camaras')));
  const lista = $('#tabs-camaras'), dona = $('#grafica-camaras');
  lista?.addEventListener('vm:tab', e => { visor?.mostrar(e.detail); });
  dona?.addEventListener('vm:segmento', e => { lista.__elegir?.(e.detail); });
}

// pasos activos del relato de conectividad (realce del texto)
$$('.relato .paso').forEach(p => new IntersectionObserver(([e]) => {
  if (e.isIntersecting) $$('.paso', p.parentElement).forEach(x => x.classList.toggle('activo', x === p));
}, { rootMargin: '-45% 0px -45% 0px' }).observe(p));
