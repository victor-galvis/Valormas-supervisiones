/* ==========================================================================
   Conectividad satelital: escena 3D narrativa
   Valle rural → antena de órbita baja (puntos de información) → constelación y
   enlace → sede educativa conectada. La cámara sigue los pasos del relato y el
   usuario puede girar libremente con el mouse o el dedo.
   ========================================================================== */
import * as THREE from '../vendor/three.module.min.js';
import { OrbitControls } from '../vendor/OrbitControls.js';

const doc = document.documentElement;
const quieto = () => doc.dataset.motion === 'reduce' || doc.dataset.paused === 'true';
const P = { marino: 0x1c2d4c, lima: 0xb5c73a, verde: 0x194a2b, verde2: 0x2a6a3f, celeste: 0xd8effb, blanco: 0xf5f8f6 };
const mat = (color, o = {}) => new THREE.MeshStandardMaterial({ color, roughness: .55, metalness: .05, ...o });

function ruido(x, z) {
  return Math.sin(x * .09) * 3.2 + Math.cos(z * .07) * 3 + Math.sin((x + z) * .05) * 4 + Math.sin(x * .23 + z * .17) * 1.2;
}

export function crearEscenaAntena(host, pasos) {
  const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
  renderer.setPixelRatio(Math.min(devicePixelRatio || 1, 2));
  renderer.toneMapping = THREE.ACESFilmicToneMapping;
  renderer.domElement.setAttribute('aria-hidden', 'true');
  host.prepend(renderer.domElement);
  const escena = new THREE.Scene();
  escena.fog = new THREE.Fog(0x16243f, 60, 160);
  const camara = new THREE.PerspectiveCamera(40, 1, .1, 400);
  const controles = new OrbitControls(camara, renderer.domElement);
  controles.enableDamping = true; controles.enablePan = false; controles.minDistance = 4; controles.maxDistance = 90; controles.maxPolarAngle = 1.45;

  escena.add(new THREE.HemisphereLight(0xe8f4ff, 0x1d3a26, 1.5));
  const sol = new THREE.DirectionalLight(0xffffff, 2.4); sol.position.set(30, 50, 20); escena.add(sol);

  // terreno montañoso (Antioquia rural)
  const tg = new THREE.PlaneGeometry(160, 160, 120, 120); tg.rotateX(-Math.PI / 2);
  const pos = tg.attributes.position, colores = [];
  const cBajo = new THREE.Color(0x2a6a3f), cMedio = new THREE.Color(0x4f9a61), cAlto = new THREE.Color(0x8fbf9b);
  for (let i = 0; i < pos.count; i++) {
    const x = pos.getX(i), z = pos.getZ(i), d = Math.hypot(x, z);
    let h = ruido(x, z) + Math.max(0, (d - 18)) * .22;
    h *= Math.min(1, Math.max(0, (d - 9) / 14));
    pos.setY(i, h);
    const k = Math.min(1, Math.max(0, (h + 2) / 18));
    const c = k < .5 ? cBajo.clone().lerp(cMedio, k * 2) : cMedio.clone().lerp(cAlto, (k - .5) * 2);
    colores.push(c.r, c.g, c.b);
  }
  tg.setAttribute('color', new THREE.Float32BufferAttribute(colores, 3));
  tg.computeVertexNormals();
  escena.add(new THREE.Mesh(tg, new THREE.MeshStandardMaterial({ vertexColors: true, flatShading: true, roughness: .9 })));

  // árboles
  const nArb = 420, arb = new THREE.InstancedMesh(new THREE.ConeGeometry(.7, 2.2, 6), mat(P.verde, { flatShading: true }), nArb);
  const m4 = new THREE.Matrix4(), q = new THREE.Quaternion(), s = new THREE.Vector3();
  for (let i = 0, k = 0; k < nArb && i < 5000; i++) {
    const x = (Math.random() - .5) * 140, z = (Math.random() - .5) * 140, d = Math.hypot(x, z);
    if (d < 11) continue;
    const h = ruido(x, z) + Math.max(0, d - 18) * .22, esc = .7 + Math.random() * .9;
    m4.compose(new THREE.Vector3(x, h * Math.min(1, (d - 9) / 14) + 1 * esc, z), q, s.set(esc, esc, esc));
    arb.setMatrixAt(k++, m4);
  }
  escena.add(arb);

  // sede educativa rural
  const sede = new THREE.Group(); escena.add(sede);
  const muros = new THREE.Mesh(new THREE.BoxGeometry(9, 3, 5), mat(P.blanco)); muros.position.y = 1.5; sede.add(muros);
  const zocalo = new THREE.Mesh(new THREE.BoxGeometry(9.06, .7, 5.06), mat(P.verde2)); zocalo.position.y = .35; sede.add(zocalo);
  const perfil = new THREE.Shape([new THREE.Vector2(-3, 0), new THREE.Vector2(3, 0), new THREE.Vector2(0, 1.9)]);
  const techoG = new THREE.ExtrudeGeometry(perfil, { depth: 9.8, bevelEnabled: false }); techoG.translate(0, 0, -4.9); techoG.rotateY(Math.PI / 2);
  const techo = new THREE.Mesh(techoG, mat(P.verde, { flatShading: true })); techo.position.y = 3; sede.add(techo);
  const puerta = new THREE.Mesh(new THREE.BoxGeometry(1.2, 2, .1), mat(P.marino)); puerta.position.set(-2.5, 1, 2.52); sede.add(puerta);
  [0, 2.4].forEach(x => { const v = new THREE.Mesh(new THREE.BoxGeometry(1.5, 1, .1), mat(P.celeste, { emissive: 0xd8effb, emissiveIntensity: .25 })); v.position.set(x, 1.8, 2.52); sede.add(v); });
  const aviso = new THREE.Mesh(new THREE.BoxGeometry(3, .6, .08), mat(P.lima)); aviso.position.set(1.2, 2.75, 2.56); sede.add(aviso);
  const asta = new THREE.Mesh(new THREE.CylinderGeometry(.05, .05, 5), mat(0xcfd6dc, { metalness: .6 })); asta.position.set(-6.2, 2.5, 3); sede.add(asta);
  const bandera = new THREE.Mesh(new THREE.PlaneGeometry(1.4, .9), mat(P.lima, { side: THREE.DoubleSide })); bandera.position.set(-5.5, 4.4, 3); sede.add(bandera);

  // antena satelital de órbita baja sobre mástil
  const antena = new THREE.Group(); antena.position.set(2.6, 5.15, -.6); sede.add(antena);
  const mastil = new THREE.Mesh(new THREE.CylinderGeometry(.07, .07, 1.6, 16), mat(0xcfd6dc, { metalness: .7, roughness: .3 })); mastil.position.y = .8; antena.add(mastil);
  const cabeza = new THREE.Group(); cabeza.position.y = 1.6; antena.add(cabeza);
  const rr = new THREE.Shape(), w = 1.25, h = .78, r = .12;
  rr.moveTo(-w / 2 + r, -h / 2); rr.lineTo(w / 2 - r, -h / 2); rr.quadraticCurveTo(w / 2, -h / 2, w / 2, -h / 2 + r); rr.lineTo(w / 2, h / 2 - r); rr.quadraticCurveTo(w / 2, h / 2, w / 2 - r, h / 2);
  rr.lineTo(-w / 2 + r, h / 2); rr.quadraticCurveTo(-w / 2, h / 2, -w / 2, h / 2 - r); rr.lineTo(-w / 2, -h / 2 + r); rr.quadraticCurveTo(-w / 2, -h / 2, -w / 2 + r, -h / 2);
  const placaG = new THREE.ExtrudeGeometry(rr, { depth: .06, bevelEnabled: true, bevelThickness: .02, bevelSize: .02, bevelSegments: 4 });
  const placa = new THREE.Mesh(placaG, [mat(0xffffff, { roughness: .25 }), mat(0xd9dee3, { roughness: .4 })]);
  placa.rotation.x = -Math.PI / 2 + .55; // mirando al cielo, levemente al sur
  cabeza.add(placa);
  const brazo = new THREE.Mesh(new THREE.BoxGeometry(.12, .5, .12), mat(0x9aa4ad, { metalness: .5 })); brazo.position.set(0, -.15, .05); brazo.rotation.x = .5; cabeza.add(brazo);
  // cable de datos y energía hasta el router
  const router = new THREE.Group(); router.position.set(3.9, 1.6, 2.6); sede.add(router);
  const caja = new THREE.Mesh(new THREE.BoxGeometry(.7, .45, .22), mat(0xffffff, { roughness: .3 })); router.add(caja);
  const led = new THREE.Mesh(new THREE.SphereGeometry(.045, 12, 8), new THREE.MeshStandardMaterial({ color: P.lima, emissive: P.lima, emissiveIntensity: 1 })); led.position.set(.22, .1, .12); router.add(led);
  const ruta = new THREE.CatmullRomCurve3([new THREE.Vector3(2.6, 6.5, -.6), new THREE.Vector3(2.6, 5.2, -.6), new THREE.Vector3(3.2, 4.6, .6), new THREE.Vector3(4.55, 3.2, 2.1), new THREE.Vector3(4.55, 2, 2.6), new THREE.Vector3(4.1, 1.6, 2.65)]);
  sede.add(new THREE.Mesh(new THREE.TubeGeometry(ruta, 60, .035, 8), mat(0x1a1d22, { roughness: .6 })));

  // ondas Wi‑Fi alrededor de la sede
  const ondas = [0, 1, 2].map(i => {
    const o = new THREE.Mesh(new THREE.TorusGeometry(1, .04, 8, 64), new THREE.MeshBasicMaterial({ color: P.lima, transparent: true, opacity: 0 }));
    o.rotation.x = Math.PI / 2; o.position.set(3.9, 1.7, 2.6); o.userData.f = i / 3; escena.add(o); return o;
  });

  // constelación de satélites en órbita baja
  const panelTex = (() => {
    const c = document.createElement('canvas'); c.width = 128; c.height = 64; const g = c.getContext('2d');
    g.fillStyle = '#1c2d4c'; g.fillRect(0, 0, 128, 64); g.strokeStyle = 'rgba(216,239,251,.55)'; g.lineWidth = 2;
    for (let i = 1; i < 8; i++) { g.beginPath(); g.moveTo(i * 16, 0); g.lineTo(i * 16, 64); g.stroke(); }
    g.beginPath(); g.moveTo(0, 32); g.lineTo(128, 32); g.stroke();
    return new THREE.CanvasTexture(c);
  })();
  const sats = [];
  for (let i = 0; i < 7; i++) {
    const g = new THREE.Group();
    g.add(new THREE.Mesh(new THREE.BoxGeometry(1.6, .35, .9), mat(0xe9edf1, { metalness: .4, roughness: .3 })));
    const pan = new THREE.Mesh(new THREE.BoxGeometry(4.2, .05, 1.5), [mat(0x2a3d61), mat(0x2a3d61), new THREE.MeshStandardMaterial({ map: panelTex, roughness: .3, metalness: .4 }), mat(0x2a3d61), mat(0x2a3d61), mat(0x2a3d61)]);
    pan.position.x = 2.9; g.add(pan);
    const luz = new THREE.Mesh(new THREE.SphereGeometry(.12, 12, 8), new THREE.MeshBasicMaterial({ color: P.lima })); luz.position.set(-.9, 0, 0); g.add(luz);
    g.scale.setScalar(1.8);
    g.userData = { x: -90 + i * 30, z: -8 + (i % 3) * 6, y: 40 + (i % 2) * 4 };
    escena.add(g); sats.push(g);
  }
  const hazG = new THREE.BufferGeometry().setFromPoints([new THREE.Vector3(), new THREE.Vector3()]);
  const haz = new THREE.Line(hazG, new THREE.LineDashedMaterial({ color: P.lima, dashSize: 1.2, gapSize: .8, transparent: true, opacity: .95 }));
  escena.add(haz);
  const pulso = new THREE.Mesh(new THREE.SphereGeometry(.28, 16, 12), new THREE.MeshBasicMaterial({ color: P.lima })); escena.add(pulso);
  const orbitaTrazo = new THREE.Mesh(new THREE.TorusGeometry(140, .06, 6, 240, Math.PI / 2.2), new THREE.MeshBasicMaterial({ color: P.celeste, transparent: true, opacity: .25 }));
  orbitaTrazo.rotation.set(0, Math.PI / 2, 0); orbitaTrazo.position.set(0, -92, 0); escena.add(orbitaTrazo);

  // puntos de información (hotspots) sobre la antena
  const puntos = [
    { id: 'hs-placa', ancla: new THREE.Vector3(2.6, 6.95, -.55), t: 'Antena de órbita baja', d: 'Panel electrónico que apunta al cielo y se conecta a satélites que orbitan a unos 550 km, mucho más cerca que los satélites tradicionales: menos latencia para clases y videollamadas.' },
    { id: 'hs-mastil', ancla: new THREE.Vector3(2.6, 5.6, -.6), t: 'Mástil y orientación', d: 'Se instala sobre el techo, con vista despejada al cielo. El equipo se autoorienta y no requiere ajustes manuales.' },
    { id: 'hs-cable', ancla: new THREE.Vector3(4.55, 2.9, 2.2), t: 'Cable de datos y energía', d: 'Un único cable lleva datos y energía entre la antena y el router, protegido contra la intemperie.' },
    { id: 'hs-router', ancla: new THREE.Vector3(3.9, 1.6, 2.75), t: 'Router Wi‑Fi de la sede', d: 'Distribuye internet a las aulas. Valor+ gestiona la instalación, el soporte técnico y el monitoreo del servicio.' },
  ];
  const capaHS = document.createElement('div'); capaHS.className = 'capa-hotspots'; host.append(capaHS);
  const globo = document.createElement('div'); globo.className = 'globo'; globo.id = 'globo-antena'; globo.hidden = true; globo.setAttribute('role', 'region'); globo.setAttribute('aria-live', 'polite'); host.append(globo);
  puntos.forEach((p, i) => {
    const b = document.createElement('button'); b.type = 'button'; b.className = 'hotspot'; b.textContent = i + 1;
    b.setAttribute('aria-label', `Punto ${i + 1}: ${p.t}`); b.setAttribute('aria-expanded', 'false'); b.setAttribute('aria-controls', 'globo-antena');
    b.addEventListener('click', () => {
      const abierto = b.getAttribute('aria-expanded') === 'true';
      puntos.forEach(x => x.boton.setAttribute('aria-expanded', 'false'));
      if (abierto) { globo.hidden = true; return; }
      b.setAttribute('aria-expanded', 'true');
      globo.innerHTML = `<h4>${p.t}</h4><p>${p.d}</p>`; globo.hidden = false; globo.dataset.de = i;
    });
    p.boton = b; capaHS.append(b);
  });

  // pasos de cámara
  const tomas = [
    { cam: [34, 24, 40], obj: [0, 3, 0] },
    { cam: [10.5, 6.8, 11], obj: [3.2, 4.1, .9] },
    { cam: [-34, 8, 50], obj: [2, 26, -2] },
    { cam: [13, 5.5, 15], obj: [1, 2, 1] },
  ];
  let paso = 0, vuelo = null, usuario = false;
  camara.position.set(...tomas[0].cam); controles.target.set(...tomas[0].obj);
  controles.addEventListener('start', () => { usuario = true; vuelo = null; });
  function irA(i) {
    paso = i; usuario = false;
    const t = tomas[i];
    vuelo = { k: quieto() ? 1 : 0, de: [camara.position.clone(), controles.target.clone()], a: [new THREE.Vector3(...t.cam), new THREE.Vector3(...t.obj)] };
    capaHS.style.opacity = i === 1 ? '1' : '0';
    capaHS.style.pointerEvents = i === 1 ? 'auto' : 'none';
    puntos.forEach(p => { p.boton.tabIndex = i === 1 ? 0 : -1; });
    if (i !== 1) globo.hidden = true;
  }
  const io = new IntersectionObserver(es => es.forEach(e => { if (e.isIntersecting) irA(+e.target.dataset.paso); }), { rootMargin: '-45% 0px -45% 0px' });
  pasos.forEach(p => io.observe(p));
  irA(0);

  // bucle
  let visible = true, t = 0, ultimo = performance.now();
  new IntersectionObserver(([e]) => { visible = e.isIntersecting; }).observe(host);
  function redim() { const w = host.clientWidth, h = host.clientHeight; if (!w || !h) return; renderer.setSize(w, h, false); camara.aspect = w / h; camara.updateProjectionMatrix(); }
  new ResizeObserver(redim).observe(host); redim();
  const v = new THREE.Vector3(), dish = new THREE.Vector3(2.6, 6.8, -.6);
  function cuadro(ahora) {
    const dt = Math.min(.05, (ahora - ultimo) / 1000); ultimo = ahora;
    if (visible && !document.hidden) {
      if (!quieto()) t += dt;
      if (vuelo) {
        vuelo.k = Math.min(1, vuelo.k + dt / 1.4);
        const e = 1 - Math.pow(1 - vuelo.k, 3);
        camara.position.lerpVectors(vuelo.de[0], vuelo.a[0], e); controles.target.lerpVectors(vuelo.de[1], vuelo.a[1], e);
        if (vuelo.k >= 1) vuelo = null;
      } else if (!usuario && !quieto() && paso !== 1) {
        // deriva suave de la cámara mientras se lee
        const off = new THREE.Vector3(...tomas[paso].cam).sub(controles.target).applyAxisAngle(new THREE.Vector3(0, 1, 0), Math.sin(t * .15) * .12);
        camara.position.copy(controles.target).add(off);
      }
      // satélites cruzando el cielo
      let cercano = null, dmin = 1e9;
      sats.forEach(g => {
        const u = g.userData; u.x += dt * 4.5; if (u.x > 105) u.x -= 210;
        g.position.set(u.x, u.y - Math.abs(u.x) * .08, u.z); g.rotation.z = -u.x * .002;
        const d = Math.abs(u.x - 2.6); if (d < dmin) { dmin = d; cercano = g; }
      });
      const enlace = paso >= 2;
      haz.visible = pulso.visible = enlace && !!cercano;
      if (cercano) {
        hazG.attributes.position.setXYZ(0, cercano.position.x, cercano.position.y, cercano.position.z);
        hazG.attributes.position.setXYZ(1, dish.x, dish.y, dish.z); hazG.attributes.position.needsUpdate = true;
        haz.computeLineDistances(); haz.material.dashOffset = -t * 6;
        const k = (t * .6) % 1; pulso.position.lerpVectors(cercano.position, dish, k);
      }
      ondas.forEach(o => {
        const k = (t * .5 + o.userData.f) % 1;
        o.scale.setScalar(1 + k * 9); o.material.opacity = paso === 3 ? (1 - k) * .8 : 0;
      });
      led.material.emissiveIntensity = .5 + .5 * Math.sin(t * 6);
      bandera.rotation.y = Math.sin(t * 2) * .2;
      controles.update();
      renderer.render(escena, camara);
      // ubicar los puntos de información sobre la pantalla
      if (paso === 1) {
        const r = host.getBoundingClientRect();
        puntos.forEach(p => {
          v.copy(p.ancla).project(camara);
          p.boton.style.left = ((v.x + 1) / 2 * r.width) + 'px'; p.boton.style.top = ((1 - v.y) / 2 * r.height) + 'px';
        });
        if (!globo.hidden) {
          const b = puntos[+globo.dataset.de].boton;
          const x = parseFloat(b.style.left), y = parseFloat(b.style.top);
          globo.style.left = Math.min(x, r.width - 320) + 'px'; globo.style.top = Math.max(110, y) + 'px';
        }
      }
    }
    requestAnimationFrame(cuadro);
  }
  requestAnimationFrame(cuadro);
  return { irA };
}
