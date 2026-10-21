/* ==========================================================================
   Valor+ · Escenas 3D corporativas con Three.js
   Línea gráfica de valormas.gov.co: verdes institucionales, lima del "+", azul
   marino y blanco. Objetos sólidos y mates con luz suave (sin brillos neón).
   - Hero de inicio: "+" de la marca en 3D con medallones de los servicios
   - Servicios: objeto 3D por servicio sobre un pedestal (estilo render de producto)
   - Cifras y pie de página: malla de puntos ondulante, sutil
   - Clientes: carrusel 3D en anillo
   - Encabezados internos: signos "+" flotantes
   Respeta "reducir movimiento" y el botón de pausa (data-paused en <html>).
   Sin WebGL (o abierto como archivo local) el sitio usa las animaciones CSS/2D.
   ========================================================================== */
import * as THREE from './vendor/three.module.min.js';

const doc = document.documentElement;
const reduced = () => doc.dataset.motion === 'reduce';
const paused = () => doc.dataset.paused === 'true';
const still = () => reduced() || paused();
const LITE = matchMedia('(pointer: coarse)').matches || (navigator.hardwareConcurrency || 8) <= 4;
const DPR = Math.min(devicePixelRatio || 1, LITE ? 1.5 : 2);
const clamp = (v, a, b) => Math.min(b, Math.max(a, v));
const lerp = (a, b, k) => a + (b - a) * k;
const easeInOut = k => k < .5 ? 4 * k * k * k : 1 - Math.pow(-2 * k + 2, 3) / 2;
const easeOutBack = k => 1 + 2.2 * Math.pow(k - 1, 3) + 1.2 * Math.pow(k - 1, 2);

// Paleta institucional (sitio actual de Valor+)
const P = {
  verde: 0x009549, verdeOscuro: 0x065325, verdeMedio: 0x0e7a3a, verdeClaro: 0x7cc79a,
  lima: 0xb5cc2e, marino: 0x0c264c, azul: 0x1f6fc4, blanco: 0xffffff, hueso: 0xf4f7f5,
};

function webglOK() {
  try { const c = document.createElement('canvas'); return !!(c.getContext('webgl2') || c.getContext('webgl')); }
  catch { return false; }
}

/* ---------- Puntero compartido ---------- */
const pointer = { x: 0, y: 0, tx: 0, ty: 0 };
addEventListener('pointermove', e => { pointer.tx = e.clientX / innerWidth * 2 - 1; pointer.ty = -(e.clientY / innerHeight * 2 - 1); }, { passive: true });

/* ---------- Escenario base y bucle único ---------- */
const STAGES = new Set();
const io = new IntersectionObserver(entries => entries.forEach(e => {
  const st = e.target.__stage; if (!st) return;
  st.visible = e.isIntersecting; st.dirty = true;
}), { rootMargin: '120px 0px' });

class Stage {
  constructor(host, { fov = 40, z = 10, cls = '' } = {}) {
    this.host = host;
    this.canvas = document.createElement('canvas');
    this.canvas.className = 'gl ' + cls;
    this.canvas.setAttribute('aria-hidden', 'true');
    host.prepend(this.canvas);
    const r = this.renderer = new THREE.WebGLRenderer({ canvas: this.canvas, antialias: true, alpha: true, powerPreference: 'high-performance' });
    r.setPixelRatio(DPR);
    r.setClearColor(0x000000, 0);
    r.toneMapping = THREE.ACESFilmicToneMapping;
    r.toneMappingExposure = 1;
    this.scene = new THREE.Scene();
    this.camera = new THREE.PerspectiveCamera(fov, 1, .1, 200);
    this.camera.position.z = z;
    this.t = 0; this.visible = false; this.dirty = true;
    host.__stage = this;
    new ResizeObserver(() => this.resize()).observe(host);
    this.resize();
    io.observe(host);
    STAGES.add(this);
  }
  resize() {
    const w = this.canvas.clientWidth || this.host.clientWidth, h = this.canvas.clientHeight || this.host.clientHeight;
    if (!w || !h) return;
    this.w = w; this.h = h;
    this.renderer.setSize(w, h, false);
    this.camera.aspect = w / h; this.camera.updateProjectionMatrix();
    this.onResize?.(w, h);
    this.dirty = true;
  }
  progress() {
    if (reduced()) return 0;
    const r = this.host.getBoundingClientRect();
    return clamp((innerHeight - r.top) / (innerHeight + r.height), 0, 1);
  }
  render() { this.renderer.render(this.scene, this.camera); }
}

let last = performance.now();
function frame(now) {
  const dt = Math.min((now - last) / 1000, .05); last = now;
  const k = reduced() ? 0 : 1;
  pointer.x = lerp(pointer.x, pointer.tx * k, .05); pointer.y = lerp(pointer.y, pointer.ty * k, .05);
  const s = still();
  for (const st of STAGES) {
    if (!st.visible || document.hidden || doc.dataset.overlay) continue;
    if (s && !st.dirty && !st.busy) continue;
    if (!s) st.t += dt;
    st.update?.(st.t, s ? 0 : dt);
    st.render();
    st.dirty = false;
  }
  requestAnimationFrame(frame);
}
addEventListener('scroll', () => { for (const st of STAGES) if (st.visible) st.dirty = true; }, { passive: true });
document.addEventListener('vm:pausa', () => STAGES.forEach(st => st.dirty = true));
new MutationObserver(() => STAGES.forEach(st => { st.onTheme?.(); st.dirty = true; })).observe(doc, { attributes: true, attributeFilter: ['data-theme', 'data-contrast'] });

/* ---------- Iluminación de estudio (suave, sin brillos) ---------- */
function studioLights(scene, { rim = P.verde, intensity = 1 } = {}) {
  scene.add(new THREE.HemisphereLight(0xffffff, 0x1d4a33, 1.3 * intensity));
  const key = new THREE.DirectionalLight(0xffffff, 2.2 * intensity); key.position.set(4, 7, 8);
  const fill = new THREE.DirectionalLight(0xdfeee6, .8 * intensity); fill.position.set(-6, 2, 5);
  const back = new THREE.DirectionalLight(rim, 1.4 * intensity); back.position.set(-3, 4, -7);
  scene.add(key, fill, back);
}
const mat = (color, o = {}) => new THREE.MeshStandardMaterial({ color, roughness: .45, metalness: .08, ...o });

/* ---------- Geometrías de marca ---------- */
function roundedPolyShape(pts, r) {
  const s = new THREE.Shape(), n = pts.length;
  for (let i = 0; i < n; i++) {
    const p = pts[i], a = pts[(i - 1 + n) % n], b = pts[(i + 1) % n];
    const p1 = p.clone().add(a.clone().sub(p).normalize().multiplyScalar(r));
    const p2 = p.clone().add(b.clone().sub(p).normalize().multiplyScalar(r));
    i === 0 ? s.moveTo(p1.x, p1.y) : s.lineTo(p1.x, p1.y);
    s.quadraticCurveTo(p.x, p.y, p2.x, p2.y);
  }
  s.closePath();
  return s;
}
let plusGeo;
function plusGeometry() {
  if (plusGeo) return plusGeo;
  const L = 1.2, w = .38, V = (x, y) => new THREE.Vector2(x, y);
  const pts = [V(w, L), V(-w, L), V(-w, w), V(-L, w), V(-L, -w), V(-w, -w), V(-w, -L), V(w, -L), V(w, -w), V(L, -w), V(L, w), V(w, w)];
  plusGeo = new THREE.ExtrudeGeometry(roundedPolyShape(pts, .14), { depth: .42, bevelEnabled: true, bevelThickness: .1, bevelSize: .08, bevelSegments: 6, curveSegments: 10 });
  plusGeo.center();
  return plusGeo;
}
function shadowBlob(size = 5, opacity = .28) {
  const c = document.createElement('canvas'); c.width = c.height = 128;
  const g = c.getContext('2d'), gr = g.createRadialGradient(64, 64, 0, 64, 64, 64);
  gr.addColorStop(0, `rgba(6,40,22,${opacity})`); gr.addColorStop(1, 'rgba(6,40,22,0)');
  g.fillStyle = gr; g.fillRect(0, 0, 128, 128);
  const m = new THREE.Mesh(new THREE.PlaneGeometry(size, size), new THREE.MeshBasicMaterial({ map: new THREE.CanvasTexture(c), transparent: true, depthWrite: false }));
  m.rotation.x = -Math.PI / 2;
  return m;
}
function loadImage(src) {
  return new Promise(res => { const i = new Image(); i.onload = () => res(i); i.onerror = () => res(null); i.src = src; });
}
async function medallionTexture(src) {
  const img = await loadImage(src); if (!img) return null;
  const S = 256, c = document.createElement('canvas'); c.width = c.height = S;
  const g = c.getContext('2d'), m = Math.min(img.width, img.height);
  g.fillStyle = '#ffffff'; g.fillRect(0, 0, S, S);
  g.save(); g.beginPath(); g.arc(S / 2, S / 2, S / 2 - 14, 0, Math.PI * 2); g.clip();
  g.drawImage(img, (img.width - m) / 2, (img.height - m) / 2, m, m, 14, 14, S - 28, S - 28); g.restore();
  const t = new THREE.CanvasTexture(c); t.colorSpace = THREE.SRGBColorSpace; t.anisotropy = 4;
  return t;
}

/* ==========================================================================
   1. Hero de inicio: "+" de la marca y medallones de servicios
   ========================================================================== */
function heroScene(orb) {
  if (getComputedStyle(orb).display === 'none') return; // en móvil el hero no muestra la composición
  const st = new Stage(orb, { fov: 30, z: 15.5 });
  orb.classList.add('has-3d');
  const S = st.scene;
  studioLights(S, { rim: P.verde });

  const core = new THREE.Group(); S.add(core);
  const plus = new THREE.Mesh(plusGeometry(), mat(P.lima, { roughness: .32, metalness: .12 }));
  core.add(plus);

  // anillos institucionales: verde sólido y blanco fino
  const ring1 = new THREE.Mesh(new THREE.TorusGeometry(2.25, .065, 24, 160), mat(P.verde, { roughness: .3, metalness: .35 }));
  const ring2 = new THREE.Mesh(new THREE.TorusGeometry(2.62, .018, 12, 200), mat(P.blanco, { roughness: .4 }));
  ring2.material.transparent = true; ring2.material.opacity = .55;
  core.add(ring1, ring2);

  // medallones con las imágenes de los servicios
  const orbit = new THREE.Group(); orbit.rotation.x = -.42; core.add(orbit);
  const medals = [];
  const srcs = [...orb.querySelectorAll('img')].map(i => i.getAttribute('src'));
  srcs.forEach((src, i) => medallionTexture(src).then(tex => {
    if (!tex) return;
    const side = mat(P.blanco, { roughness: .35 }), face = new THREE.MeshStandardMaterial({ map: tex, roughness: .55 });
    const geo = new THREE.CylinderGeometry(.56, .56, .1, 48); geo.rotateX(Math.PI / 2); // la cara queda en +Z
    const m = new THREE.Mesh(geo, [side, face, face]);
    m.userData.a = i / srcs.length * Math.PI * 2;
    orbit.add(m); medals.push(m); st.dirty = true;
  }));

  // polvo de datos discreto
  const n = 260, pos = new Float32Array(n * 3);
  for (let i = 0; i < n; i++) { const v = new THREE.Vector3().randomDirection().multiplyScalar(3.2 + Math.random() * 2.2); pos.set([v.x, v.y, v.z], i * 3); }
  const dust = new THREE.Points(new THREE.BufferGeometry().setAttribute('position', new THREE.BufferAttribute(pos, 3)),
    new THREE.PointsMaterial({ color: 0xcfe8da, size: .035, transparent: true, opacity: .55, depthWrite: false }));
  core.add(dust);

  const camWorld = new THREE.Vector3();
  st.update = (t) => {
    const p = st.progress();
    plus.rotation.y = t * .45 + p * Math.PI;
    plus.rotation.x = Math.sin(t * .5) * .18;
    ring1.rotation.set(Math.PI / 2 + Math.sin(t * .4) * .25, t * .2, 0);
    ring2.rotation.set(Math.PI / 2.4, -t * .15, Math.sin(t * .3) * .2);
    medals.forEach(m => {
      const a = m.userData.a + t * .22;
      m.position.set(Math.cos(a) * 3, 0, Math.sin(a) * 3);
      m.lookAt(camWorld.copy(st.camera.position)); // cada medallón mira a la cámara
    });
    dust.rotation.y = t * .04;
    core.rotation.y = pointer.x * .3;
    core.rotation.x = -pointer.y * .18;
    core.position.y = Math.sin(t * .8) * .08;
  };
}

/* ==========================================================================
   2. Servicios: un objeto 3D por servicio sobre un pedestal
   ========================================================================== */
function coinsModel() {
  const g = new THREE.Group(), geo = new THREE.CylinderGeometry(.55, .55, .14, 48);
  const side = mat(P.verdeMedio, { metalness: .4, roughness: .3 }), top = mat(0x14a85c, { metalness: .3, roughness: .35 });
  [[-1.05, .35, 5], [.15, -.45, 8], [1.15, .35, 3]].forEach(([x, z, n]) => {
    for (let i = 0; i < n; i++) {
      const c = new THREE.Mesh(geo, [side, top, top]);
      c.position.set(x + (Math.random() - .5) * .06, .07 + i * .15, z + (Math.random() - .5) * .06);
      c.rotation.y = Math.random();
      g.add(c);
    }
  });
  const lid = new THREE.Mesh(new THREE.TorusGeometry(.42, .04, 12, 48), mat(P.lima));
  lid.rotation.x = Math.PI / 2; lid.position.set(.15, .07 + 8 * .15, -.45); g.add(lid);
  return g;
}
function globeModel() {
  const g = new THREE.Group();
  const s = new THREE.Mesh(new THREE.SphereGeometry(1.35, 64, 48), mat(P.blanco, { roughness: .6 }));
  s.position.y = 1.75; g.add(s);
  const line = mat(P.verde, { roughness: .4 });
  for (let i = -2; i <= 2; i++) {
    const lat = i * .5, r = Math.cos(lat) * 1.37;
    const t = new THREE.Mesh(new THREE.TorusGeometry(r, .018, 8, 96), line);
    t.rotation.x = Math.PI / 2; t.position.y = 1.75 + Math.sin(lat) * 1.37; g.add(t);
  }
  for (let i = 0; i < 6; i++) {
    const t = new THREE.Mesh(new THREE.TorusGeometry(1.37, .018, 8, 96), line);
    t.rotation.y = i / 6 * Math.PI; t.position.y = 1.75; g.add(t);
  }
  const sats = new THREE.Group(); sats.position.y = 1.75; g.add(sats);
  [P.marino, P.lima, P.verde].forEach((c, i) => {
    const b = new THREE.Mesh(new THREE.BoxGeometry(.2, .2, .2), mat(c));
    b.userData.a = i * 2.1; sats.add(b);
  });
  g.userData.tick = t => sats.children.forEach(b => { const a = b.userData.a + t * .8; b.position.set(Math.cos(a) * 1.85, Math.sin(a * 1.3) * .4, Math.sin(a) * 1.85); b.rotation.set(t, t * .7, 0); });
  return g;
}
function barsModel() {
  const g = new THREE.Group(), cols = [0xa8dcbc, 0x2fb873, P.verde, P.verdeOscuro], hs = [1, 1.6, 2.3, 3.1];
  hs.forEach((h, i) => {
    const b = new THREE.Mesh(new THREE.BoxGeometry(.62, h, .62), mat(cols[i], { roughness: .4 }));
    b.position.set(-1.2 + i * .8, h / 2, 0); b.userData.h = h; g.add(b);
  });
  const dot = new THREE.Mesh(new THREE.SphereGeometry(.17, 32, 16), mat(P.lima));
  dot.position.set(1.2, 3.42, 0); g.add(dot);
  g.userData.tick = t => { g.children.forEach((b, i) => { if (b.userData.h) { const k = 1 + Math.sin(t * 1.4 + i) * .04; b.scale.y = k; b.position.y = b.userData.h * k / 2; } }); dot.position.y = 3.1 * (1 + Math.sin(t * 1.4 + 3) * .04) + .32; };
  return g;
}
function serversModel() {
  const g = new THREE.Group(), leds = [];
  for (let i = 0; i < 4; i++) {
    const u = new THREE.Mesh(new THREE.BoxGeometry(2.5, .48, 1.5), mat(0x1b3c68, { roughness: .4, metalness: .2 }));
    u.position.y = .3 + i * .56; g.add(u);
    const slot = new THREE.Mesh(new THREE.BoxGeometry(1.4, .08, .02), mat(0x23406b));
    slot.position.set(-.35, u.position.y, .76); g.add(slot);
    for (let k = 0; k < 3; k++) {
      const led = new THREE.Mesh(new THREE.SphereGeometry(.045, 12, 8), new THREE.MeshStandardMaterial({ color: k === 0 ? P.lima : 0x3fd68a, emissive: k === 0 ? P.lima : 0x3fd68a, emissiveIntensity: .6 }));
      led.position.set(.75 + k * .17, u.position.y, .77); g.add(led); leds.push(led);
    }
  }
  g.userData.tick = t => leds.forEach((l, i) => { l.material.emissiveIntensity = .25 + .5 * (Math.sin(t * 3 + i * 1.7) > .3 ? 1 : 0); });
  return g;
}
function lockModel() {
  const g = new THREE.Group();
  const body = new THREE.Mesh(new THREE.BoxGeometry(2, 1.55, .8), mat(P.verde, { roughness: .35 }));
  body.position.y = .95; g.add(body);
  const shackle = new THREE.Mesh(new THREE.TorusGeometry(.6, .13, 20, 48, Math.PI), mat(0xe9eef2, { metalness: .85, roughness: .22 }));
  shackle.position.y = 1.72; g.add(shackle);
  [-.6, .6].forEach(x => { const leg = new THREE.Mesh(new THREE.CylinderGeometry(.13, .13, .25, 20), shackle.material); leg.position.set(x, 1.72, 0); g.add(leg); });
  const hole = new THREE.Mesh(new THREE.CylinderGeometry(.14, .14, .05, 24), mat(P.marino));
  hole.rotation.x = Math.PI / 2; hole.position.set(0, 1.05, .41); g.add(hole);
  const slot = new THREE.Mesh(new THREE.BoxGeometry(.1, .32, .05), mat(P.marino));
  slot.position.set(0, .86, .41); g.add(slot);
  g.userData.tick = t => { shackle.position.y = 1.72 + Math.max(0, Math.sin(t * .9)) * .12; };
  return g;
}
function solarModel() {
  const g = new THREE.Group();
  const c = document.createElement('canvas'); c.width = 256; c.height = 160;
  const x = c.getContext('2d'); x.fillStyle = '#123a6b'; x.fillRect(0, 0, 256, 160);
  x.strokeStyle = 'rgba(255,255,255,.55)'; x.lineWidth = 3;
  for (let i = 1; i < 6; i++) { x.beginPath(); x.moveTo(i * 256 / 6, 0); x.lineTo(i * 256 / 6, 160); x.stroke(); }
  for (let i = 1; i < 4; i++) { x.beginPath(); x.moveTo(0, i * 40); x.lineTo(256, i * 40); x.stroke(); }
  const tex = new THREE.CanvasTexture(c); tex.colorSpace = THREE.SRGBColorSpace;
  const frameM = mat(0xdfe6ea, { metalness: .6, roughness: .3 });
  const panel = new THREE.Mesh(new THREE.BoxGeometry(2.6, .07, 1.65), [frameM, frameM, new THREE.MeshStandardMaterial({ map: tex, roughness: .25, metalness: .3 }), frameM, frameM, frameM]);
  panel.position.set(-.2, 1.25, 0); panel.rotation.x = .75; g.add(panel);
  [[-1.2, .6], [.8, .6]].forEach(([px, h]) => { const leg = new THREE.Mesh(new THREE.CylinderGeometry(.04, .04, h * 1.6, 12), frameM); leg.position.set(px, h * .8, -.45); g.add(leg); });
  const sun = new THREE.Mesh(new THREE.SphereGeometry(.42, 48, 32), new THREE.MeshStandardMaterial({ color: 0xd9e35a, emissive: 0xb5cc2e, emissiveIntensity: .35, roughness: .5 }));
  sun.position.set(1.35, 2.75, -.6); g.add(sun);
  const halo = new THREE.Mesh(new THREE.TorusGeometry(.62, .02, 8, 64), mat(P.lima)); halo.position.copy(sun.position); g.add(halo);
  g.userData.tick = t => { halo.rotation.y = t * .8; halo.rotation.x = Math.sin(t * .5) * .5; };
  return g;
}
function servicesScene(vis) {
  const steps = [...vis.closest('.scrolly').querySelectorAll('.scrolly-step')];
  if (!steps.length || getComputedStyle(vis).display === 'none') return;
  const st = new Stage(vis, { fov: 34, z: 11 });
  vis.classList.add('has-3d');
  const S = st.scene;
  studioLights(S, { rim: P.verdeClaro });
  st.camera.position.set(0, 3.2, 10.5);
  const stage = new THREE.Group(); S.add(stage);
  const pedestal = new THREE.Mesh(new THREE.CylinderGeometry(2.5, 2.62, .22, 96), mat(P.blanco, { roughness: .8 }));
  pedestal.position.y = -.11; stage.add(pedestal);
  const trim = new THREE.Mesh(new THREE.TorusGeometry(2.56, .025, 8, 160), mat(P.verde));
  trim.rotation.x = Math.PI / 2; trim.position.y = -.01; stage.add(trim);
  const shadow = shadowBlob(7, .22); shadow.position.y = -.23; stage.add(shadow);
  const models = [coinsModel(), globeModel(), barsModel(), serversModel(), lockModel(), solarModel()];
  models.forEach((m, i) => { m.scale.setScalar(i === 0 ? 1 : 0); m.visible = i === 0; stage.add(m); });
  let cur = 0, prev = 0, k = 1;
  const go = i => {
    if (i === cur || i < 0) return;
    prev = cur; cur = i; k = still() ? 1 : 0;
    models.forEach((m, j) => { m.visible = j === cur || (k < 1 && j === prev); if (j !== cur && j !== prev) m.scale.setScalar(0); });
    if (k === 1) { models[prev].visible = false; models[cur].scale.setScalar(1); }
    st.busy = true; st.dirty = true;
  };
  const obs = new IntersectionObserver(es => es.forEach(e => { if (e.isIntersecting) go(steps.indexOf(e.target)); }), { rootMargin: '-45% 0px -45% 0px' });
  steps.forEach(s => obs.observe(s));
  st.update = (t, dt) => {
    if (k < 1) {
      k = Math.min(1, k + (dt || 1) / .9);
      const out = clamp(k * 1.8, 0, 1), inn = clamp((k - .3) / .7, 0, 1);
      models[prev].scale.setScalar(1 - easeInOut(out));
      models[prev].rotation.y += .08;
      models[cur].scale.setScalar(Math.max(0, easeOutBack(inn)));
      models[cur].rotation.y = (1 - inn) * -Math.PI / 2;
      if (k === 1) { models[prev].visible = false; st.busy = false; }
    }
    models[cur].userData.tick?.(t);
    stage.rotation.y = Math.sin(t * .45) * .5 + pointer.x * .35; // balanceo: el frente siempre visible
    st.camera.position.y = 3.2 + pointer.y * .4;
    st.camera.lookAt(0, 1.2, 0);
  };
}

/* ==========================================================================
   3. Malla de puntos ondulante (cifras y pie de página)
   ========================================================================== */
const waveVert = `
uniform float uTime; uniform vec2 uMouse; uniform float uSize; uniform float uAmp; uniform vec3 uC1; uniform vec3 uC2;
varying vec3 vColor; varying float vAlpha;
void main(){
  vec3 p = position;
  float d = distance(p.xz, uMouse);
  float h = sin(p.x * .3 + uTime * .7) * .45 + cos(p.z * .4 + uTime * .9) * .35;
  h += exp(-d * .35) * .9 * sin(uTime * 2.4 - d);
  p.y += h * uAmp;
  vColor = mix(uC1, uC2, smoothstep(-.8, .9, h));
  vec4 mv = modelViewMatrix * vec4(p, 1.);
  gl_PointSize = uSize * (12. / -mv.z);
  vAlpha = smoothstep(55., 12., -mv.z);
  gl_Position = projectionMatrix * mv;
}`;
const waveFrag = `
uniform float uOpacity; varying vec3 vColor; varying float vAlpha;
void main(){
  float r = length(gl_PointCoord - .5);
  if (r > .5) discard;
  gl_FragColor = vec4(vColor, smoothstep(.5, .3, r) * vAlpha * uOpacity);
}`;
function waveScene(host, { cols = 140, rows = 50, gap = .5, opacity = .6, amp = 1, c1 = P.verdeOscuro, c2 = P.lima, cam = [0, 5, 15], cls = '' } = {}) {
  const st = new Stage(host, { fov: 50, z: cam[2], cls });
  host.classList.add('has-gl');
  if (LITE) { cols = Math.round(cols * .6); rows = Math.round(rows * .6); gap *= 1.6; }
  const pos = new Float32Array(cols * rows * 3);
  let i = 0;
  for (let x = 0; x < cols; x++) for (let z = 0; z < rows; z++) pos.set([(x - cols / 2) * gap, 0, (z - rows / 2) * gap], 3 * i++);
  const u = {
    uTime: { value: 0 }, uMouse: { value: new THREE.Vector2(999, 999) }, uSize: { value: 3.2 * DPR }, uAmp: { value: amp }, uOpacity: { value: opacity },
    uC1: { value: new THREE.Color(c1) }, uC2: { value: new THREE.Color(c2) },
  };
  const pts = new THREE.Points(new THREE.BufferGeometry().setAttribute('position', new THREE.BufferAttribute(pos, 3)),
    new THREE.ShaderMaterial({ uniforms: u, vertexShader: waveVert, fragmentShader: waveFrag, transparent: true, depthWrite: false }));
  st.scene.add(pts);
  st.camera.position.set(...cam);
  const ray = new THREE.Raycaster(), plane = new THREE.Plane(new THREE.Vector3(0, 1, 0), 0), hit = new THREE.Vector3(), ndc = new THREE.Vector2();
  host.addEventListener('pointermove', e => {
    const r = st.canvas.getBoundingClientRect();
    ndc.set((e.clientX - r.left) / r.width * 2 - 1, -((e.clientY - r.top) / r.height * 2 - 1));
    ray.setFromCamera(ndc, st.camera);
    if (ray.ray.intersectPlane(plane, hit)) u.uMouse.value.set(hit.x, hit.z);
  }, { passive: true });
  host.addEventListener('pointerleave', () => u.uMouse.value.set(999, 999));
  st.update = (t) => {
    u.uTime.value = t;
    st.camera.position.x = pointer.x * 1.2;
    st.camera.position.y = cam[1] + pointer.y * .4;
    st.camera.lookAt(0, -1, 0);
  };
}

/* ==========================================================================
   4. Clientes: carrusel 3D en anillo
   ========================================================================== */
function cardTexture(img) {
  return new Promise(res => {
    const go = () => {
      const W = 512, H = 320, c = document.createElement('canvas'); c.width = W; c.height = H;
      const g = c.getContext('2d'), r = 32;
      g.fillStyle = '#ffffff';
      g.beginPath(); g.moveTo(r, 0); g.arcTo(W, 0, W, H, r); g.arcTo(W, H, 0, H, r); g.arcTo(0, H, 0, 0, r); g.arcTo(0, 0, W, 0, r); g.closePath(); g.fill();
      g.strokeStyle = '#dde4ee'; g.lineWidth = 4; g.stroke();
      const pad = 46, sc = Math.min((W - pad * 2) / img.naturalWidth, (H - pad * 2) / img.naturalHeight);
      g.drawImage(img, (W - img.naturalWidth * sc) / 2, (H - img.naturalHeight * sc) / 2, img.naturalWidth * sc, img.naturalHeight * sc);
      const t = new THREE.CanvasTexture(c); t.colorSpace = THREE.SRGBColorSpace; t.anisotropy = 4; res(t);
    };
    img.complete && img.naturalWidth ? go() : (img.loading = 'eager', img.addEventListener('load', go, { once: true }), img.addEventListener('error', () => res(null), { once: true }));
  });
}
function ringScene(wrap) {
  const mq = wrap.querySelector('.marquee');
  const imgs = [...wrap.querySelectorAll('.marquee-track li:not([aria-hidden]) img')];
  if (!imgs.length) return;
  const host = document.createElement('div'); host.className = 'ring-3d'; host.setAttribute('aria-hidden', 'true');
  mq.before(host);
  const st = new Stage(host, { fov: 34, z: 20 });
  wrap.classList.add('has-3d');
  const n = imgs.length, R = n * 3.3 / (Math.PI * 2);
  const ring = new THREE.Group(); st.scene.add(ring);
  const bg = () => new THREE.Color(getComputedStyle(wrap.closest('section') || document.body).backgroundColor);
  st.scene.fog = new THREE.Fog(bg(), R + 6, R * 2 + 10);
  st.onTheme = () => { st.scene.fog.color = bg(); };
  imgs.forEach((img, i) => cardTexture(img).then(tex => {
    if (!tex) return;
    const m = new THREE.Mesh(new THREE.PlaneGeometry(3, 1.88), new THREE.MeshBasicMaterial({ map: tex, transparent: true, side: THREE.DoubleSide }));
    const a = i / n * Math.PI * 2;
    m.position.set(Math.sin(a) * R, 0, Math.cos(a) * R); m.rotation.y = a;
    ring.add(m); st.dirty = true;
  }));
  let vel = 0, drag = false, lx = 0;
  host.addEventListener('pointerdown', e => { drag = true; lx = e.clientX; host.setPointerCapture?.(e.pointerId); });
  host.addEventListener('pointermove', e => { if (!drag) return; vel = (e.clientX - lx) * .004; ring.rotation.y += vel; lx = e.clientX; st.dirty = true; });
  host.addEventListener('pointerup', () => { drag = false; });
  st.camera.position.set(0, 1.8, R + 6.5);
  st.update = (t, dt) => {
    if (!drag) { vel *= .94; ring.rotation.y += vel + (mq.classList.contains('is-paused') ? 0 : dt * .16); }
    st.camera.position.x = pointer.x * 1.5;
    st.camera.lookAt(0, 0, 0);
  };
}

/* ==========================================================================
   5. Encabezados internos: signos "+" flotantes de la marca
   ========================================================================== */
function heroPlusScene(ph) {
  const st = new Stage(ph, { fov: 40, z: 16, cls: 'gl-hero' });
  ph.classList.add('has-3d');
  const S = st.scene;
  studioLights(S, { rim: P.verde, intensity: .9 });
  const specs = [[P.lima, .62], [P.verde, .44], [P.blanco, .32], [P.verdeClaro, .38], [P.verde, .26]];
  const items = specs.map(([c, s], i) => {
    const m = new THREE.Mesh(plusGeometry(), mat(c, { roughness: .38 }));
    m.scale.setScalar(s);
    m.userData = { phase: i * 1.3, spin: .25 + i * .07, base: new THREE.Vector3() };
    S.add(m); return m;
  });
  const ring = new THREE.Mesh(new THREE.TorusGeometry(3.4, .02, 8, 160), mat(P.verde, { transparent: true, opacity: .5 }));
  S.add(ring);
  const place = () => {
    const wide = st.w / st.h > 1.4, cx = wide ? 7.5 : 4.5;
    const offs = [[0, 0, 0], [-2.6, 1.8, -1.5], [2.2, 2, -2.5], [-1.4, -2.2, -1], [2.6, -1.6, -3]];
    items.forEach((m, i) => m.userData.base.set(cx + offs[i][0], offs[i][1], offs[i][2]));
    ring.position.set(cx, 0, -1);
    st.canvas.style.opacity = wide ? '1' : '.35';
  };
  st.onResize = place; place();
  st.update = (t) => {
    const p = st.progress();
    items.forEach(m => {
      const u = m.userData;
      m.position.set(u.base.x, u.base.y + Math.sin(t * .7 + u.phase) * .25 + p * 2, u.base.z);
      m.rotation.set(Math.sin(t * .4 + u.phase) * .5, t * u.spin, Math.sin(t * .3 + u.phase) * .2);
    });
    ring.rotation.set(Math.PI / 2.3 + Math.sin(t * .3) * .1, t * .1, 0);
    st.camera.position.x = pointer.x * .8; st.camera.position.y = pointer.y * .5;
    st.camera.lookAt(0, 0, 0);
  };
}

/* ==========================================================================
   Arranque
   ========================================================================== */
function start() {
  const orb = document.querySelector('.hero .hero-orb');
  if (orb) heroScene(orb);
  document.querySelectorAll('.scrolly-visual').forEach(servicesScene);
  const stats = document.querySelector('[data-gl="olas"]');
  if (stats) waveScene(stats, { opacity: .55, amp: .9, c1: P.verdeClaro, c2: P.verde, cam: [0, 6, 16] });
  document.querySelectorAll('.marquee-wrap').forEach(ringScene);
  document.querySelectorAll('.page-hero').forEach(heroPlusScene);
  const foot = document.querySelector('.site-footer');
  if (foot) waveScene(foot, { cols: 130, rows: 40, gap: .5, opacity: .5, amp: .7, c1: P.verde, c2: P.lima, cam: [0, 3.5, 12], cls: 'gl-foot' });
  doc.classList.add('gl-on');
  requestAnimationFrame(frame);
}

if (webglOK() && location.protocol !== 'file:') {
  try { start(); } catch (e) { console.warn('Escenas 3D desactivadas:', e); }
}
