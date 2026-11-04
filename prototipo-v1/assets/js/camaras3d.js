/* ==========================================================================
   Visor 3D de cámaras de seguridad: autodomo PTZ, lectura de placas (LPR) y multisensor.
   El usuario gira y acerca el modelo; el cono muestra el campo de visión.
   ========================================================================== */
import * as THREE from './vendor/three.module.min.js';
import { OrbitControls } from './vendor/OrbitControls.js';

const doc = document.documentElement;
const quieto = () => doc.dataset.movimiento === 'no';
const P = { marino: 0x1c2d4c, lima: 0xb5c73a, blanco: 0xf4f6f8, gris: 0xc9d0d8, oscuro: 0x16202f };
const mat = (color, o = {}) => new THREE.MeshStandardMaterial({ color, roughness: .35, metalness: .1, ...o });
const vidrio = () => new THREE.MeshPhysicalMaterial({ color: 0x0f1a30, roughness: .05, metalness: .2, transmission: .2, transparent: true, opacity: .85, clearcoat: 1 });

function lente(r = .16) {
  const g = new THREE.Group();
  const aro = new THREE.Mesh(new THREE.CylinderGeometry(r * 1.25, r * 1.25, .08, 32), mat(0x2b3442, { metalness: .6 }));
  const cristal = new THREE.Mesh(new THREE.SphereGeometry(r, 32, 16, 0, Math.PI * 2, 0, Math.PI / 2), vidrio());
  cristal.position.y = .04;
  g.add(aro, cristal);
  return g;
}
function poste() {
  const g = new THREE.Group();
  const tubo = new THREE.Mesh(new THREE.CylinderGeometry(.12, .12, 3.2, 24), mat(P.gris, { metalness: .6 }));
  tubo.position.y = -1.6; g.add(tubo);
  return g;
}
function cono(angulo, largo, color = P.lima) {
  const r = Math.tan(angulo / 2) * largo;
  const c = new THREE.Mesh(new THREE.ConeGeometry(r, largo, 48, 1, true), new THREE.MeshBasicMaterial({ color, transparent: true, opacity: .14, side: THREE.DoubleSide, depthWrite: false }));
  c.geometry.translate(0, -largo / 2, 0);
  const borde = new THREE.LineSegments(new THREE.EdgesGeometry(new THREE.ConeGeometry(r, largo, 8, 1, true)), new THREE.LineBasicMaterial({ color, transparent: true, opacity: .5 }));
  borde.geometry.translate(0, -largo / 2, 0);
  const g = new THREE.Group(); g.add(c, borde);
  return g;
}

function autodomo() {
  const g = new THREE.Group(); g.add(poste());
  const brazo = new THREE.Mesh(new THREE.BoxGeometry(1.3, .22, .3), mat(P.blanco)); brazo.position.set(.55, .2, 0); g.add(brazo);
  const cuerpo = new THREE.Mesh(new THREE.CylinderGeometry(.55, .5, .55, 48), mat(P.blanco)); cuerpo.position.set(1.15, -.1, 0); g.add(cuerpo);
  const franja = new THREE.Mesh(new THREE.CylinderGeometry(.56, .56, .06, 48), mat(P.lima)); franja.position.set(1.15, .08, 0); g.add(franja);
  const domo = new THREE.Mesh(new THREE.SphereGeometry(.48, 48, 24, 0, Math.PI * 2, Math.PI / 2, Math.PI / 2), vidrio()); domo.position.set(1.15, -.37, 0); g.add(domo);
  const cabeza = new THREE.Group(); cabeza.position.set(1.15, -.55, 0); g.add(cabeza);
  const l = lente(.12); l.rotation.x = Math.PI / 2; l.position.z = .18; cabeza.add(l);
  const vision = cono(Math.PI / 4, 4.2); vision.rotation.x = -Math.PI / 2; vision.position.z = .25; cabeza.add(vision);
  g.userData.tick = t => { cabeza.rotation.y = Math.sin(t * .6) * 1.4; cabeza.rotation.x = .35 + Math.sin(t * .4) * .15; };
  return g;
}
function lpr() {
  const g = new THREE.Group(); g.add(poste());
  const soporte = new THREE.Mesh(new THREE.CylinderGeometry(.08, .1, .55, 16), mat(P.blanco)); soporte.position.y = .25; g.add(soporte);
  const cuerpo = new THREE.Group(); cuerpo.position.set(0, .6, 0); cuerpo.rotation.x = .22; g.add(cuerpo);
  const caja = new THREE.Mesh(new THREE.BoxGeometry(.6, .5, 1.7), mat(P.blanco)); cuerpo.add(caja);
  const visera = new THREE.Mesh(new THREE.BoxGeometry(.72, .06, 1.95), mat(P.blanco)); visera.position.set(0, .3, .1); cuerpo.add(visera);
  const frente = new THREE.Mesh(new THREE.BoxGeometry(.56, .46, .05), mat(P.oscuro, { roughness: .1 })); frente.position.z = .86; cuerpo.add(frente);
  const l = lente(.12); l.rotation.x = Math.PI / 2; l.position.set(0, .04, .88); cuerpo.add(l);
  for (let i = 0; i < 8; i++) {
    const a = i / 8 * Math.PI * 2, ir = new THREE.Mesh(new THREE.SphereGeometry(.025, 8, 6), new THREE.MeshStandardMaterial({ color: 0x7a1e1e, emissive: 0xb02a2a, emissiveIntensity: .6 }));
    ir.position.set(Math.cos(a) * .19, .04 + Math.sin(a) * .16, .9); cuerpo.add(ir);
  }
  const marca = new THREE.Mesh(new THREE.BoxGeometry(.61, .05, .5), mat(P.lima)); marca.position.set(0, -.12, -.4); cuerpo.add(marca);
  const vision = cono(Math.PI / 9, 6); vision.rotation.x = -Math.PI / 2; vision.position.z = .95; cuerpo.add(vision);
  // placa de vehículo leída
  const placa = new THREE.Mesh(new THREE.PlaneGeometry(.9, .45), new THREE.MeshBasicMaterial({ map: texturaPlaca(), transparent: true }));
  placa.position.set(0, -.6, 6.5); placa.rotation.x = -.2; cuerpo.add(placa);
  g.userData.tick = t => { placa.material.opacity = .55 + .45 * Math.sin(t * 2); };
  return g;
}
function texturaPlaca() {
  const c = document.createElement('canvas'); c.width = 256; c.height = 128; const x = c.getContext('2d');
  x.fillStyle = '#f2d21b'; x.fillRect(0, 0, 256, 128); x.strokeStyle = '#111'; x.lineWidth = 8; x.strokeRect(4, 4, 248, 120);
  x.fillStyle = '#111'; x.font = 'bold 64px sans-serif'; x.textAlign = 'center'; x.fillText('VAL 123', 128, 84);
  x.strokeStyle = '#b5c73a'; x.lineWidth = 6; x.strokeRect(-2, -2, 260, 132);
  return new THREE.CanvasTexture(c);
}
function multisensor() {
  const g = new THREE.Group(); g.add(poste());
  const brazo = new THREE.Mesh(new THREE.CylinderGeometry(.1, .1, .5, 16), mat(P.blanco)); brazo.position.y = .2; g.add(brazo);
  const disco = new THREE.Mesh(new THREE.CylinderGeometry(.85, .95, .35, 64), mat(P.blanco)); disco.position.y = -.1; g.add(disco);
  const aro = new THREE.Mesh(new THREE.TorusGeometry(.9, .03, 8, 64), mat(P.lima)); aro.rotation.x = Math.PI / 2; aro.position.y = .05; g.add(aro);
  const cabezas = new THREE.Group(); cabezas.position.y = -.3; g.add(cabezas);
  for (let i = 0; i < 4; i++) {
    const a = i / 4 * Math.PI * 2, s = new THREE.Group();
    s.position.set(Math.cos(a) * .55, 0, Math.sin(a) * .55); s.rotation.y = -a + Math.PI / 2;
    const cap = new THREE.Mesh(new THREE.SphereGeometry(.24, 24, 12, 0, Math.PI * 2, Math.PI / 2, Math.PI / 2), vidrio()); s.add(cap);
    const l = lente(.08); l.rotation.x = Math.PI / 2 + .5; l.position.set(0, -.08, .12); s.add(l);
    const v = cono(Math.PI / 3, 3.2, i % 2 ? P.lima : 0xd8effb); v.rotation.x = -Math.PI / 2 - .5; v.position.set(0, -.12, .15); s.add(v);
    cabezas.add(s);
  }
  g.userData.tick = t => { cabezas.rotation.y = Math.sin(t * .3) * .2; };
  return g;
}

export function crearVisor(host) {
  const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
  renderer.setPixelRatio(Math.min(devicePixelRatio || 1, 2));
  renderer.toneMapping = THREE.ACESFilmicToneMapping;
  renderer.domElement.setAttribute('aria-hidden', 'true');
  host.prepend(renderer.domElement);
  const escena = new THREE.Scene();
  const camara = new THREE.PerspectiveCamera(36, 1, .1, 100);
  camara.position.set(4.5, 1.8, 6.5);
  const controles = new OrbitControls(camara, renderer.domElement);
  controles.enableDamping = true; controles.enablePan = false; controles.minDistance = 3; controles.maxDistance = 14;
  controles.target.set(.4, -.4, .6); controles.autoRotate = !quieto(); controles.autoRotateSpeed = 1.2;
  controles.addEventListener('start', () => { controles.autoRotate = false; });
  escena.add(new THREE.HemisphereLight(0xffffff, 0x8fa5c0, 2));
  const l = new THREE.DirectionalLight(0xffffff, 2.2); l.position.set(5, 8, 6); escena.add(l);
  const sombra = new THREE.Mesh(new THREE.CircleGeometry(2.5, 48), new THREE.MeshBasicMaterial({ color: 0x1c2d4c, transparent: true, opacity: .08 }));
  sombra.rotation.x = -Math.PI / 2; sombra.position.y = -3.2; escena.add(sombra);
  const modelos = [autodomo(), lpr(), multisensor()];
  modelos.forEach((m, i) => { m.visible = i === 0; escena.add(m); });
  let actual = 0, t = 0, ultimo = performance.now(), visible = true, escala = 1;
  new IntersectionObserver(([e]) => { visible = e.isIntersecting; }).observe(host);
  function redim() { const w = host.clientWidth, h = host.clientHeight; if (!w || !h) return; renderer.setSize(w, h, false); camara.aspect = w / h; camara.updateProjectionMatrix(); }
  new ResizeObserver(redim).observe(host); redim();
  document.addEventListener('vm:movimiento', () => { controles.autoRotate = !quieto(); });
  function cuadro(ahora) {
    const dt = Math.min(.05, (ahora - ultimo) / 1000); ultimo = ahora;
    if (visible && !document.hidden) {
      if (!quieto()) t += dt;
      escala = Math.min(1, escala + dt * 3);
      const m = modelos[actual]; m.scale.setScalar(quieto() ? 1 : .6 + .4 * (1 - Math.pow(1 - escala, 3)));
      m.userData.tick?.(t);
      controles.update(); renderer.render(escena, camara);
    }
    requestAnimationFrame(cuadro);
  }
  requestAnimationFrame(cuadro);
  return { mostrar(i) { if (i === actual) return; modelos[actual].visible = false; actual = i; modelos[i].visible = true; escala = 0; } };
}
