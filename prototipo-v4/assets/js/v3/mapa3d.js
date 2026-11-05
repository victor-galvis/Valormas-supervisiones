/* ==========================================================================
   Mapa 3D interactivo de Antioquia (125 municipios, límites base DANE simplificados)
   Capas: todos · conectividad · seguridad. Rotar, acercar, pasar el cursor y elegir.
   API: const mapa = crearMapa(host, opciones)
        mapa.capa('conectividad') · mapa.seleccionar(codigo) · mapa.enfocar(codigo|null)
        host emite 'vm:municipio' { detail: { m, con, seg } }
   ========================================================================== */
import * as THREE from '../vendor/three.module.min.js';
import { OrbitControls } from '../vendor/OrbitControls.js';
import GEO from '../../data/antioquia.js';
import DATOS from '../../data/proyectos.js';

const doc = document.documentElement;
const quieto = () => doc.dataset.motion === 'reduce' || doc.dataset.paused === 'true';
export const MUNICIPIOS = GEO.municipios;
export const SUBREGIONES = GEO.meta.subregiones;
export { DATOS };

const PALETA_SUB = {
  'Valle de Aburrá': '#b5c73a', 'Oriente': '#7fb069', 'Suroeste': '#4f9a61', 'Occidente': '#2f7a4b', 'Norte': '#3f8f7a',
  'Nordeste': '#6aa6a0', 'Magdalena Medio': '#8cc2c9', 'Bajo Cauca': '#a9d3e6', 'Urabá': '#5f8fb0',
};
const C = { marino: 0x1c2d4c, lima: 0xb5c73a, celeste: 0xd8effb, verde: 0x2a6a3f, apagado: 0x2a3d61 };

const [X0, Y0, X1, Y1] = GEO.meta.bbox;
const LON0 = (X0 + X1) / 2, LAT0 = (Y0 + Y1) / 2, K = 9, COS = Math.cos(LAT0 * Math.PI / 180);
export const proyectar = (lon, lat) => [(lon - LON0) * K * COS, (lat - LAT0) * K];

const con = DATOS.conectividad.municipios, seg = DATOS.seguridad.municipios;
const maxCon = Math.max(...Object.values(con).map(v => v.s)), maxSeg = Math.max(...Object.values(seg));
// escala de color por percentil: reparte los tonos aunque los valores sean parecidos
const percentil = valores => { const o = [...valores].filter(v => v > 0).sort((a, b) => a - b); return v => o.length > 1 ? o.indexOf(v) / (o.length - 1) : 1; };
const pctCon = percentil(Object.values(con).map(v => v.s)), pctSeg = percentil(Object.values(seg));

function texturaPunto() {
  const c = document.createElement('canvas'); c.width = c.height = 64;
  const g = c.getContext('2d'), gr = g.createRadialGradient(32, 32, 0, 32, 32, 32);
  gr.addColorStop(0, 'rgba(255,255,255,1)'); gr.addColorStop(.35, 'rgba(255,255,255,.9)'); gr.addColorStop(.5, 'rgba(255,255,255,.25)'); gr.addColorStop(1, 'rgba(255,255,255,0)');
  g.fillStyle = gr; g.fillRect(0, 0, 64, 64);
  return new THREE.CanvasTexture(c);
}

export function crearMapa(host, op = {}) {
  const opciones = { capa: 'todos', autoRotar: true, distancia: 46, ...op };
  const ancho = () => host.clientWidth, alto = () => host.clientHeight;
  const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
  renderer.setPixelRatio(Math.min(devicePixelRatio || 1, 2));
  renderer.toneMapping = THREE.ACESFilmicToneMapping;
  renderer.domElement.setAttribute('aria-hidden', 'true');
  host.prepend(renderer.domElement);
  const escena = new THREE.Scene();
  const camara = new THREE.PerspectiveCamera(34, 1, .1, 500);
  camara.position.set(0, opciones.distancia * .78, opciones.distancia * .62);
  const controles = new OrbitControls(camara, renderer.domElement);
  controles.enableDamping = true; controles.dampingFactor = .07;
  controles.enablePan = false; controles.minDistance = 14; controles.maxDistance = 80;
  controles.minPolarAngle = .15; controles.maxPolarAngle = 1.2;
  controles.autoRotateSpeed = .45;
  controles.autoRotate = opciones.autoRotar && !quieto();
  controles.addEventListener('start', () => { controles.autoRotate = false; });

  escena.add(new THREE.HemisphereLight(0xffffff, 0x1c2d4c, 1.6));
  const sol = new THREE.DirectionalLight(0xffffff, 2); sol.position.set(12, 30, 18); escena.add(sol);
  const contra = new THREE.DirectionalLight(0xb5c73a, .7); contra.position.set(-20, 10, -20); escena.add(contra);

  // halo bajo el mapa
  const brillo = new THREE.Mesh(new THREE.CircleGeometry(24, 64), new THREE.MeshBasicMaterial({ map: texturaPunto(), color: 0x3d5f8f, transparent: true, opacity: .45, depthWrite: false }));
  brillo.rotation.x = -Math.PI / 2; brillo.position.y = -.05; escena.add(brillo);

  // municipios en relieve
  const grupo = new THREE.Group(); escena.add(grupo);
  const piezas = MUNICIPIOS.map(m => {
    const pts = m.p.map(([lon, lat]) => new THREE.Vector2(...proyectar(lon, lat)));
    const forma = new THREE.Shape(pts);
    const geo = new THREE.ExtrudeGeometry(forma, { depth: 1, bevelEnabled: false });
    geo.rotateX(-Math.PI / 2);
    const tapa = new THREE.MeshStandardMaterial({ color: PALETA_SUB[m.r], roughness: .6, metalness: .05 });
    const lado = new THREE.MeshStandardMaterial({ color: new THREE.Color(PALETA_SUB[m.r]).multiplyScalar(.55), roughness: .8 });
    const malla = new THREE.Mesh(geo, [tapa, lado]);
    malla.scale.y = .3;
    const borde = new THREE.LineLoop(new THREE.BufferGeometry().setFromPoints(pts.map(p => new THREE.Vector3(p.x, 1.002, -p.y))), new THREE.LineBasicMaterial({ color: 0xffffff, transparent: true, opacity: .35 }));
    malla.add(borde);
    malla.userData = { m, alto: .3, color: new THREE.Color(PALETA_SUB[m.r]) };
    grupo.add(malla);
    const [cx, cz] = proyectar(m.cx, m.cy);
    return { m, malla, tapa, lado, centro: new THREE.Vector3(cx, 0, -cz) };
  });
  const porCodigo = Object.fromEntries(piezas.map(p => [p.m.c, p]));

  // puntos de conectividad (sedes) y de cámaras con un shader de pulso
  const tex = texturaPunto();
  const puntosMat = color => new THREE.ShaderMaterial({
    transparent: true, depthWrite: false, blending: THREE.NormalBlending,
    uniforms: { uT: { value: 0 }, uMapa: { value: tex }, uColor: { value: new THREE.Color(color) }, uEsc: { value: renderer.getPixelRatio() } },
    vertexShader: `attribute float tam; attribute float fase; uniform float uT; uniform float uEsc; varying float vA;
      void main(){ vec4 mv = modelViewMatrix * vec4(position,1.); float p = .85 + .15*sin(uT*2.2 + fase);
        gl_PointSize = tam * p * uEsc * (60. / -mv.z); vA = 1.; gl_Position = projectionMatrix * mv; }`,
    fragmentShader: `uniform sampler2D uMapa; uniform vec3 uColor; varying float vA;
      void main(){ vec4 t = texture2D(uMapa, gl_PointCoord); gl_FragColor = vec4(uColor, t.a * vA); }`,
  });
  function capaPuntos(datos, valor, color, maxV) {
    const lista = piezas.filter(p => valor(datos[p.m.c]) > 0);
    const pos = new Float32Array(lista.length * 3), tam = new Float32Array(lista.length), fase = new Float32Array(lista.length);
    lista.forEach((p, i) => { pos.set([p.centro.x, 0, p.centro.z], i * 3); tam[i] = 5 + 12 * Math.sqrt(valor(datos[p.m.c]) / maxV); fase[i] = i * 1.7; });
    const g = new THREE.BufferGeometry();
    g.setAttribute('position', new THREE.BufferAttribute(pos, 3)); g.setAttribute('tam', new THREE.BufferAttribute(tam, 1)); g.setAttribute('fase', new THREE.BufferAttribute(fase, 1));
    const pts = new THREE.Points(g, puntosMat(color));
    pts.userData.lista = lista; pts.renderOrder = 5;
    escena.add(pts);
    return pts;
  }
  const puntosCon = capaPuntos(con, v => v ? v.s : 0, C.lima, maxCon);
  const puntosSeg = capaPuntos(seg, v => v || 0, C.celeste, maxSeg);

  // nodos de seguridad y arcos de datos hacia el nodo departamental
  const nodosG = new THREE.Group(); escena.add(nodosG);
  const nodos = DATOS.seguridad.nodos.map(n => {
    const p = porCodigo[n.c], dep = n.t === 'departamental', operando = n.e === 'operando';
    const color = operando ? C.lima : C.celeste;
    const anillo = new THREE.Mesh(new THREE.TorusGeometry(dep ? 1.1 : .7, .07, 12, 48), new THREE.MeshBasicMaterial({ color, transparent: true, opacity: .95 }));
    anillo.rotation.x = Math.PI / 2;
    const haz = new THREE.Mesh(new THREE.CylinderGeometry(.06, .06, dep ? 6 : 3.5, 12, 1, true), new THREE.MeshBasicMaterial({ color, transparent: true, opacity: .6 }));
    const g = new THREE.Group(); g.add(anillo, haz); g.userData = { p, dep, haz, anillo };
    nodosG.add(g);
    return { n, g, p };
  });
  const hub = porCodigo[DATOS.seguridad.nodos[0].c];
  const arcosMat = new THREE.ShaderMaterial({
    transparent: true, depthWrite: false,
    uniforms: { uT: { value: 0 }, uColor: { value: new THREE.Color(C.lima) } },
    vertexShader: `varying float vU; void main(){ vU = uv.x; gl_Position = projectionMatrix * modelViewMatrix * vec4(position,1.); }`,
    fragmentShader: `uniform float uT; uniform vec3 uColor; varying float vU;
      void main(){ float f = fract(vU - uT * .35); float a = .3 + .7 * smoothstep(.8, 1., f); gl_FragColor = vec4(mix(uColor, vec3(1.), smoothstep(.95, 1., f) * .6), a); }`,
  });
  const arcosG = new THREE.Group(); escena.add(arcosG);
  const subNodo = {};
  nodos.forEach(({ n, p }) => { if (n.t === 'subregional' && n.e === 'operando') subNodo[p.m.r] = p; });
  Object.keys(seg).forEach(c => {
    const p = porCodigo[c]; if (!p || p === hub) return;
    const destino = (subNodo[p.m.r] && subNodo[p.m.r] !== p) ? subNodo[p.m.r] : hub;
    arcosG.add(arco(p.centro, destino.centro, .9));
  });
  Object.values(subNodo).forEach(p => arcosG.add(arco(p.centro, hub.centro, 2.2)));
  function arco(a, b, h) {
    const medio = a.clone().lerp(b, .5); medio.y = h + a.distanceTo(b) * .18;
    const curva = new THREE.QuadraticBezierCurve3(a.clone().setY(.6), medio, b.clone().setY(.6));
    return new THREE.Mesh(new THREE.TubeGeometry(curva, 48, h > 1.5 ? .07 : .045, 6, false), arcosMat);
  }

  // estado de capa
  let capaActual = null, seleccion = null, hover = null;
  function capa(nombre) {
    capaActual = nombre;
    piezas.forEach(p => {
      const c = con[p.m.c], s = seg[p.m.c] || 0;
      let alto = .3, color = new THREE.Color(PALETA_SUB[p.m.r]);
      if (nombre === 'conectividad') {
        alto = c ? .3 + 2.4 * c.s / maxCon : .15;
        color = c ? new THREE.Color(0x1f4f33).lerp(new THREE.Color(C.lima), pctCon(c.s)) : new THREE.Color(C.apagado);
      } else if (nombre === 'seguridad') {
        alto = s ? .3 + 2.4 * s / maxSeg : .15;
        color = s ? new THREE.Color(0x35607e).lerp(new THREE.Color(C.celeste), pctSeg(s)) : new THREE.Color(C.apagado);
      }
      p.malla.userData.alto = alto; p.malla.userData.color = color;
    });
    puntosCon.visible = nombre !== 'seguridad';
    puntosSeg.visible = nombre === 'seguridad' || nombre === 'todos';
    nodosG.visible = arcosG.visible = nombre === 'seguridad' || (nombre === 'todos' && opciones.arcosEnTodos);
    pedirRender();
  }

  // interacción
  const ray = new THREE.Raycaster(), ndc = new THREE.Vector2();
  const tip = document.createElement('div'); tip.className = 'tooltip-3d'; tip.setAttribute('aria-hidden', 'true'); host.append(tip);
  function picar(e) {
    const r = renderer.domElement.getBoundingClientRect();
    ndc.set((e.clientX - r.left) / r.width * 2 - 1, -((e.clientY - r.top) / r.height) * 2 + 1);
    ray.setFromCamera(ndc, camara);
    const hit = ray.intersectObjects(grupo.children, false)[0];
    return hit ? hit.object : null;
  }
  function texto(m) {
    const c = con[m.c], s = seg[m.c] || 0;
    const lin = [];
    if (capaActual !== 'seguridad') lin.push(`${c ? c.s : 0} sedes conectadas`);
    if (capaActual !== 'conectividad') lin.push(`${s} cámaras integradas`);
    return `<strong>${m.n}</strong>${m.r} · ${lin.join(' · ')}`;
  }
  renderer.domElement.addEventListener('pointermove', e => {
    const o = picar(e);
    if (o !== hover) { hover = o; pedirRender(); }
    if (o) {
      const r = host.getBoundingClientRect();
      tip.innerHTML = texto(o.userData.m); tip.style.left = (e.clientX - r.left) + 'px'; tip.style.top = (e.clientY - r.top) + 'px';
      tip.classList.add('visible'); renderer.domElement.style.cursor = 'pointer';
    } else { tip.classList.remove('visible'); renderer.domElement.style.cursor = ''; }
  });
  renderer.domElement.addEventListener('pointerleave', () => { hover = null; tip.classList.remove('visible'); pedirRender(); });
  let abajo = null;
  renderer.domElement.addEventListener('pointerdown', e => { abajo = [e.clientX, e.clientY]; });
  renderer.domElement.addEventListener('pointerup', e => {
    if (!abajo || Math.hypot(e.clientX - abajo[0], e.clientY - abajo[1]) > 6) return;
    const o = picar(e); if (o) seleccionar(o.userData.m.c, true);
  });
  function seleccionar(codigo, enfocarla = false) {
    seleccion = porCodigo[codigo] || null;
    if (seleccion) {
      host.dispatchEvent(new CustomEvent('vm:municipio', { detail: { m: seleccion.m, con: con[codigo] || null, seg: seg[codigo] || 0 }, bubbles: true }));
      if (enfocarla) enfocar(codigo);
    }
    pedirRender();
  }
  let vuelo = null;
  function enfocar(codigo, dist = 26) {
    const p = codigo ? porCodigo[codigo] : null;
    const objetivo = p ? p.centro.clone() : new THREE.Vector3();
    const dir = camara.position.clone().sub(controles.target).normalize();
    const destinoCam = objetivo.clone().add(dir.multiplyScalar(p ? dist : opciones.distancia));
    vuelo = { t: 0, de: [controles.target.clone(), camara.position.clone()], a: [objetivo, destinoCam] };
    controles.autoRotate = false;
    pedirRender();
  }

  // bucle
  let visible = true, sucio = true, reloj = 0, ultimo = performance.now();
  const pedirRender = () => { sucio = true; };
  new IntersectionObserver(([e]) => { visible = e.isIntersecting; }).observe(host);
  controles.addEventListener('change', pedirRender);
  ['vm:movimiento', 'vm:pausa'].forEach(ev => document.addEventListener(ev, () => { controles.autoRotate = opciones.autoRotar && !quieto(); pedirRender(); }));
  function redimensionar() {
    const w = ancho(), h = alto(); if (!w || !h) return;
    renderer.setSize(w, h, false); camara.aspect = w / h;
    camara.fov = w / h < .9 ? 46 : 34; camara.updateProjectionMatrix(); pedirRender();
  }
  new ResizeObserver(redimensionar).observe(host); redimensionar();
  const tmp = new THREE.Color();
  function cuadro(ahora) {
    const dt = Math.min(.05, (ahora - ultimo) / 1000); ultimo = ahora;
    if (visible && !document.hidden) {
      const animar = !quieto();
      if (animar) reloj += dt;
      let moviendo = false;
      piezas.forEach(p => {
        const u = p.malla.userData, objetivo = u.alto * (p === seleccion ? 1.25 : 1);
        if (Math.abs(p.malla.scale.y - objetivo) > .002) { p.malla.scale.y = animar ? p.malla.scale.y + (objetivo - p.malla.scale.y) * .12 : objetivo; moviendo = true; }
        tmp.copy(u.color); if (p.malla === hover) tmp.lerp(new THREE.Color(0xffffff), .35); if (p === seleccion) tmp.set(0xffffff);
        if (!p.tapa.color.equals(tmp)) { p.tapa.color.lerp(tmp, animar ? .2 : 1); p.lado.color.copy(p.tapa.color).multiplyScalar(.55); moviendo = true; }
      });
      [puntosCon, puntosSeg].forEach(pt => {
        const pos = pt.geometry.attributes.position;
        pt.userData.lista.forEach((p, i) => pos.setY(i, p.malla.scale.y + .25));
        pos.needsUpdate = true; pt.material.uniforms.uT.value = reloj;
      });
      nodos.forEach(({ g, p }) => { g.position.set(p.centro.x, p.malla.scale.y + .05, p.centro.z); g.userData.haz.position.y = g.userData.haz.geometry.parameters.height / 2; g.userData.anillo.scale.setScalar(1 + .12 * Math.sin(reloj * 2.5)); });
      arcosMat.uniforms.uT.value = reloj;
      if (vuelo) {
        vuelo.t = Math.min(1, vuelo.t + (animar ? dt / 1.1 : 1));
        const k = 1 - Math.pow(1 - vuelo.t, 3);
        controles.target.lerpVectors(vuelo.de[0], vuelo.a[0], k); camara.position.lerpVectors(vuelo.de[1], vuelo.a[1], k);
        if (vuelo.t >= 1) vuelo = null;
        moviendo = true;
      }
      controles.update();
      if (sucio || moviendo || animar) { renderer.render(escena, camara); sucio = false; }
    }
    requestAnimationFrame(cuadro);
  }
  capa(opciones.capa);
  requestAnimationFrame(cuadro);

  return {
    capa, seleccionar, enfocar, porCodigo, camara, controles,
    girar(v) { controles.autoRotate = v && !quieto(); },
    acercar(f) { const d = camara.position.clone().sub(controles.target).multiplyScalar(f); camara.position.copy(controles.target).add(d); controles.update(); pedirRender(); },
  };
}

export function webglDisponible() {
  try { const c = document.createElement('canvas'); return !!(c.getContext('webgl2') || c.getContext('webgl')); } catch { return false; }
}
