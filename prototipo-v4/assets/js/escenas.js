/* ==========================================================================
   Escenas 3D por proyecto: "mesa holográfica" con la paleta institucional.
   Uso: <div class="escena-caso" data-plantilla="recaudo|catastro|documentos|alumbrado|
        datacenter|camaras|vial|satelital|energia"></div>
   Se puede girar y acercar; respeta "reducir movimiento" y la pausa global.
   ========================================================================== */
import * as THREE from './vendor/three.module.min.js';
import { OrbitControls } from './vendor/OrbitControls.js';

const doc = document.documentElement;
const quieto = () => doc.dataset.motion === 'reduce' || doc.dataset.paused === 'true';
const P = { marino: 0x1c2d4c, marino2: 0x263b63, lima: 0xb5c73a, verde: 0x194a2b, verde2: 0x2a6a3f, verde3: 0x8fbf9b, celeste: 0xd8effb, blanco: 0xf4f7f5, gris: 0xc9d0d8 };
const mat = (c, o = {}) => new THREE.MeshStandardMaterial({ color: c, roughness: .5, metalness: .08, ...o });
const brillo = (c, i = .9) => new THREE.MeshStandardMaterial({ color: c, emissive: c, emissiveIntensity: i });

function mesa(escena) {
  const g = new THREE.Group();
  const base = new THREE.Mesh(new THREE.CylinderGeometry(5.2, 5.5, .35, 96), mat(P.marino2, { roughness: .35, metalness: .4 }));
  base.position.y = -.175; g.add(base);
  const aro = new THREE.Mesh(new THREE.TorusGeometry(5.25, .04, 8, 160), brillo(P.lima, .7)); aro.rotation.x = Math.PI / 2; g.add(aro);
  const grilla = new THREE.PolarGridHelper(5, 16, 6, 96, 0x3d5786, 0x3d5786);
  grilla.position.y = .01; grilla.material.transparent = true; grilla.material.opacity = .55; g.add(grilla);
  escena.add(g);
  return g;
}
function paquetes(escena, curva, n, color = P.lima) {
  const lista = Array.from({ length: n }, (_, i) => { const m = new THREE.Mesh(new THREE.BoxGeometry(.14, .14, .14), brillo(color, .8)); m.userData.f = i / n; escena.add(m); return m; });
  return t => lista.forEach(m => { const k = (((m.userData.f + t * .18) % 1) + 1) % 1; m.position.copy(curva.getPointAt(k)); m.rotation.set(t * 2, t * 3, 0); });
}

/* ---------- plantillas ---------- */
const PLANTILLAS = {
  recaudo(E) {
    const monedas = new THREE.Group(); E.add(monedas);
    const geo = new THREE.CylinderGeometry(.55, .55, .14, 40), lado = mat(P.verde2, { metalness: .5, roughness: .3 }), cara = mat(0x3c8a52, { metalness: .4 });
    [[-2.2, 1.2, 6], [-1, -.6, 9], [.4, 1.4, 4]].forEach(([x, z, n]) => { for (let i = 0; i < n; i++) { const c = new THREE.Mesh(geo, [lado, cara, cara]); c.position.set(x, .07 + i * .15, z); c.rotation.y = i; monedas.add(c); } });
    const barras = [1.2, 1.9, 2.7, 3.6].map((h, i) => { const b = new THREE.Mesh(new THREE.BoxGeometry(.5, h, .5), mat([P.verde3, P.verde2, P.verde, P.lima][i])); b.position.set(1.6 + i * .7, h / 2, -.6); b.userData.h = h; E.add(b); return b; });
    const curva = new THREE.CatmullRomCurve3([new THREE.Vector3(-2.2, 1.2, 1.2), new THREE.Vector3(-.5, 3.2, 1), new THREE.Vector3(1.5, 4.2, 0), new THREE.Vector3(3.7, 3.9, -.6)]);
    const mover = paquetes(E, curva, 10);
    return t => { mover(t); barras.forEach((b, i) => { const k = 1 + Math.sin(t * 1.3 + i) * .05; b.scale.y = k; b.position.y = b.userData.h * k / 2; }); monedas.rotation.y = Math.sin(t * .4) * .15; };
  },
  catastro(E) {
    const tam = 8, n = 8, grupo = new THREE.Group(); E.add(grupo);
    const tonos = [P.verde2, P.verde3, 0x4f9a61, 0x6aa86e];
    for (let i = 0; i < n; i++) for (let j = 0; j < n; j++) {
      const h = .08 + ((i * 7 + j * 13) % 5) * .05, p = new THREE.Mesh(new THREE.BoxGeometry(tam / n - .08, h, tam / n - .08), mat(tonos[(i + j * 3) % 4], { roughness: .8 }));
      p.position.set(-tam / 2 + (i + .5) * tam / n, h / 2, -tam / 2 + (j + .5) * tam / n); p.userData.h = h; grupo.add(p);
    }
    grupo.scale.setScalar(.85);
    const laser = new THREE.Mesh(new THREE.PlaneGeometry(7.4, 1.6), new THREE.MeshBasicMaterial({ color: P.lima, transparent: true, opacity: .28, side: THREE.DoubleSide, depthWrite: false }));
    laser.rotation.y = Math.PI / 2; laser.position.y = .8; E.add(laser);
    const linea = new THREE.Mesh(new THREE.BoxGeometry(.04, .04, 7.4), brillo(P.lima, 1)); linea.position.y = .02; E.add(linea);
    const pines = [];
    for (let k = 0; k < 7; k++) { const pin = new THREE.Mesh(new THREE.ConeGeometry(.16, .45, 16), mat(P.celeste)); pin.rotation.x = Math.PI; pin.position.set(-3 + (k * 37 % 60) / 10, 1.2, -3 + (k * 23 % 60) / 10); E.add(pin); pines.push(pin); }
    return t => {
      const x = Math.sin(t * .6) * 3.3; laser.position.x = linea.position.x = x;
      grupo.children.forEach(p => { const d = Math.abs(p.position.x * .85 - x); p.material.emissive = new THREE.Color(P.lima); p.material.emissiveIntensity = d < .5 ? .35 : 0; });
      pines.forEach((p, i) => { p.position.y = 1.1 + Math.sin(t * 2 + i) * .15; p.rotation.y = t; });
    };
  },
  documentos(E) {
    const est = new THREE.Group(); E.add(est); est.position.set(-1.8, 0, 0);
    for (let r = 0; r < 3; r++) for (let c = 0; c < 4; c++) { const caja = new THREE.Mesh(new THREE.BoxGeometry(.7, .5, .9), mat(c % 2 ? 0xd9c9a3 : 0xe8dcbc, { roughness: .9 })); caja.position.set(c * .78 - 1.2, .26 + r * .55, 0); est.add(caja); }
    const nube = new THREE.Mesh(new THREE.CylinderGeometry(.9, .9, 1.6, 48), mat(P.celeste, { roughness: .3, metalness: .2 })); nube.position.set(2.6, 1.6, -.4); E.add(nube);
    [1, 1.5, 2].forEach(y => { const a = new THREE.Mesh(new THREE.TorusGeometry(.91, .03, 8, 48), brillo(P.lima, .6)); a.rotation.x = Math.PI / 2; a.position.set(2.6, y + .4, -.4); E.add(a); });
    const hojas = Array.from({ length: 9 }, (_, i) => { const h = new THREE.Mesh(new THREE.PlaneGeometry(.42, .56), mat(0xffffff, { side: THREE.DoubleSide })); h.userData.f = i / 9; E.add(h); return h; });
    const curva = new THREE.CatmullRomCurve3([new THREE.Vector3(-1.8, 1.9, .5), new THREE.Vector3(0, 3.4, .6), new THREE.Vector3(1.8, 3.3, 0), new THREE.Vector3(2.6, 2.5, -.4)]);
    return t => hojas.forEach(h => { const k = (h.userData.f + t * .15) % 1; h.position.copy(curva.getPointAt(k)); h.rotation.set(t * 1.5 + k * 6, t + k * 4, 0); h.scale.setScalar(1 - k * .55); });
  },
  alumbrado(E) {
    const via = new THREE.Mesh(new THREE.BoxGeometry(9, .05, 1.8), mat(0x2b3442, { roughness: .9 })); via.position.y = .03; E.add(via);
    for (let i = -4; i <= 4; i++) { const r = new THREE.Mesh(new THREE.BoxGeometry(.45, .06, .08), mat(0xffffff)); r.position.set(i, .06, 0); E.add(r); }
    const luces = [];
    for (let i = 0; i < 6; i++) for (const lado of [-1, 1]) {
      const x = -3.75 + i * 1.5, poste = new THREE.Mesh(new THREE.CylinderGeometry(.04, .05, 2.2, 10), mat(P.gris, { metalness: .6 })); poste.position.set(x, 1.1, lado * 1.2); E.add(poste);
      const brazo = new THREE.Mesh(new THREE.BoxGeometry(.08, .06, .55), mat(P.gris)); brazo.position.set(x, 2.15, lado * .95); E.add(brazo);
      const led = new THREE.Mesh(new THREE.BoxGeometry(.28, .08, .18), brillo(0xf6f2c4, 0)); led.position.set(x, 2.1, lado * .7); E.add(led);
      const cono = new THREE.Mesh(new THREE.ConeGeometry(.75, 2.05, 24, 1, true), new THREE.MeshBasicMaterial({ color: 0xfff6c8, transparent: true, opacity: 0, depthWrite: false, side: THREE.DoubleSide }));
      cono.position.set(x, 1.05, lado * .7); E.add(cono); luces.push({ led, cono, i });
    }
    const autos = [0, 1, 2].map(i => { const a = new THREE.Mesh(new THREE.BoxGeometry(.6, .28, .36), mat([P.lima, P.celeste, 0xffffff][i])); a.userData.v = .5 + i * .2; a.userData.carril = i % 2 ? .4 : -.4; E.add(a); return a; });
    return t => {
      const onda = (t * 1.2) % 9;
      luces.forEach(l => { const on = Math.max(0, 1 - Math.abs(l.i * 1.5 - onda) / 4); l.led.material.emissiveIntensity = .3 + on * 1.2; l.cono.material.opacity = .04 + on * .14; });
      autos.forEach(a => { a.position.set(((t * a.userData.v * 2 + a.userData.v * 7) % 9) - 4.5, .2, a.userData.carril); });
    };
  },
  datacenter(E) {
    const leds = [];
    [-2.4, -.8, .8, 2.4].forEach((x, k) => {
      const rack = new THREE.Mesh(new THREE.BoxGeometry(1.1, 3, 1.1), mat(P.marino, { metalness: .3, roughness: .35 })); rack.position.set(x, 1.5, -.6); E.add(rack);
      for (let u = 0; u < 9; u++) {
        const r = new THREE.Mesh(new THREE.BoxGeometry(.9, .04, .02), mat(0x3a5280)); r.position.set(x, .3 + u * .3, -.04); E.add(r);
        const l = new THREE.Mesh(new THREE.SphereGeometry(.035, 8, 6), brillo(u % 3 ? 0x3fd68a : P.lima, .2)); l.position.set(x + .35, .36 + u * .3, -.03); E.add(l); leds.push(l);
      }
    });
    const nube = new THREE.Mesh(new THREE.SphereGeometry(.6, 32, 16), mat(P.celeste, { roughness: .4 })); nube.position.set(0, 4.3, -.6); nube.scale.set(1.8, 1, 1); E.add(nube);
    const flujos = [-2.4, -.8, .8, 2.4].map(x => paquetes(E, new THREE.CatmullRomCurve3([new THREE.Vector3(x, 3.05, -.6), new THREE.Vector3(x * .6, 3.8, -.4), new THREE.Vector3(0, 4.2, -.6)]), 3));
    const usuarios = [-2, 0, 2].map(x => { const u = new THREE.Mesh(new THREE.CapsuleGeometry(.18, .35, 6, 12), mat(P.verde3)); u.position.set(x, .45, 2.4); E.add(u); return u; });
    return t => { flujos.forEach(f => f(t)); leds.forEach((l, i) => { l.material.emissiveIntensity = Math.sin(t * 5 + i * 1.7) > .2 ? 1 : .15; }); usuarios.forEach((u, i) => { u.position.y = .45 + Math.abs(Math.sin(t * 2 + i)) * .1; }); };
  },
  camaras(E) {
    const plaza = new THREE.Mesh(new THREE.CylinderGeometry(3.6, 3.6, .06, 6), mat(0x3d5786, { roughness: .9 })); plaza.position.y = .03; E.add(plaza);
    const fuente = new THREE.Mesh(new THREE.CylinderGeometry(.6, .7, .4, 24), mat(P.celeste)); fuente.position.y = .2; E.add(fuente);
    const cabezas = [];
    [[3.4, 0], [-1.7, 2.9], [-1.7, -2.9]].forEach(([x, z]) => {
      const poste = new THREE.Mesh(new THREE.CylinderGeometry(.07, .08, 3, 12), mat(P.gris, { metalness: .6 })); poste.position.set(x, 1.5, z); E.add(poste);
      const cab = new THREE.Group(); cab.position.set(x, 3, z); E.add(cab);
      const domo = new THREE.Mesh(new THREE.SphereGeometry(.28, 24, 12), mat(0xffffff)); cab.add(domo);
      const lente = new THREE.Mesh(new THREE.SphereGeometry(.12, 16, 8), mat(0x0f1a30, { roughness: .1 })); lente.position.z = .22; cab.add(lente);
      const cono = new THREE.Mesh(new THREE.ConeGeometry(1.4, 3.6, 32, 1, true), new THREE.MeshBasicMaterial({ color: P.lima, transparent: true, opacity: .14, depthWrite: false, side: THREE.DoubleSide }));
      cono.geometry.translate(0, -1.8, 0); cono.rotation.x = -Math.PI / 2 - .7; cab.add(cono);
      cab.lookAt(0, 0, 0); cabezas.push({ cab, base: cab.rotation.y });
    });
    const personas = Array.from({ length: 6 }, (_, i) => { const p = new THREE.Mesh(new THREE.CapsuleGeometry(.12, .3, 6, 10), mat(i % 2 ? P.verde3 : P.blanco)); p.userData = { r: 1.4 + (i % 3) * .6, v: .3 + i * .07, f: i }; E.add(p); return p; });
    return t => {
      cabezas.forEach((c, i) => { c.cab.rotation.y = c.base + Math.sin(t * .6 + i * 2) * .6; });
      personas.forEach(p => { const a = t * p.userData.v + p.userData.f; p.position.set(Math.cos(a) * p.userData.r, .27, Math.sin(a) * p.userData.r); });
    };
  },
  vial(E) {
    const curva = new THREE.CatmullRomCurve3([new THREE.Vector3(-4.5, .05, 2), new THREE.Vector3(-1.5, .05, .6), new THREE.Vector3(1, .05, -1.2), new THREE.Vector3(4.5, .05, -1.6)]);
    E.add(new THREE.Mesh(new THREE.TubeGeometry(curva, 80, .5, 4, false), mat(0x2b3442, { roughness: .9, flatShading: true })));
    const montes = [[-3, -2.5, 1.6], [2.8, 2.4, 1.3], [0, -3.4, 1.1]].map(([x, z, h]) => { const m = new THREE.Mesh(new THREE.ConeGeometry(1.6, h * 1.6, 7), mat(P.verde2, { flatShading: true })); m.position.set(x, h * .8, z); E.add(m); return m; });
    const tunel = new THREE.Mesh(new THREE.TorusGeometry(.7, .18, 12, 24, Math.PI), mat(P.gris)); tunel.position.set(1, 0, -1.2); tunel.rotation.y = -.6; E.add(tunel);
    const camiones = [0, 1].map(i => { const c = new THREE.Mesh(new THREE.BoxGeometry(.6, .35, .3), mat(i ? P.lima : P.celeste)); c.userData.f = i * .5; E.add(c); return c; });
    const hitos = [.15, .45, .75].map(k => { const h = new THREE.Mesh(new THREE.ConeGeometry(.12, .4, 12), brillo(P.lima, .6)); h.position.copy(curva.getPointAt(k)).add(new THREE.Vector3(0, .4, .8)); E.add(h); return h; });
    return t => {
      camiones.forEach(c => { const k = (c.userData.f + t * .07) % 1; c.position.copy(curva.getPointAt(k)).setY(.25); c.lookAt(curva.getPointAt(Math.min(.999, k + .01)).setY(.25)); });
      hitos.forEach((h, i) => { h.position.y = .45 + Math.sin(t * 2 + i) * .12; });
    };
  },
  satelital(E) {
    const casa = new THREE.Mesh(new THREE.BoxGeometry(2.2, 1.2, 1.6), mat(P.blanco)); casa.position.set(-1.2, .6, .4); E.add(casa);
    const techo = new THREE.Mesh(new THREE.ConeGeometry(1.7, .9, 4), mat(P.verde, { flatShading: true })); techo.position.set(-1.2, 1.65, .4); techo.rotation.y = Math.PI / 4; techo.scale.set(1, 1, .75); E.add(techo);
    const mastil = new THREE.Mesh(new THREE.CylinderGeometry(.05, .05, 1, 12), mat(P.gris, { metalness: .6 })); mastil.position.set(1.5, .5, .6); E.add(mastil);
    const plato = new THREE.Mesh(new THREE.BoxGeometry(1, .06, .65), mat(0xffffff, { roughness: .2 })); plato.position.set(1.5, 1.05, .6); plato.rotation.x = -.5; E.add(plato);
    const sats = [0, 1, 2].map(i => { const g = new THREE.Group(); g.add(new THREE.Mesh(new THREE.BoxGeometry(.4, .12, .25), mat(0xe9edf1, { metalness: .5 }))); const pan = new THREE.Mesh(new THREE.BoxGeometry(1.2, .02, .4), mat(P.marino2)); pan.position.x = .8; g.add(pan); g.userData.f = i / 3; E.add(g); return g; });
    const hazG = new THREE.BufferGeometry().setFromPoints([new THREE.Vector3(), new THREE.Vector3()]);
    const haz = new THREE.Line(hazG, new THREE.LineDashedMaterial({ color: P.lima, dashSize: .25, gapSize: .15 })); E.add(haz);
    const ondas = [0, 1, 2].map(i => { const o = new THREE.Mesh(new THREE.TorusGeometry(1, .025, 8, 64), new THREE.MeshBasicMaterial({ color: P.lima, transparent: true })); o.rotation.x = Math.PI / 2; o.position.set(-1.2, .1, .4); o.userData.f = i / 3; E.add(o); return o; });
    return t => {
      let cerca = sats[0], dmin = 99;
      sats.forEach(s => { const a = ((s.userData.f + t * .06) % 1) * Math.PI - Math.PI / 2; s.position.set(Math.sin(a) * 5.5, 5 + Math.cos(a) * 1.4, -1.5); const d = Math.abs(s.position.x - 1.5); if (d < dmin) { dmin = d; cerca = s; } });
      hazG.attributes.position.setXYZ(0, cerca.position.x, cerca.position.y, cerca.position.z); hazG.attributes.position.setXYZ(1, 1.5, 1.1, .6); hazG.attributes.position.needsUpdate = true;
      haz.computeLineDistances(); haz.material.dashOffset = -t * 2;
      ondas.forEach(o => { const k = (t * .4 + o.userData.f) % 1; o.scale.setScalar(.8 + k * 3); o.material.opacity = (1 - k) * .7; });
    };
  },
  energia(E) {
    const paneles = [];
    for (let i = 0; i < 3; i++) for (let j = 0; j < 2; j++) {
      const p = new THREE.Mesh(new THREE.BoxGeometry(1.3, .05, .8), [mat(P.gris), mat(P.gris), mat(0x22406e, { metalness: .5, roughness: .2 }), mat(P.gris), mat(P.gris), mat(P.gris)]);
      p.position.set(-2.4 + i * 1.6, .7, -1 + j * 1.3); p.rotation.x = -.45; E.add(p); paneles.push(p);
      const pata = new THREE.Mesh(new THREE.CylinderGeometry(.03, .03, .7, 8), mat(P.gris)); pata.position.set(p.position.x, .35, p.position.z); E.add(pata);
    }
    const sol = new THREE.Mesh(new THREE.SphereGeometry(.55, 32, 16), brillo(0xd9e35a, .6)); sol.position.set(2.8, 4, -1.5); E.add(sol);
    const halo = new THREE.Mesh(new THREE.TorusGeometry(.85, .03, 8, 64), brillo(P.lima, .6)); halo.position.copy(sol.position); E.add(halo);
    const rayos = Array.from({ length: 6 }, (_, i) => { const r = new THREE.Mesh(new THREE.SphereGeometry(.07, 8, 6), brillo(P.lima, 1)); r.userData.f = i / 6; E.add(r); return r; });
    const farol = new THREE.Mesh(new THREE.CylinderGeometry(.05, .05, 2.4, 10), mat(P.gris)); farol.position.set(3, 1.2, 2); E.add(farol);
    const led = new THREE.Mesh(new THREE.BoxGeometry(.3, .08, .2), brillo(0xfff6c8, .2)); led.position.set(2.85, 2.4, 2); E.add(led);
    return t => {
      halo.rotation.y = t; halo.rotation.x = Math.sin(t * .5) * .6;
      rayos.forEach((r, i) => { const k = (r.userData.f + t * .3) % 1, dest = paneles[i % paneles.length].position; r.position.lerpVectors(sol.position, dest, k); });
      led.material.emissiveIntensity = .5 + .5 * Math.sin(t * 1.5);
    };
  },
};

export function crearEscenaCaso(host) {
  const plantilla = PLANTILLAS[host.dataset.plantilla] ? host.dataset.plantilla : 'datacenter';
  const r = new THREE.WebGLRenderer({ antialias: true, alpha: true });
  r.setPixelRatio(Math.min(devicePixelRatio || 1, 2)); r.toneMapping = THREE.ACESFilmicToneMapping;
  r.domElement.setAttribute('aria-hidden', 'true');
  host.prepend(r.domElement);
  const escena = new THREE.Scene();
  const cam = new THREE.PerspectiveCamera(36, 1, .1, 100); cam.position.set(9, 7.5, 11);
  const ctl = new OrbitControls(cam, r.domElement);
  ctl.enableDamping = true; ctl.enablePan = false; ctl.maxPolarAngle = 1.35;
  ctl.target.set(0, 1.1, 0); ctl.minDistance = 10; ctl.maxDistance = 34; ctl.autoRotate = !quieto(); ctl.autoRotateSpeed = .8;
  ctl.addEventListener('start', () => { ctl.autoRotate = false; });
  escena.add(new THREE.HemisphereLight(0xffffff, 0x1c2d4c, 1.5));
  const sol = new THREE.DirectionalLight(0xffffff, 2.1); sol.position.set(6, 10, 7); escena.add(sol);
  const contra = new THREE.DirectionalLight(P.lima, .8); contra.position.set(-8, 4, -6); escena.add(contra);
  mesa(escena);
  const tick = PLANTILLAS[plantilla](escena);
  let t = 0, ultimo = performance.now(), visible = true;
  new IntersectionObserver(([e]) => { visible = e.isIntersecting; }).observe(host);
  const redim = () => { const w = host.clientWidth, h = host.clientHeight; if (!w || !h) return; r.setSize(w, h, false); cam.aspect = w / h; cam.updateProjectionMatrix(); cam.position.setLength(19 * Math.max(1, 1.05 / cam.aspect)); };
  new ResizeObserver(redim).observe(host); redim();
  ['vm:pausa', 'vm:movimiento'].forEach(ev => document.addEventListener(ev, () => { ctl.autoRotate = !quieto(); }));
  tick(0);
  (function cuadro(ahora) {
    const dt = Math.max(0, Math.min(.05, (ahora - ultimo) / 1000)); ultimo = ahora;
    if (visible && !document.hidden) {
      if (!quieto()) { t += dt; tick(t); }
      ctl.update(); r.render(escena, cam);
    }
    requestAnimationFrame(cuadro);
  })(performance.now());
}

if ((() => { try { const c = document.createElement('canvas'); return !!(c.getContext('webgl2') || c.getContext('webgl')); } catch { return false; } })()) {
  document.querySelectorAll('.escena-caso').forEach(h => {
    try { crearEscenaCaso(h); h.classList.add('activa'); }
    catch (e) { console.error(e); }
  });
}
