/* ==========================================================================
   Valor+ · Escenas 3D con Three.js
   - Hero de inicio: núcleo "+" de la marca, esfera de datos, anillos orbitales y servicios en órbita
   - Cifras: mar de datos ondulante que reacciona al cursor
   - Servicios: nube de partículas que se transforma en una figura por servicio
   - Clientes: carrusel 3D en anillo
   - Encabezados internos: constelación de poliedros
   - Pie de página: ola de partículas
   Todo respeta "reducir movimiento" y el botón de pausa (data-paused en <html>).
   Si el navegador no tiene WebGL, el sitio sigue funcionando con las animaciones CSS/2D.
   ========================================================================== */
import * as THREE from './vendor/three.module.min.js';
import { EffectComposer } from './vendor/jsm/postprocessing/EffectComposer.js';
import { RenderPass } from './vendor/jsm/postprocessing/RenderPass.js';
import { UnrealBloomPass } from './vendor/jsm/postprocessing/UnrealBloomPass.js';
import { OutputPass } from './vendor/jsm/postprocessing/OutputPass.js';

const doc = document.documentElement;
const ROOT = doc.dataset.root || '';
const reduced = () => doc.dataset.motion === 'reduce';
const paused = () => doc.dataset.paused === 'true';
const still = () => reduced() || paused();
const coarse = matchMedia('(pointer: coarse)').matches;
const small = () => innerWidth < 760;
const LITE = coarse || (navigator.hardwareConcurrency || 8) <= 4;
const DPR = Math.min(devicePixelRatio || 1, LITE ? 1.5 : 1.75);
const clamp = (v, a, b) => Math.min(b, Math.max(a, v));
const lerp = (a, b, k) => a + (b - a) * k;
const ease = k => k < .5 ? 4 * k * k * k : 1 - Math.pow(-2 * k + 2, 3) / 2;

const C = { green: 0x00c26a, sky: 0x00a3e0, blue: 0x2b7de0, lime: 0xb8d430, navy: 0x0c264c, deep: 0x061528 };

function webglOK() {
  try { const c = document.createElement('canvas'); return !!(c.getContext('webgl2') || c.getContext('webgl')); }
  catch { return false; }
}

/* ---------- Puntero y scroll compartidos ---------- */
const pointer = { x: 0, y: 0, tx: 0, ty: 0 };
addEventListener('pointermove', e => { pointer.tx = e.clientX / innerWidth * 2 - 1; pointer.ty = -(e.clientY / innerHeight * 2 - 1); }, { passive: true });

/* ---------- Textura de brillo para partículas ---------- */
let glowTex;
function glow() {
  if (glowTex) return glowTex;
  const c = document.createElement('canvas'); c.width = c.height = 64;
  const g = c.getContext('2d'), gr = g.createRadialGradient(32, 32, 0, 32, 32, 32);
  gr.addColorStop(0, 'rgba(255,255,255,1)'); gr.addColorStop(.2, 'rgba(255,255,255,.85)'); gr.addColorStop(.5, 'rgba(255,255,255,.25)'); gr.addColorStop(1, 'rgba(255,255,255,0)');
  g.fillStyle = gr; g.fillRect(0, 0, 64, 64);
  glowTex = new THREE.CanvasTexture(c);
  return glowTex;
}

/* ---------- Escenario base y bucle único de render ---------- */
const STAGES = new Set();
const io = new IntersectionObserver(entries => entries.forEach(e => {
  const st = e.target.__stage; if (!st) return;
  st.visible = e.isIntersecting; st.dirty = true;
}), { rootMargin: '120px 0px' });

class Stage {
  constructor(host, { bloom = false, fov = 45, z = 10, clear = null, insert = 'prepend', cls = '' } = {}) {
    this.host = host;
    this.canvas = document.createElement('canvas');
    this.canvas.className = 'gl ' + cls;
    this.canvas.setAttribute('aria-hidden', 'true');
    host[insert](this.canvas);
    this.renderer = new THREE.WebGLRenderer({ canvas: this.canvas, antialias: !LITE, alpha: clear === null, powerPreference: 'high-performance' });
    this.renderer.setPixelRatio(DPR);
    this.renderer.setClearColor(clear ?? 0x000000, clear === null ? 0 : 1);
    this.scene = new THREE.Scene();
    this.camera = new THREE.PerspectiveCamera(fov, 1, .1, 400);
    this.camera.position.z = z;
    if (bloom && !LITE) {
      this.composer = new EffectComposer(this.renderer);
      this.composer.addPass(new RenderPass(this.scene, this.camera));
      this.bloom = new UnrealBloomPass(new THREE.Vector2(256, 256), .85, .55, .12);
      this.composer.addPass(this.bloom);
      this.composer.addPass(new OutputPass());
    }
    this.t = 0; this.visible = false; this.dirty = true;
    host.__stage = this;
    new ResizeObserver(() => this.resize()).observe(host);
    this.resize();
    io.observe(host);
    STAGES.add(this);
  }
  resize() {
    const w = this.host.clientWidth, h = this.host.clientHeight;
    if (!w || !h) return;
    this.w = w; this.h = h;
    this.renderer.setSize(w, h, false);
    this.composer?.setSize(w, h);
    this.camera.aspect = w / h; this.camera.updateProjectionMatrix();
    this.onResize?.(w, h);
    this.dirty = true;
  }
  progress() { // 0 cuando el host entra arriba, 1 cuando sale por arriba (0 con movimiento reducido)
    if (reduced()) return 0;
    const r = this.host.getBoundingClientRect();
    return clamp(-r.top / Math.max(1, r.height), 0, 1);
  }
  render() { this.composer ? this.composer.render() : this.renderer.render(this.scene, this.camera); }
}

let last = performance.now();
function frame(now) {
  const dt = Math.min((now - last) / 1000, .05); last = now;
  const k = reduced() ? 0 : 1;
  pointer.x = lerp(pointer.x, pointer.tx * k, .06); pointer.y = lerp(pointer.y, pointer.ty * k, .06);
  const s = still();
  for (const st of STAGES) {
    if (!st.visible || document.hidden || doc.dataset.overlay) continue;
    if (s && !st.dirty) continue;
    if (!s) st.t += dt;
    st.update?.(st.t, s ? 0 : dt, s);
    st.render();
    st.dirty = false;
  }
  requestAnimationFrame(frame);
}
addEventListener('scroll', () => { for (const st of STAGES) if (st.visible) st.dirty = true; }, { passive: true });
document.addEventListener('vm:pausa', () => STAGES.forEach(st => st.dirty = true));

/* ---------- Utilidades de geometría ---------- */
function roundedPolyShape(pts, r) {
  const s = new THREE.Shape(), n = pts.length;
  for (let i = 0; i < n; i++) {
    const p = pts[i], a = pts[(i - 1 + n) % n], b = pts[(i + 1) % n];
    const da = new THREE.Vector2().subVectors(a, p).normalize().multiplyScalar(r);
    const db = new THREE.Vector2().subVectors(b, p).normalize().multiplyScalar(r);
    const p1 = new THREE.Vector2().addVectors(p, da), p2 = new THREE.Vector2().addVectors(p, db);
    i === 0 ? s.moveTo(p1.x, p1.y) : s.lineTo(p1.x, p1.y);
    s.quadraticCurveTo(p.x, p.y, p2.x, p2.y);
  }
  s.closePath();
  return s;
}
function plusGeometry(L = 1.25, w = .4, depth = .55) {
  const V = (x, y) => new THREE.Vector2(x, y);
  const pts = [V(w, L), V(-w, L), V(-w, w), V(-L, w), V(-L, -w), V(-w, -w), V(-w, -L), V(w, -L), V(w, -w), V(L, -w), V(L, w), V(w, w)];
  const g = new THREE.ExtrudeGeometry(roundedPolyShape(pts, .16), { depth, bevelEnabled: true, bevelThickness: .14, bevelSize: .1, bevelSegments: 8, curveSegments: 10 });
  g.center();
  return g;
}
function fibSphere(n, r, jitter = 0) {
  const a = new Float32Array(n * 3), ga = Math.PI * (3 - Math.sqrt(5));
  for (let i = 0; i < n; i++) {
    const y = 1 - (i / (n - 1)) * 2, rad = Math.sqrt(1 - y * y), th = ga * i, rr = r + (Math.random() - .5) * jitter;
    a[i * 3] = Math.cos(th) * rad * rr; a[i * 3 + 1] = y * rr; a[i * 3 + 2] = Math.sin(th) * rad * rr;
  }
  return a;
}
function pointsMaterial(size, opacity = 1) {
  return new THREE.PointsMaterial({ size, map: glow(), vertexColors: true, transparent: true, opacity, depthWrite: false, blending: THREE.AdditiveBlending, sizeAttenuation: true });
}
function gradientColors(pos, c1, c2, c3, axis = 1, span = 1) {
  const n = pos.length / 3, col = new Float32Array(n * 3), A = new THREE.Color(c1), B = new THREE.Color(c2), Cc = new THREE.Color(c3), tmp = new THREE.Color();
  for (let i = 0; i < n; i++) {
    const k = clamp((pos[i * 3 + axis] / span + 1) / 2, 0, 1);
    k < .5 ? tmp.lerpColors(A, B, k * 2) : tmp.lerpColors(B, Cc, (k - .5) * 2);
    col.set([tmp.r, tmp.g, tmp.b], i * 3);
  }
  return col;
}
function circleTexture(src) {
  return new Promise(res => {
    const img = new Image();
    img.onload = () => {
      const S = 256, c = document.createElement('canvas'); c.width = c.height = S;
      const g = c.getContext('2d');
      g.beginPath(); g.arc(S / 2, S / 2, S / 2 - 6, 0, Math.PI * 2); g.closePath(); g.save(); g.clip();
      const m = Math.min(img.width, img.height);
      g.drawImage(img, (img.width - m) / 2, (img.height - m) / 2, m, m, 0, 0, S, S); g.restore();
      g.lineWidth = 8; g.strokeStyle = 'rgba(255,255,255,.7)'; g.stroke();
      const t = new THREE.CanvasTexture(c); t.colorSpace = THREE.SRGBColorSpace; res(t);
    };
    img.onerror = () => res(null);
    img.src = src;
  });
}
function nebula(scene, specs) {
  return specs.map(([color, x, y, z, s, o]) => {
    const sp = new THREE.Sprite(new THREE.SpriteMaterial({ map: glow(), color, transparent: true, opacity: o, depthWrite: false, blending: THREE.AdditiveBlending }));
    sp.position.set(x, y, z); sp.scale.setScalar(s); scene.add(sp); return sp;
  });
}
function starfield(n, rMin, rMax, size = .08) {
  const p = new Float32Array(n * 3), c = new Float32Array(n * 3), cols = [new THREE.Color(C.sky), new THREE.Color(C.green), new THREE.Color(0xffffff), new THREE.Color(C.lime)];
  for (let i = 0; i < n; i++) {
    const v = new THREE.Vector3().randomDirection().multiplyScalar(lerp(rMin, rMax, Math.random()));
    p.set([v.x, v.y, v.z], i * 3);
    const cc = cols[Math.random() * cols.length | 0]; c.set([cc.r, cc.g, cc.b], i * 3);
  }
  const g = new THREE.BufferGeometry();
  g.setAttribute('position', new THREE.BufferAttribute(p, 3)); g.setAttribute('color', new THREE.BufferAttribute(c, 3));
  return new THREE.Points(g, pointsMaterial(size, .8));
}

/* ==========================================================================
   1. Hero de inicio
   ========================================================================== */
function heroScene(hero) {
  const st = new Stage(hero, { bloom: true, fov: 38, z: 17, clear: C.deep });
  hero.classList.add('has-3d');
  const net = hero.querySelector('canvas.net'); net?.__stop?.(); net?.remove();

  const S = st.scene;
  S.fog = new THREE.FogExp2(C.deep, .012);
  nebula(S, [[C.green, -14, 4, -30, 34, .35], [C.sky, 16, 8, -40, 40, .3], [C.blue, 4, -10, -30, 36, .35], [C.lime, 10, -4, -20, 16, .12]]);
  const stars = starfield(LITE ? 900 : 2200, 18, 90, .14); S.add(stars);

  const core = new THREE.Group(); S.add(core);
  S.add(new THREE.AmbientLight(0x88aacc, .5));
  const l1 = new THREE.PointLight(C.green, 140, 40), l2 = new THREE.PointLight(C.sky, 140, 40), l3 = new THREE.DirectionalLight(0xffffff, 1.2);
  l3.position.set(3, 5, 8); S.add(l1, l2, l3);

  // "+" de la marca, extruido
  const plus = new THREE.Mesh(plusGeometry(), new THREE.MeshPhysicalMaterial({ color: C.lime, emissive: 0x5e7a00, emissiveIntensity: 1.1, metalness: .25, roughness: .22, clearcoat: 1, clearcoatRoughness: .08 }));
  core.add(plus);
  const plusEdges = new THREE.LineSegments(new THREE.EdgesGeometry(plus.geometry, 30), new THREE.LineBasicMaterial({ color: 0xeaff9c, transparent: true, opacity: .35 }));
  plus.add(plusEdges);

  // burbuja de vidrio
  const shell = new THREE.Mesh(new THREE.SphereGeometry(2.45, 64, 64), new THREE.MeshPhysicalMaterial({ color: 0x1a5aa0, transparent: true, opacity: .14, roughness: .05, metalness: .1, clearcoat: 1, side: THREE.DoubleSide, depthWrite: false }));
  core.add(shell);
  const ico = new THREE.LineSegments(new THREE.EdgesGeometry(new THREE.IcosahedronGeometry(3.25, 1)), new THREE.LineBasicMaterial({ color: C.sky, transparent: true, opacity: .32 }));
  core.add(ico);

  // esfera de datos (Fibonacci) que se expande con el scroll
  const N = LITE ? 1600 : 3600;
  const base = fibSphere(N, 4.1, .5);
  const sg = new THREE.BufferGeometry();
  const spos = new Float32Array(base);
  sg.setAttribute('position', new THREE.BufferAttribute(spos, 3));
  sg.setAttribute('color', new THREE.BufferAttribute(gradientColors(base, C.green, C.sky, C.blue, 1, 4.1), 3));
  const sphere = new THREE.Points(sg, pointsMaterial(.075, .95));
  core.add(sphere);
  const dirs = Array.from({ length: N }, (_, i) => new THREE.Vector3(base[i * 3], base[i * 3 + 1], base[i * 3 + 2]).normalize().multiplyScalar(.6 + Math.random() * 1.6));

  // anillos orbitales con satélites
  const rings = [];
  [[5, C.green, .9, .2], [5.7, C.sky, -.5, -.6], [6.4, C.lime, .3, 1.1]].forEach(([r, color, rx, rz], i) => {
    const g = new THREE.Group(); g.rotation.set(rx, 0, rz); core.add(g);
    const ring = new THREE.Mesh(new THREE.TorusGeometry(r, .014, 8, 220), new THREE.MeshBasicMaterial({ color, transparent: true, opacity: .55 }));
    g.add(ring);
    const sat = new THREE.Sprite(new THREE.SpriteMaterial({ map: glow(), color, blending: THREE.AdditiveBlending, depthWrite: false }));
    sat.scale.setScalar(.7); g.add(sat);
    rings.push({ g, sat, r, speed: .5 + i * .22, phase: i * 2 });
  });

  // servicios en órbita (texturas reales)
  const orbit = new THREE.Group(); orbit.rotation.x = -.35; core.add(orbit);
  const sprites = [];
  const srcs = [...document.querySelectorAll('.hero-orb img')].map(i => i.getAttribute('src'));
  srcs.forEach((src, i) => circleTexture(src).then(tex => {
    if (!tex) return;
    const sp = new THREE.Sprite(new THREE.SpriteMaterial({ map: tex, transparent: true }));
    sp.scale.setScalar(1.05); orbit.add(sp);
    sprites.push({ sp, a: i / srcs.length * Math.PI * 2 });
    st.dirty = true;
  }));

  // haces de luz que salen del núcleo
  const beams = new THREE.Group(); core.add(beams);
  for (let i = 0; i < 14; i++) {
    const m = new THREE.Mesh(new THREE.CylinderGeometry(.006, .03, 6.5, 6, 1, true), new THREE.MeshBasicMaterial({ color: i % 2 ? C.sky : C.green, transparent: true, opacity: .18, blending: THREE.AdditiveBlending, depthWrite: false }));
    m.position.y = 3.25; const pivot = new THREE.Group(); pivot.add(m);
    pivot.rotation.set(Math.random() * Math.PI, Math.random() * Math.PI, Math.random() * Math.PI);
    beams.add(pivot);
  }

  let layout = { x: 4.6, y: 0, z: 0, s: 1 };
  st.onResize = (w, h) => {
    const a = w / h;
    layout = a > 1.15 ? { x: Math.min(6.4, 3.1 * a), y: -.2, z: -2, s: .74 } : { x: 0, y: 4.6, z: -8, s: .7 };
    st.canvas.style.opacity = a > 1.15 ? '1' : '.55';
  };
  st.onResize(st.w, st.h);

  st.update = (t, dt, isStill) => {
    const p = st.progress();
    const ep = ease(p);
    core.position.set(layout.x, layout.y + ep * 2.5, layout.z);
    core.scale.setScalar(layout.s * (1 + ep * .25));
    core.rotation.y = pointer.x * .35;
    core.rotation.x = -pointer.y * .2;

    plus.rotation.y = t * .55 + ep * Math.PI * 1.5;
    plus.rotation.x = Math.sin(t * .6) * .28;
    plus.rotation.z = Math.sin(t * .35) * .12;
    const pulse = 1 + Math.sin(t * 2.2) * .04;
    plus.scale.setScalar(pulse);

    ico.rotation.x = t * .12; ico.rotation.y = -t * .18;
    shell.rotation.y = t * .05;
    sphere.rotation.y = t * .09; sphere.rotation.x = Math.sin(t * .2) * .2;
    // explosión de la esfera al hacer scroll
    for (let i = 0; i < N; i++) {
      const d = dirs[i], k = ep * 6 * (.4 + (i % 7) / 7);
      spos[i * 3] = base[i * 3] + d.x * k; spos[i * 3 + 1] = base[i * 3 + 1] + d.y * k; spos[i * 3 + 2] = base[i * 3 + 2] + d.z * k;
    }
    sg.attributes.position.needsUpdate = true;
    sphere.material.opacity = .95 * (1 - ep * .75);

    rings.forEach(r => {
      const a = t * r.speed + r.phase;
      r.sat.position.set(Math.cos(a) * r.r, Math.sin(a) * r.r, 0);
      r.g.rotation.y = t * .1 * r.speed;
    });
    sprites.forEach(o => {
      const a = o.a + t * .22;
      o.sp.position.set(Math.cos(a) * 6.2, Math.sin(a * 2) * .5, Math.sin(a) * 6.2);
    });
    beams.rotation.y = t * .07; beams.rotation.z = t * .05;
    beams.children.forEach((b, i) => { b.children[0].material.opacity = .04 + .08 * (1 + Math.sin(t * 1.5 + i)) / 2; });

    l1.position.set(Math.cos(t * .7) * 6 + layout.x, 3, Math.sin(t * .7) * 6);
    l2.position.set(Math.cos(t * .7 + Math.PI) * 6 + layout.x, -2, Math.sin(t * .7 + Math.PI) * 6);
    stars.rotation.y = t * .01 + pointer.x * .05; stars.rotation.x = pointer.y * .03;

    st.camera.position.x = lerp(st.camera.position.x, pointer.x * 1.4, .05);
    st.camera.position.y = lerp(st.camera.position.y, pointer.y * .9 - ep * 1.5, .05);
    st.camera.position.z = 17 - ep * 7;
    st.camera.lookAt(layout.x * .35, layout.y * .4, 0);
    if (st.bloom) st.bloom.strength = .8 + Math.sin(t * 1.3) * .12 + ep * .5;
  };
}

/* ==========================================================================
   2. Mar de datos (cifras) y ola del pie de página
   ========================================================================== */
const waveVert = `
uniform float uTime; uniform float uAmp; uniform vec2 uMouse; uniform float uSize; uniform vec3 uC1; uniform vec3 uC2; uniform vec3 uC3;
varying vec3 vColor; varying float vAlpha;
void main(){
  vec3 p = position;
  float d = distance(p.xz, uMouse);
  float h = sin(p.x * .32 + uTime * .9) * .55 + cos(p.z * .42 + uTime * 1.1) * .45 + sin((p.x + p.z) * .17 + uTime * .55) * .7;
  h += exp(-d * .28) * 1.6 * sin(uTime * 3.0 - d * 1.2);
  p.y += h * uAmp;
  float k = smoothstep(-1.6, 1.8, h);
  vColor = k < .5 ? mix(uC1, uC2, k * 2.) : mix(uC2, uC3, (k - .5) * 2.);
  vec4 mv = modelViewMatrix * vec4(p, 1.);
  gl_PointSize = uSize * (14. / -mv.z);
  vAlpha = smoothstep(60., 10., -mv.z);
  gl_Position = projectionMatrix * mv;
}`;
const waveFrag = `
uniform float uOpacity; varying vec3 vColor; varying float vAlpha;
void main(){
  float r = length(gl_PointCoord - .5);
  if (r > .5) discard;
  gl_FragColor = vec4(vColor, smoothstep(.5, .0, r) * vAlpha * uOpacity);
}`;
function waveScene(host, { cols = 170, rows = 70, gap = .42, opacity = 1, amp = 1, colors = [C.blue, C.sky, C.green], cam = [0, 5.5, 15], insert = 'prepend', cls = '' } = {}) {
  const st = new Stage(host, { fov: 50, z: cam[2], insert, cls });
  host.classList.add('has-gl');
  if (LITE) { cols = Math.round(cols * .55); rows = Math.round(rows * .55); gap *= 1.6; }
  const pos = new Float32Array(cols * rows * 3);
  let i = 0;
  for (let x = 0; x < cols; x++) for (let z = 0; z < rows; z++) pos.set([(x - cols / 2) * gap, 0, (z - rows / 2) * gap], 3 * i++);
  const g = new THREE.BufferGeometry(); g.setAttribute('position', new THREE.BufferAttribute(pos, 3));
  const u = {
    uTime: { value: 0 }, uAmp: { value: amp }, uMouse: { value: new THREE.Vector2(999, 999) }, uSize: { value: 5.5 * DPR }, uOpacity: { value: opacity },
    uC1: { value: new THREE.Color(colors[0]) }, uC2: { value: new THREE.Color(colors[1]) }, uC3: { value: new THREE.Color(colors[2]) },
  };
  const pts = new THREE.Points(g, new THREE.ShaderMaterial({ uniforms: u, vertexShader: waveVert, fragmentShader: waveFrag, transparent: true, depthWrite: false, blending: THREE.AdditiveBlending }));
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
    const p = st.progress();
    u.uTime.value = t;
    st.camera.position.y = cam[1] + pointer.y * .6 - p * 2;
    st.camera.position.x = pointer.x * 1.5;
    st.camera.lookAt(0, -1 + p * 1.5, 0);
    pts.rotation.y = Math.sin(t * .05) * .15;
  };
  return st;
}

/* ==========================================================================
   3. Servicios: partículas que se transforman en una figura por servicio
   ========================================================================== */
function sampleShapes(N) {
  const R = Math.random, V = new THREE.Vector3();
  const make = fn => { const a = new Float32Array(N * 3); for (let i = 0; i < N; i++) { fn(i, V); a.set([V.x, V.y, V.z], i * 3); } return a; };
  return [
    // 1. Recaudo: pila de monedas
    make((i, v) => {
      const k = i % 5, R0 = 2.1, h = .32, y0 = (k - 2) * .55, x0 = Math.sin(k * 1.7) * .25;
      const th = R() * Math.PI * 2;
      if (R() < .55) { const r = R0 * Math.sqrt(R()); v.set(Math.cos(th) * r + x0, y0 + (R() < .5 ? h / 2 : -h / 2), Math.sin(th) * r); }
      else v.set(Math.cos(th) * R0 + x0, y0 + (R() - .5) * h, Math.sin(th) * R0);
      v.applyAxisAngle(new THREE.Vector3(1, 0, 0), .35);
    }),
    // 2. Automatización: globo de datos con meridianos y paralelos
    make((i, v) => {
      const r = 2.7;
      if (R() < .65) {
        if (R() < .5) { const lon = Math.floor(R() * 12) / 12 * Math.PI * 2, lat = (R() - .5) * Math.PI; v.set(Math.cos(lat) * Math.cos(lon) * r, Math.sin(lat) * r, Math.cos(lat) * Math.sin(lon) * r); }
        else { const lat = (Math.floor(R() * 9) / 8 - .5) * Math.PI * .9, lon = R() * Math.PI * 2; v.set(Math.cos(lat) * Math.cos(lon) * r, Math.sin(lat) * r, Math.cos(lat) * Math.sin(lon) * r); }
      } else v.randomDirection().multiplyScalar(r * (.98 + R() * .04));
    }),
    // 3. Proyectos: estructura reticular (andamio)
    make((i, v) => {
      const g = [-2.1, -.7, .7, 2.1], a = R() * 3 | 0, c1 = g[R() * 4 | 0], c2 = g[R() * 4 | 0], s = (R() - .5) * 4.2;
      a === 0 ? v.set(s, c1, c2) : a === 1 ? v.set(c1, s, c2) : v.set(c1, c2, s);
    }),
    // 4. Consultoría: nudo toroidal
    make((i, v) => {
      const t = R() * Math.PI * 2, p = 2, q = 3, r = 1.25 * (2 + Math.cos(q * t));
      const c = new THREE.Vector3(r * Math.cos(p * t), 1.25 * Math.sin(q * t) * 1.2, r * Math.sin(p * t));
      v.copy(c).add(new THREE.Vector3().randomDirection().multiplyScalar(.38 * Math.sqrt(R())));
      v.multiplyScalar(.82);
    }),
    // 5. Seguridad: candado
    make((i, v) => {
      if (R() < .62) { // cuerpo
        const w = 3.2, h = 2.4, d = 1.1, f = R() * 3 | 0, a = R() - .5, b = R() - .5, sg = R() < .5 ? -.5 : .5;
        f === 0 ? v.set(sg * w, a * h, b * d) : f === 1 ? v.set(a * w, sg * h, b * d) : v.set(a * w, b * h, sg * d);
        v.y -= 1;
        if (Math.hypot(v.x, v.y + .8) < .35 && Math.abs(v.z) > .5) v.z *= .2; // ojo de la cerradura
      } else { // arco
        const t = R() * Math.PI, rr = 1.15;
        v.set(Math.cos(t) * rr, .2 + Math.sin(t) * rr * 1.25, 0).add(new THREE.Vector3().randomDirection().multiplyScalar(.22));
      }
    }),
    // 6. Energía: sol con rayos
    make((i, v) => {
      const u = R();
      if (u < .45) v.randomDirection().multiplyScalar(1.35);
      else if (u < .85) { const k = i % 18, d = new THREE.Vector3(Math.cos(k / 18 * Math.PI * 2), Math.sin(k / 18 * Math.PI * 2), Math.sin(k * 2.3) * .35).normalize(); v.copy(d).multiplyScalar(1.8 + R() * 1.6); }
      else { const t = R() * Math.PI * 2; v.set(Math.cos(t) * 3.4, Math.sin(t) * 3.4, (R() - .5) * .2); }
    }),
  ];
}
function morphScene(vis) {
  const figs = [...vis.querySelectorAll('figure')];
  const steps = [...vis.closest('.scrolly').querySelectorAll('.scrolly-step')];
  if (!figs.length || !steps.length) return;
  const st = new Stage(vis, { bloom: true, fov: 42, z: 11, clear: C.navy });
  vis.classList.add('has-3d');
  const N = LITE ? 3500 : 8000;
  const shapes = sampleShapes(N);
  const colors = figs.map(f => new THREE.Color(getComputedStyle(f).getPropertyValue('--c').trim() || '#00c26a'));
  const pos = new Float32Array(shapes[0]), col = new Float32Array(N * 3);
  const delay = new Float32Array(N).map(() => Math.random());
  const g = new THREE.BufferGeometry();
  g.setAttribute('position', new THREE.BufferAttribute(pos, 3)); g.setAttribute('color', new THREE.BufferAttribute(col, 3));
  const pts = new THREE.Points(g, pointsMaterial(.095, 1)); st.scene.add(pts);
  const halo = nebula(st.scene, [[0xffffff, 0, 0, -6, 16, .18]])[0];
  const dust = starfield(LITE ? 300 : 700, 8, 30, .08); st.scene.add(dust);

  let from = 0, to = 0, k = 1;
  const tmp = new THREE.Color(), white = new THREE.Color(0xffffff);
  function paint(ci, kk) {
    for (let i = 0; i < N; i++) {
      tmp.copy(colors[ci]).lerp(white, (i % 9 === 0) ? .55 : (i % 4) * .06);
      if (kk < 1) tmp.lerp(colors[from], 1 - kk);
      col.set([tmp.r, tmp.g, tmp.b], i * 3);
    }
    g.attributes.color.needsUpdate = true;
  }
  paint(0, 1);
  const obs = new IntersectionObserver(es => es.forEach(e => {
    if (!e.isIntersecting) return;
    const i = steps.indexOf(e.target);
    if (i === to || i < 0) return;
    from = to; to = i; k = still() ? 1 : 0;
    if (still()) { pos.set(shapes[to]); g.attributes.position.needsUpdate = true; paint(to, 1); }
    st.dirty = true;
  }), { rootMargin: '-45% 0px -45% 0px' });
  steps.forEach(s => obs.observe(s));

  st.update = (t, dt) => {
    if (k < 1) {
      k = Math.min(1, k + dt / 1.6);
      const A = shapes[from], B = shapes[to];
      for (let i = 0; i < N; i++) {
        const kk = ease(clamp(k * 1.5 - delay[i] * .5, 0, 1));
        const swirl = Math.sin(kk * Math.PI) * 1.4;
        const ix = i * 3;
        const x = lerp(A[ix], B[ix], kk), y = lerp(A[ix + 1], B[ix + 1], kk), z = lerp(A[ix + 2], B[ix + 2], kk);
        const ang = swirl * (delay[i] - .5) * 2;
        pos[ix] = x * Math.cos(ang) - z * Math.sin(ang);
        pos[ix + 1] = y + Math.sin(i + t * 4) * swirl * .25;
        pos[ix + 2] = x * Math.sin(ang) + z * Math.cos(ang);
      }
      g.attributes.position.needsUpdate = true;
      paint(to, ease(k));
    }
    pts.rotation.y = t * .28 + pointer.x * .5;
    pts.rotation.x = Math.sin(t * .35) * .18 - pointer.y * .3;
    halo.material.color.copy(colors[to]);
    dust.rotation.y = -t * .03;
    if (st.bloom) st.bloom.strength = .95;
  };
}

/* ==========================================================================
   4. Clientes: carrusel 3D en anillo
   ========================================================================== */
function cardTexture(img) {
  return new Promise(res => {
    const go = () => {
      const W = 512, H = 320, c = document.createElement('canvas'); c.width = W; c.height = H;
      const g = c.getContext('2d'), r = 36;
      g.fillStyle = '#ffffff';
      g.beginPath(); g.moveTo(r, 0); g.arcTo(W, 0, W, H, r); g.arcTo(W, H, 0, H, r); g.arcTo(0, H, 0, 0, r); g.arcTo(0, 0, W, 0, r); g.closePath(); g.fill();
      const pad = 44, sc = Math.min((W - pad * 2) / img.naturalWidth, (H - pad * 2) / img.naturalHeight);
      const w = img.naturalWidth * sc, h = img.naturalHeight * sc;
      g.drawImage(img, (W - w) / 2, (H - h) / 2, w, h);
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
  const bgColor = () => new THREE.Color(getComputedStyle(wrap.closest('section') || document.body).backgroundColor);
  st.scene.fog = new THREE.Fog(bgColor(), R + 6, R * 2 + 10);
  new MutationObserver(() => { st.scene.fog.color = bgColor(); st.dirty = true; }).observe(doc, { attributes: true, attributeFilter: ['data-theme', 'data-contrast'] });
  imgs.forEach((img, i) => cardTexture(img).then(tex => {
    if (!tex) return;
    const m = new THREE.Mesh(new THREE.PlaneGeometry(3, 1.88), new THREE.MeshBasicMaterial({ map: tex, transparent: true, side: THREE.DoubleSide }));
    const a = i / n * Math.PI * 2;
    m.position.set(Math.sin(a) * R, 0, Math.cos(a) * R);
    m.rotation.y = a;
    ring.add(m); st.dirty = true;
  }));
  let vel = 0, drag = false, lx = 0;
  host.addEventListener('pointerdown', e => { drag = true; lx = e.clientX; host.setPointerCapture?.(e.pointerId); });
  host.addEventListener('pointermove', e => { if (!drag) return; vel = (e.clientX - lx) * .004; ring.rotation.y += vel; lx = e.clientX; st.dirty = true; });
  host.addEventListener('pointerup', () => { drag = false; });
  st.camera.position.set(0, 1.8, R + 6.5);
  st.camera.lookAt(0, 0, 0);
  st.update = (t, dt) => {
    const stopped = mq.classList.contains('is-paused');
    if (!drag) { vel *= .94; ring.rotation.y += vel + (stopped ? 0 : dt * .18); }
    ring.position.y = Math.sin(t * .8) * .12;
    st.camera.position.x = pointer.x * 2;
    st.camera.lookAt(0, 0, 0);
  };
  mq.parentElement.querySelector('.pause-btn')?.addEventListener('click', () => { st.dirty = true; });
}

/* ==========================================================================
   5. Encabezados internos: constelación de poliedros
   ========================================================================== */
function constellationScene(ph) {
  const st = new Stage(ph, { fov: 45, z: 14, insert: 'prepend', cls: 'gl-hero' });
  ph.classList.add('has-3d');
  const S = st.scene, shapes = [];
  const geos = [new THREE.IcosahedronGeometry(1.2, 0), new THREE.OctahedronGeometry(1.1, 0), new THREE.DodecahedronGeometry(1, 0), new THREE.TorusGeometry(.9, .3, 10, 24), new THREE.TetrahedronGeometry(1.1, 0), new THREE.IcosahedronGeometry(.8, 1)];
  const cols = [C.green, C.sky, C.lime, C.blue, C.green, C.sky];
  const wide = () => st.w / st.h > 1.3;
  geos.forEach((geo, i) => {
    const grp = new THREE.Group();
    const line = new THREE.LineSegments(new THREE.EdgesGeometry(geo), new THREE.LineBasicMaterial({ color: cols[i], transparent: true, opacity: .75 }));
    const fill = new THREE.Mesh(geo, new THREE.MeshBasicMaterial({ color: cols[i], transparent: true, opacity: .07, blending: THREE.AdditiveBlending, depthWrite: false }));
    const pts = new THREE.Points(new THREE.BufferGeometry().setAttribute('position', geo.getAttribute('position').clone()), new THREE.PointsMaterial({ color: cols[i], size: .16, map: glow(), transparent: true, depthWrite: false, blending: THREE.AdditiveBlending }));
    grp.add(line, fill, pts);
    grp.userData = { base: new THREE.Vector3(), spin: new THREE.Vector3(Math.random() * .5 + .1, Math.random() * .5 + .1, 0), phase: Math.random() * 6, s: .6 + Math.random() * .7 };
    S.add(grp); shapes.push(grp);
  });
  const place = () => {
    const xr = wide() ? [3, 12] : [-6, 6];
    shapes.forEach((s, i) => {
      s.userData.base.set(lerp(xr[0], xr[1], (i + .5) / shapes.length) + (Math.random() - .5) * 2, (Math.random() - .5) * 6, -Math.random() * 6);
      s.scale.setScalar(s.userData.s * (wide() ? 1 : .7));
    });
  };
  st.onResize = place; place();
  const dust = starfield(LITE ? 300 : 800, 6, 40, .1); S.add(dust);
  st.update = (t) => {
    const p = st.progress();
    shapes.forEach(s => {
      const u = s.userData;
      s.position.set(u.base.x, u.base.y + Math.sin(t * .8 + u.phase) * .4 + p * 3, u.base.z);
      s.rotation.x = t * u.spin.x; s.rotation.y = t * u.spin.y;
    });
    dust.rotation.y = t * .02;
    st.camera.position.x = pointer.x * 1.2; st.camera.position.y = pointer.y * .8;
    st.camera.lookAt(0, 0, 0);
    st.canvas.style.opacity = String(1 - p * .8);
  };
}

/* ==========================================================================
   Arranque
   ========================================================================== */
function start() {
  const hero = document.querySelector('.hero');
  if (hero) heroScene(hero);
  const stats = document.querySelector('[data-gl="olas"]');
  if (stats) waveScene(stats, { opacity: 1, amp: 1.1 });
  document.querySelectorAll('.scrolly-visual').forEach(v => { if (getComputedStyle(v).display !== 'none') morphScene(v); });
  document.querySelectorAll('.marquee-wrap').forEach(ringScene);
  document.querySelectorAll('.page-hero').forEach(constellationScene);
  const foot = document.querySelector('.site-footer');
  if (foot) waveScene(foot, { cols: 150, rows: 45, gap: .45, opacity: .7, amp: .9, colors: [C.blue, C.sky, C.green], cam: [0, 3.5, 12], cls: 'gl-foot' });
  doc.classList.add('gl-on');
  requestAnimationFrame(frame);
}

if (webglOK() && location.protocol !== 'file:') {
  try { start(); } catch (e) { console.warn('Escenas 3D desactivadas:', e); }
}
