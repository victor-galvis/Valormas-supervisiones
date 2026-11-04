#!/usr/bin/env python3
"""Genera las páginas del prototipo v1.0 de Valor+.  Uso: python3 _construir.py"""
import json
import datetime
from pathlib import Path
from html import escape as esc

BASE = Path(__file__).resolve().parent
MESES = ['enero', 'febrero', 'marzo', 'abril', 'mayo', 'junio', 'julio', 'agosto', 'septiembre', 'octubre', 'noviembre', 'diciembre']
HOY = datetime.date.today()
ACTUALIZADO = f'{HOY.day} de {MESES[HOY.month - 1]} de {HOY.year}'


def cargar(nombre):
    t = (BASE / 'assets' / 'data' / nombre).read_text(encoding='utf-8')
    return json.loads(t[t.index('export default ') + 15:].rstrip().rstrip(';'))


GEO, DAT = cargar('antioquia.js'), cargar('proyectos.js')
SUBS = GEO['meta']['subregiones']
POR_SUB = {s: [m for m in GEO['municipios'] if m['r'] == s] for s in SUBS}
CON, SEG = DAT['conectividad']['municipios'], DAT['seguridad']['municipios']
sedes_sub = [sum(CON.get(m['c'], {}).get('s', 0) for m in POR_SUB[s]) for s in SUBS]
sat_sub = [sum(CON.get(m['c'], {}).get('sat', 0) for m in POR_SUB[s]) for s in SUBS]
rad_sub = [sum(CON.get(m['c'], {}).get('rad', 0) for m in POR_SUB[s]) for s in SUBS]
cam_sub = [sum(SEG.get(m['c'], 0) for m in POR_SUB[s]) for s in SUBS]
mun_seg_sub = [sum(1 for m in POR_SUB[s] if SEG.get(m['c'], 0) > 0) for s in SUBS]

# ---------------------------------------------------------------- íconos
I = {
    'flecha': '<path d="M5 12h14M13 6l6 6-6 6"/>', 'buscar': '<circle cx="11" cy="11" r="7"/><path d="m20 20-3.5-3.5"/>',
    'menu': '<path d="M4 7h16M4 12h16M4 17h16"/>', 'cerrar': '<path d="M6 6l12 12M18 6 6 18"/>',
    'a11y': '<circle cx="12" cy="4.5" r="1.8"/><path d="M5 8.5c2.3.7 4.6 1 7 1s4.7-.3 7-1M12 9.5v4.5M12 14l-3 6.5M12 14l3 6.5"/>',
    'mas': '<path d="M12 5v14M5 12h14"/>', 'menos': '<path d="M5 12h14"/>', 'centro': '<circle cx="12" cy="12" r="3"/><path d="M12 2v4M12 18v4M2 12h4M18 12h4"/>',
    'mano': '<path d="M8 13V5.5a1.5 1.5 0 0 1 3 0V12M11 11V4.5a1.5 1.5 0 0 1 3 0V12M14 11.5V6a1.5 1.5 0 0 1 3 0v8a6 6 0 0 1-6 6h-1a6 6 0 0 1-5-2.7L3 14.5a1.5 1.5 0 0 1 2.4-1.8L8 15"/>',
    'correo': '<rect x="3" y="5" width="18" height="14" rx="2"/><path d="m3 7 9 6 9-6"/>', 'telefono': '<path d="M5 4h4l2 5-2.5 1.5a11 11 0 0 0 5 5L15 13l5 2v4a2 2 0 0 1-2 2A16 16 0 0 1 3 6a2 2 0 0 1 2-2"/>',
    'ubicacion': '<path d="M12 21s-7-6.2-7-11.5A7 7 0 0 1 19 9.5C19 14.8 12 21 12 21z"/><circle cx="12" cy="9.5" r="2.5"/>', 'reloj': '<circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/>',
    'formulario': '<rect x="5" y="3" width="14" height="18" rx="2"/><path d="M9 8h6M9 12h6M9 16h4"/>', 'balanza': '<path d="M12 3v18M7 21h10M5 7h14M5 7l-3 6a3 3 0 0 0 6 0zM19 7l-3 6a3 3 0 0 0 6 0z"/>',
}
REDES = [('Facebook', 'https://www.facebook.com/ValorMasOficial/', '<path d="M14 8h3V4h-3c-2.8 0-4 1.7-4 4.3V10H7v4h3v8h4v-8h3l1-4h-4V8.6c0-.4.3-.6.6-.6z"/>'),
         ('Instagram', 'https://www.instagram.com/valormas/', '<rect x="3" y="3" width="18" height="18" rx="5" fill="none" stroke="currentColor" stroke-width="2"/><circle cx="12" cy="12" r="4" fill="none" stroke="currentColor" stroke-width="2"/><circle cx="17.5" cy="6.5" r="1.2"/>'),
         ('X', 'https://x.com/valormas', '<path d="M17.8 3h3.1l-6.8 7.8L22 21h-6.3l-4.9-6.4L5.2 21H2.1l7.3-8.3L1.8 3h6.4l4.4 5.9zm-1.1 16.2h1.7L7.4 4.7H5.6z"/>'),
         ('LinkedIn', 'https://co.linkedin.com/company/valormasoficial', '<path d="M4.98 3.5a2.5 2.5 0 1 1 0 5 2.5 2.5 0 0 1 0-5zM3 9.5h4V21H3zM9.5 9.5h3.8v1.6h.1c.5-1 1.8-2 3.8-2 4 0 4.8 2.6 4.8 6V21h-4v-5.1c0-1.2 0-2.8-1.7-2.8s-2 1.3-2 2.7V21h-4z"/>')]


def ico(n, cls=''):
    c = f' class="{cls}"' if cls else ''
    return f'<svg{c} viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true" focusable="false">{I[n]}</svg>'


# Íconos ilustrados de servicios (dibujados para el prototipo)
def ico_servicio(tipo):
    trazos = {
        'recaudo': '<rect x="10" y="30" width="44" height="26" rx="5" fill="#d8effb"/><circle cx="32" cy="22" r="13" fill="#b5c73a"/><path d="M32 15v14M28 18.5c0-1.6 1.8-2.6 4-2.6s4 1 4 2.6-1.8 2.4-4 2.6-4 1-4 2.6 1.8 2.6 4 2.6 4-1 4-2.6" stroke="#1c2d4c" stroke-width="2.2" fill="none" stroke-linecap="round"/><path d="M18 42h28M18 48h18" stroke="#1c2d4c" stroke-width="3" stroke-linecap="round"/>',
        'datos': '<ellipse cx="32" cy="16" rx="20" ry="7" fill="#b5c73a"/><path d="M12 16v30c0 4 9 7 20 7s20-3 20-7V16" fill="#d8effb"/><path d="M12 31c0 4 9 7 20 7s20-3 20-7" stroke="#1c2d4c" stroke-width="2.5" fill="none"/><path d="M12 16v30c0 4 9 7 20 7s20-3 20-7V16" stroke="#1c2d4c" stroke-width="2.5" fill="none"/>',
        'proyectos': '<rect x="8" y="38" width="10" height="18" rx="2" fill="#d8effb"/><rect x="24" y="28" width="10" height="28" rx="2" fill="#d8effb"/><rect x="40" y="14" width="10" height="42" rx="2" fill="#b5c73a"/><path d="M8 26 24 18l10 4 18-14" stroke="#1c2d4c" stroke-width="3" fill="none" stroke-linecap="round" stroke-linejoin="round"/><path d="M45 8h7v7" stroke="#1c2d4c" stroke-width="3" fill="none" stroke-linecap="round"/>',
        'consultoria': '<rect x="8" y="10" width="48" height="32" rx="5" fill="#d8effb"/><path d="M8 34h48" stroke="#1c2d4c" stroke-width="2.5"/><path d="M24 54h16M32 42v12" stroke="#1c2d4c" stroke-width="3" stroke-linecap="round"/><path d="m24 20-6 5 6 5M40 20l6 5-6 5" stroke="#1c2d4c" stroke-width="3" fill="none" stroke-linecap="round" stroke-linejoin="round"/><circle cx="32" cy="25" r="3.5" fill="#b5c73a"/>',
        'seguridad': '<path d="M32 6 54 14v14c0 14-9 24-22 30C19 52 10 42 10 28V14z" fill="#d8effb"/><path d="M32 6 54 14v14c0 14-9 24-22 30C19 52 10 42 10 28V14z" stroke="#1c2d4c" stroke-width="2.5" fill="none"/><rect x="22" y="22" width="20" height="12" rx="3" fill="#1c2d4c"/><circle cx="36" cy="28" r="3.5" fill="#b5c73a"/><path d="M26 34l-3 8" stroke="#1c2d4c" stroke-width="3" stroke-linecap="round"/>',
        'energia': '<circle cx="22" cy="20" r="9" fill="#b5c73a"/><path d="M22 4v4M22 32v4M6 20h4M34 20h4M10.7 8.7l2.8 2.8M30.5 28.5l2.8 2.8M10.7 31.3l2.8-2.8" stroke="#1c2d4c" stroke-width="2.5" stroke-linecap="round"/><path d="M24 56h32l-6-22H18z" fill="#d8effb"/><path d="M24 56h32l-6-22H18zM21 45h33M34 34l3 22" stroke="#1c2d4c" stroke-width="2.5" fill="none" stroke-linejoin="round"/>',
    }
    return f'<svg class="ico" viewBox="0 0 64 64" aria-hidden="true" focusable="false">{trazos[tipo]}</svg>'


ARTE_CONECTIVIDAD = '''<svg viewBox="0 0 600 460" preserveAspectRatio="xMidYMid slice" aria-hidden="true" focusable="false">
<defs><linearGradient id="cielo" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#0f1a30"/><stop offset="1" stop-color="#263b63"/></linearGradient></defs>
<rect width="600" height="460" fill="url(#cielo)"/>
<g fill="#d8effb" opacity=".6"><circle cx="60" cy="50" r="1.5"/><circle cx="180" cy="90" r="1.2"/><circle cx="300" cy="40" r="1.6"/><circle cx="420" cy="110" r="1.2"/><circle cx="540" cy="60" r="1.5"/><circle cx="250" cy="150" r="1"/><circle cx="500" cy="170" r="1"/></g>
<g class="flota"><rect x="430" y="58" width="44" height="14" rx="3" fill="#e9edf1"/><rect x="474" y="61" width="70" height="8" fill="#3b4f78"/><rect x="360" y="61" width="70" height="8" fill="#3b4f78"/><circle cx="436" cy="65" r="3" fill="#b5c73a"/></g>
<path d="M452 76 300 300" stroke="#b5c73a" stroke-width="3" stroke-dasharray="10 8"/>
<path d="M0 330 120 240 210 300 320 210 430 290 520 230 600 280V460H0z" fill="#2a6a3f"/>
<path d="M0 380 90 330 200 370 300 320 420 370 520 330 600 360V460H0z" fill="#194a2b"/>
<g transform="translate(250 300)"><rect x="0" y="20" width="110" height="46" fill="#f4f7f5"/><path d="M-8 22 55-8l63 30z" fill="#194a2b"/><rect x="18" y="38" width="16" height="28" fill="#1c2d4c"/><rect x="48" y="34" width="22" height="14" fill="#d8effb"/><rect x="78" y="34" width="22" height="14" fill="#d8effb"/>
<path d="M80 -4v-18" stroke="#c9d0d8" stroke-width="3"/><rect x="62" y="-40" width="40" height="22" rx="4" fill="#fff" transform="rotate(-25 82 -29)"/></g>
<g fill="none" stroke="#b5c73a" stroke-width="3" opacity=".8"><path d="M335 395a30 30 0 0 1 40 0"/><path d="M325 383a46 46 0 0 1 60 0"/></g>
</svg>'''

ARTE_SEGURIDAD = '''<svg viewBox="0 0 600 460" preserveAspectRatio="xMidYMid slice" aria-hidden="true" focusable="false">
<rect width="600" height="460" fill="#0f1a30"/>
<g stroke="#263b63" stroke-width="1">''' + ''.join(f'<path d="M{x} 0V460"/>' for x in range(0, 600, 40)) + ''.join(f'<path d="M0 {y}H600"/>' for y in range(0, 460, 40)) + '''</g>
<g stroke="#b5c73a" stroke-width="2" fill="none" opacity=".85"><path d="M300 230 120 120M300 230 470 110M300 230 520 300M300 230 150 340M300 230 330 400M300 230 220 70"/></g>
<g fill="#d8effb"><circle cx="120" cy="120" r="7"/><circle cx="470" cy="110" r="7"/><circle cx="520" cy="300" r="7"/><circle cx="150" cy="340" r="7"/><circle cx="330" cy="400" r="7"/><circle cx="220" cy="70" r="7"/></g>
<circle cx="300" cy="230" r="34" fill="none" stroke="#b5c73a" stroke-width="4"/><circle cx="300" cy="230" r="14" fill="#b5c73a"/>
<g class="flota" transform="translate(380 160)"><path d="M0 0h70v10H0z" fill="#e9edf1"/><rect x="40" y="10" width="70" height="40" rx="8" fill="#f4f6f8"/><circle cx="96" cy="30" r="11" fill="#1c2d4c"/><circle cx="96" cy="30" r="4" fill="#b5c73a"/><path d="M110 30 190 -10 190 70z" fill="#b5c73a" opacity=".18"/></g>
</svg>'''


# ---------------------------------------------------------------- plantilla
NAV = [('Inicio', 'index.html', 'inicio'), ('Nosotros', 'index.html#nosotros', 'nosotros'), ('Servicios', 'index.html#servicios', 'servicios'),
       ('Proyectos', 'index.html#proyectos', 'proyectos'), ('Transparencia', 'transparencia.html', 'transparencia'),
       ('Atención a la ciudadanía', 'atencion-ciudadania.html', 'atencion'), ('Participa', 'participa.html', 'participa')]
PREFS = ("(function(){try{var d=document.documentElement,s=localStorage,e=s.getItem('v1.escala'),c=s.getItem('v1.contraste'),m=s.getItem('v1.movimiento');"
         "if(e)d.style.setProperty('--escala',e);if(c)d.dataset.contraste='alto';d.dataset.movimiento=m||(matchMedia('(prefers-reduced-motion: reduce)').matches?'no':'si');}catch(x){}})();")


def pagina(ruta, titulo, desc, activo, cuerpo, modulo=True, json_bloques='', vista=None):
    r = '../' * ruta.count('/')
    nav = ''.join(f'<li><a href="{r}{h}"{" aria-current=" + chr(34) + "page" + chr(34) if k == activo else ""}>{n}</a></li>' for n, h, k in NAV)
    navm = ''.join(f'<li><a href="{r}{h}">{n}</a></li>' for n, h, k in NAV)
    redes = ''.join(f'<a href="{u}" target="_blank" rel="noopener" aria-label="{n} de Valor+ (abre en una pestaña nueva)"><svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true">{p}</svg></a>' for n, u, p in REDES)
    mod = f'<link rel="modulepreload" href="{r}assets/js/vendor/three.module.min.js">\n<script type="module" src="{r}assets/js/interaccion.js"></script>' if modulo else ''
    html = f'''<!doctype html>
<html lang="es-CO">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(titulo)} | Valor+</title>
<meta name="description" content="{esc(desc)}">
<meta name="robots" content="noindex">
<meta name="theme-color" content="#1c2d4c">
<link rel="icon" href="{r}assets/img/favicon.svg" type="image/svg+xml">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Montserrat:wght@600;700;800&amp;family=Work+Sans:wght@400;500;600&amp;display=swap">
<link rel="stylesheet" href="{r}assets/css/app.css">
<script>{PREFS}</script>
<script src="{r}assets/js/base.js" defer></script>
{mod}
</head>
<body data-pagina="{vista or activo}">
<a class="saltar" href="#contenido">Saltar al contenido principal</a>
<div class="govco" role="region" aria-label="Barra del portal GOV.CO"><div class="contenedor"><a href="https://www.gov.co/" target="_blank" rel="noopener"><img src="{r}assets/img/govco.svg" alt="GOV.CO, portal del Estado colombiano (abre en una pestaña nueva)" width="101" height="22"></a></div></div>
<header class="cabecera">
  <div class="contenedor">
    <a class="marca" href="{r}index.html" aria-label="Valor+, ir al inicio"><img class="pos" src="{r}assets/img/logo.svg" alt="" width="180" height="32"><img class="neg" src="{r}assets/img/logo-blanco.svg" alt="" width="180" height="32"></a>
    <nav class="menu" aria-label="Menú principal"><ul>{nav}</ul></nav>
    <div class="acciones">
      <button class="icono-btn" type="button" data-abrir-a11y aria-haspopup="dialog" aria-label="Opciones de accesibilidad">{ico('a11y')}</button>
      <a class="boton lima mini" href="{r}atencion-ciudadania.html#pqrsd">PQRSD</a>
      <button class="icono-btn btn-menu" type="button" aria-expanded="false" aria-controls="menu-movil" aria-label="Abrir menú">{ico('menu')}</button>
    </div>
  </div>
</header>
<div class="menu-movil" id="menu-movil" role="dialog" aria-modal="true" aria-label="Menú">
  <button class="icono-btn cerrar" type="button" aria-label="Cerrar menú">{ico('cerrar')}</button>
  <nav aria-label="Menú principal (móvil)"><ul>{navm}<li><a href="{r}atencion-ciudadania.html#pqrsd">Radicar una PQRSD</a></li></ul></nav>
</div>
<main id="contenido" tabindex="-1">
{cuerpo}
</main>
<footer class="pie">
  <div class="contenedor">
    <div class="columnas">
      <div><a class="marca" href="{r}index.html"><img src="{r}assets/img/logo-blanco.svg" alt="Valor+" width="200" height="36"></a>
        <p>Integramos servicios y procesos tecnológicos para las entidades públicas de Antioquia.</p><div class="redes">{redes}</div></div>
      <div><h2>Contacto</h2><address>
        <span><strong>Valor+ S.A.S.</strong></span>
        <span>Calle 41 N.° 52-28, Edificio Edatel, piso 3, sector La Alpujarra, Medellín, Antioquia</span>
        <span>Horario: lunes a jueves de 7:30 a. m. a 5:30 p. m.; viernes de 7:30 a. m. a 1:30 p. m.</span>
        <span>Teléfono: <a href="tel:+576044443747">+57 (604) 444 3747</a> · Línea gratuita: <a href="tel:018000415379">01 8000 415 379</a></span>
      </address></div>
      <div><h2>Canales oficiales</h2><ul>
        <li>PQRSD: <a href="mailto:pqrds@valormas.gov.co">pqrds@valormas.gov.co</a></li>
        <li>Notificaciones judiciales: <a href="mailto:notificaciones@valormas.gov.co">notificaciones@valormas.gov.co</a></li>
        <li>Línea anticorrupción: <a href="mailto:transparencia@valormas.gov.co">transparencia@valormas.gov.co</a></li>
      </ul></div>
      <div><h2>Enlaces</h2><ul>
        <li><a href="{r}transparencia.html">Transparencia y acceso a la información pública</a></li>
        <li><a href="{r}atencion-ciudadania.html">Atención y servicios a la ciudadanía</a></li>
        <li><a href="{r}participa.html">Participa</a></li>
        <li><a href="{r}politicas.html">Política de tratamiento de datos personales</a></li>
        <li><a href="{r}accesibilidad.html">Accesibilidad</a></li>
        <li><a href="{r}mapa-del-sitio.html">Mapa del sitio</a></li>
      </ul></div>
    </div>
    <div class="base"><p>© <span data-anio>{HOY.year}</span> Valor+ S.A.S. Última actualización: {ACTUALIZADO}.</p><p>Prototipo v1.0 · Contenido y diseño de propuesta</p></div>
  </div>
</footer>
<div class="govco-pie" role="region" aria-label="Pie GOV.CO"><div class="contenedor"><a href="https://www.gov.co/" target="_blank" rel="noopener"><img src="{r}assets/img/co-govco.png" alt="Marca país Colombia y GOV.CO (abre en una pestaña nueva)" width="163" height="38"></a><p>Sitio de entidad pública del orden departamental</p></div></div>
<button class="flotante-a11y" type="button" data-abrir-a11y aria-haspopup="dialog" aria-label="Opciones de accesibilidad">{ico('a11y')}</button>
<dialog class="a11y" id="a11y" aria-labelledby="a11y-t">
  <header><h2 id="a11y-t">Accesibilidad</h2><button class="icono-btn" type="button" data-cerrar aria-label="Cerrar">{ico('cerrar')}</button></header>
  <div class="cuerpo">
    <div class="opcion"><span id="esc-t">Tamaño del texto</span><div class="seg" role="group" aria-labelledby="esc-t"><button type="button" data-escala="1">A</button><button type="button" data-escala="1.15">A+</button><button type="button" data-escala="1.3">A++</button></div></div>
    <div class="opcion"><span id="sw-c">Alto contraste</span><button type="button" class="interruptor" role="switch" aria-checked="false" aria-labelledby="sw-c" data-sw="contraste"></button></div>
    <div class="opcion"><span id="sw-m">Detener animaciones</span><button type="button" class="interruptor" role="switch" aria-checked="false" aria-labelledby="sw-m" data-sw="movimiento"></button></div>
    <button class="boton borde mini" type="button" data-restablecer>Restablecer</button>
    <p class="nota">Este sitio sigue las pautas WCAG 2.1 nivel AA (Resolución MinTIC 1519 de 2020). <a href="{r}accesibilidad.html">Declaración de accesibilidad</a>.</p>
  </div>
</dialog>
{json_bloques}
</body>
</html>
'''
    destino = BASE / ruta
    destino.parent.mkdir(parents=True, exist_ok=True)
    destino.write_text(html, encoding='utf-8')
    PAGINAS.append((titulo, ruta))


PAGINAS = []


def json_tag(id_, datos):
    return f'<script type="application/json" id="{id_}">{json.dumps(datos, ensure_ascii=False)}</script>'


def grafica_barras(id_, titulo, metricas, unidad_cols, nota):
    chips = ''.join(f'<button type="button" class="chip" data-metrica="{i}" aria-pressed="{str(i == 0).lower()}">{esc(m["nombre"])}</button>' for i, m in enumerate(metricas))
    cols = ''.join(f'<th scope="col">{esc(c)}</th>' for c in unidad_cols)
    return f'''<figure class="grafica" data-tipo="barras" data-datos="{id_}" data-titulo="{esc(titulo)}" data-aparece>
  <header><h3>{esc(titulo)}</h3><div class="chips" role="group" aria-label="Cambiar la métrica">{chips}</div></header>
  <div class="lienzo"></div>
  <figcaption class="nota">{nota} Pasa el cursor o usa la tecla Tab sobre las barras para ver el detalle.</figcaption>
  <details><summary>Ver los datos en tabla</summary><table class="tabla"><caption class="sr-only">{esc(titulo)}</caption><thead><tr><th scope="col">Subregión</th>{cols}</tr></thead><tbody></tbody></table></details>
</figure>'''


def panel_mapa(id_, modo, titulo='Explora el mapa'):
    chips = ''
    if modo == 'inicio':
        chips = '''<div><label id="capa-t">Capa</label><div class="chips" role="group" aria-labelledby="capa-t" style="margin-top:8px">
      <button type="button" class="chip" data-capa="todos" aria-pressed="true">Subregiones</button>
      <button type="button" class="chip" data-capa="conectividad" aria-pressed="false"><span class="punto" style="background:#b5c73a"></span>Conectividad</button>
      <button type="button" class="chip" data-capa="seguridad" aria-pressed="false"><span class="punto" style="background:#d8effb"></span>Seguridad</button></div></div>'''
    leyenda = {'inicio': '<span><i style="background:#b5c73a"></i>Sedes conectadas</span><span><i style="background:#d8effb"></i>Cámaras integradas</span>',
               'conectividad': '<span><i style="background:#b5c73a"></i>Sedes educativas conectadas (más alto = más sedes)</span>',
               'seguridad': '<span><i style="background:#b5c73a"></i>Nodo operando</span><span><i style="background:#d8effb"></i>Nodo en proceso · cámaras</span>'}[modo]
    return f'''<div class="panel-mapa" id="{id_}">
  {chips}
  <div><label for="{id_}-q">Busca tu municipio</label>
    <div class="buscador" style="margin-top:8px">{ico('buscar')}<input id="{id_}-q" type="text" role="combobox" aria-autocomplete="list" aria-expanded="false" aria-controls="{id_}-lista" placeholder="Ej.: Urrao, Yarumal, Turbo" autocomplete="off"><ul class="sugerencias" id="{id_}-lista" role="listbox" hidden></ul></div></div>
  <div class="ficha-mpio" aria-live="polite"><p class="sub" style="margin:0">Selecciona un municipio en el mapa o búscalo por su nombre.</p></div>
  <div class="leyenda">{leyenda}</div>
</div>'''


AVISO_3D = '<p class="aviso-3d" role="status">Cargando la escena 3D…</p>'
CONTROL_3D = AVISO_3D + f'''<div class="control-3d" role="group" aria-label="Controles del mapa 3D"><button type="button" class="icono-btn" data-zoom="mas" aria-label="Acercar el mapa">{ico('mas')}</button><button type="button" class="icono-btn" data-zoom="menos" aria-label="Alejar el mapa">{ico('menos')}</button><button type="button" class="icono-btn" data-zoom="centro" aria-label="Volver a la vista general">{ico('centro')}</button></div>
<p class="ayuda-3d" aria-hidden="true">{ico('mano')} Arrastra para girar · Rueda o pellizco para acercar</p>'''
NOTA_DATOS = 'Totales de referencia de las fichas de proyecto; la distribución por municipio es ilustrativa para el prototipo.'


# ---------------------------------------------------------------- inicio
def inicio():
    servicios = [
        ('recaudo', 'Estrategias tecnológicas del recaudo', 'Plataformas y operación para que las rentas públicas se liquiden, cobren y recauden de forma ágil y transparente.', '#'),
        ('datos', 'Automatización de la información', 'Datos del territorio convertidos en decisiones: catastro multipropósito, gestión documental y telegestión.', '#'),
        ('proyectos', 'Estructuración y gerenciamiento de proyectos', 'Llevamos los proyectos de la idea a la operación, con gerencia técnica, financiera y de calidad.', 'proyectos/conectividad-satelital.html'),
        ('consultoria', 'Soluciones tecnológicas y consultoría', 'Mesa de servicios, nube, ciberseguridad, licenciamiento y especialistas para la operación digital del Estado.', '#'),
        ('seguridad', 'Seguridad', 'Centros de monitoreo, videovigilancia y control de acceso integrados para municipios más seguros.', 'proyectos/seguridad-ciudadana.html'),
        ('energia', 'Energía en tecnologías limpias', 'Alumbrado eficiente y soluciones fotovoltaicas que reducen costos y emisiones.', '#'),
    ]
    cards = ''.join(f'''<a class="servicio" href="{h}" data-aparece style="--d:{i * 70}">{ico_servicio(k)}<h3>{t}</h3><p>{d}</p><span class="mas">{'Ver proyecto' if h != '#' else 'Conocer más'} {ico('flecha')}</span></a>''' for i, (k, t, d, h) in enumerate(servicios))
    ciudadania = [('1', 'Transparencia', 'Información pública según la Ley 1712 de 2014.', 'transparencia.html'),
                  ('2', 'PQRSD', 'Radica y consulta peticiones, quejas, reclamos, sugerencias y denuncias.', 'atencion-ciudadania.html#pqrsd'),
                  ('3', 'Participa', 'Rendición de cuentas y espacios de diálogo con la ciudadanía.', 'participa.html'),
                  ('4', 'Contratación', 'Convocatorias, invitaciones y plan anual de adquisiciones.', 'transparencia.html#t3'),
                  ('5', 'Datos abiertos', 'Conjuntos de datos e instrumentos de gestión de la información.', 'transparencia.html#t7'),
                  ('6', 'Atención', 'Canales, horarios y sede de atención presencial.', 'atencion-ciudadania.html')]
    acc = ''.join(f'<a class="cat" href="{h}" data-aparece style="--d:{i * 60}"><span class="n" aria-hidden="true">{ico("mas")}</span><span><h3>{t}</h3><p>{d}</p></span></a>' for i, (n, t, d, h) in enumerate(ciudadania))
    datos_sub = {'categorias': SUBS, 'metricas': [{'nombre': 'Sedes educativas conectadas', 'unidad': 'sedes', 'valores': sedes_sub}, {'nombre': 'Cámaras integradas', 'unidad': 'cámaras', 'valores': cam_sub}]}
    cuerpo = f'''
<section class="hero" aria-labelledby="hero-t">
  <div class="hero-trama" aria-hidden="true"></div>
  <div class="hero-escena" id="mapa-hero">{CONTROL_3D}</div>
  <div class="contenedor">
    <div>
      <p class="antetitulo">Valor+ · Antioquia</p>
      <h1 id="hero-t">Tecnología que <em>llega</em> a cada territorio</h1>
      <p class="entrada">Integramos conectividad, seguridad, datos y energía para que las entidades públicas de Antioquia presten mejores servicios a la ciudadanía.</p>
      <div class="botones"><a class="boton lima" href="#proyectos">Explorar proyectos {ico('flecha')}</a><a class="boton borde" href="atencion-ciudadania.html">Atención a la ciudadanía</a></div>
      {panel_mapa('panel-mapa', 'inicio')}
    </div>
  </div>
</section>

<section class="seccion celeste" aria-labelledby="cifras-t">
  <div class="contenedor">
    <p class="antetitulo">Impacto</p>
    <h2 id="cifras-t" data-aparece>Resultados que se ven en el territorio</h2>
    <div class="cifras" style="margin-top:32px" data-aparece>
      <div class="cifra"><p class="n"><span data-cuenta="870">870</span></p><p>sedes educativas rurales con internet confirmado</p></div>
      <div class="cifra"><p class="n">+<span data-cuenta="900">900</span></p><p>cámaras integradas al nodo departamental de seguridad</p></div>
      <div class="cifra"><p class="n"><span data-cuenta="48">48</span></p><p>municipios conectados a la red de seguridad</p></div>
      <div class="cifra"><p class="n"><span data-cuenta="9">9</span></p><p>subregiones de Antioquia con presencia de Valor+</p></div>
    </div>
    <p class="nota" style="margin-top:14px">Cifras de referencia de las fichas de proyecto.</p>
  </div>
</section>

<section class="seccion" id="servicios" aria-labelledby="serv-t">
  <div class="contenedor">
    <p class="antetitulo">Servicios</p>
    <h2 id="serv-t" data-aparece>Seis líneas para transformar la gestión pública</h2>
    <div class="grid g3" style="margin-top:36px">{cards}</div>
  </div>
</section>

<section class="seccion marino" id="proyectos" aria-labelledby="proy-t">
  <div class="contenedor">
    <p class="antetitulo">Proyectos</p>
    <h2 id="proy-t" data-aparece>Explora nuestros proyectos en 3D</h2>
    <p class="entrada" data-aparece>Recorre cómo llega internet satelital a una escuela rural y cómo funciona la red departamental de cámaras de seguridad.</p>
    <div class="grid g2" style="margin-top:36px">
      <a class="proyecto" href="proyectos/conectividad-satelital.html" data-aparece><div class="arte">{ARTE_CONECTIVIDAD}</div><div class="texto"><span class="etiqueta">Estructuración y gerenciamiento de proyectos</span><h3>Conectividad satelital para la ruralidad</h3><p>Antenas de órbita baja que conectan sedes educativas donde la fibra no llega.</p><span class="ir">Ver la experiencia 3D {ico('flecha')}</span></div></a>
      <a class="proyecto" href="proyectos/seguridad-ciudadana.html" data-aparece style="--d:120"><div class="arte">{ARTE_SEGURIDAD}</div><div class="texto"><span class="etiqueta">Seguridad</span><h3>Red departamental de seguridad</h3><p>Cámaras en 48 municipios conectadas a un nodo departamental de monitoreo.</p><span class="ir">Ver la experiencia 3D {ico('flecha')}</span></div></a>
    </div>
  </div>
</section>

<section class="seccion celeste" aria-labelledby="datos-t">
  <div class="contenedor">
    <p class="antetitulo">Antioquia en datos</p>
    <h2 id="datos-t" data-aparece>¿Cómo se distribuye nuestro trabajo?</h2>
    <div style="margin-top:28px">{grafica_barras('d-sub', 'Presencia por subregión', datos_sub['metricas'], ['Sedes conectadas', 'Cámaras integradas'], NOTA_DATOS)}</div>
  </div>
</section>

<section class="seccion" id="nosotros" aria-labelledby="nos-t">
  <div class="contenedor grid g2" style="align-items:center">
    <div data-aparece>
      <p class="antetitulo">Nosotros</p>
      <h2 id="nos-t">Diez años integrando tecnología para el sector público</h2>
      <p class="entrada">Valor+ S.A.S. es una empresa pública que diseña, integra y opera soluciones tecnológicas para entidades del Estado. Traducimos las necesidades del territorio en proyectos que funcionan.</p>
      <a class="boton marino" href="transparencia.html#t1">Misión, visión y estructura {ico('flecha')}</a>
    </div>
    <div class="cifras" data-aparece style="--d:120">
      <div class="cifra"><p class="n">360°</p><p>Integramos tecnología, operación y experiencia de usuario.</p></div>
      <div class="cifra"><p class="n">+</p><p>Generamos valor público medible en cada proyecto.</p></div>
    </div>
  </div>
</section>

<section class="seccion celeste" id="ciudadania" aria-labelledby="ciu-t">
  <div class="contenedor">
    <p class="antetitulo">Ciudadanía</p>
    <h2 id="ciu-t" data-aparece>Información y servicios a un clic</h2>
    <div class="grid g3" style="margin-top:32px">{acc}</div>
  </div>
</section>'''
    pagina('index.html', 'Tecnología que llega a cada territorio', 'Valor+ integra conectividad, seguridad, datos y energía para las entidades públicas de Antioquia.', 'inicio', cuerpo, json_bloques=json_tag('d-sub', datos_sub))


# ---------------------------------------------------------------- conectividad
def conectividad():
    datos_sub = {'categorias': SUBS, 'metricas': [{'nombre': 'Por satélite', 'unidad': 'sedes', 'valores': sat_sub}, {'nombre': 'Por radioenlace', 'unidad': 'sedes', 'valores': rad_sub}]}
    datos_tec = {'etiquetas': ['Satelital (órbita baja)', 'Radioenlace'], 'valores': [784, 86], 'colores': ['#b5c73a', '#1c2d4c'], 'centro': 'sedes conectadas'}
    pasos = [
        ('La brecha', 'Montañas que separan', 'En la Antioquia rural muchas sedes educativas están a horas de la cabecera municipal. Llevar fibra óptica por cordilleras y ríos puede tomar años y costar más de lo que el territorio puede esperar.'),
        ('La antena', 'Una antena que mira al cielo', 'Sobre el techo de la sede se instala una antena de órbita baja, como las de Starlink. Toca los puntos numerados de la escena para conocer cada componente.'),
        ('El enlace', 'Satélites a 550 kilómetros', 'Una constelación de satélites en órbita baja pasa sobre la sede y mantiene el enlace. Al estar cerca de la Tierra, la conexión tiene baja latencia: sirve para clases en línea y videollamadas.'),
        ('La sede conectada', 'Internet en el aula', 'El router distribuye la señal en la sede. Valor+ gerencia el proyecto: prioriza sedes, negocia con los operadores, supervisa la instalación y hace seguimiento al servicio.'),
    ]
    pasos_html = ''.join(f'<article class="paso" data-paso="{i}"><div class="caja"><p class="num">0{i + 1} · {a}</p><h2>{t}</h2><p>{d}</p></div></article>' for i, (a, t, d) in enumerate(pasos))
    flujo = [('Priorización', 'Identificamos con la Gobernación las sedes sin conectividad y las ordenamos según matrícula, distancia y condiciones técnicas.'),
             ('Negociación', 'Gestionamos con los operadores las mejores condiciones; las eficiencias logradas permiten conectar más sedes con el mismo presupuesto.'),
             ('Instalación', 'Supervisamos la instalación de antenas, routers y cableado, y verificamos que el servicio quede operativo.'),
             ('Soporte', 'Hacemos seguimiento a la operatividad, atendemos novedades y coordinamos la reactivación de sedes con fallas.')]
    fl = ''.join(f'<li><button type="button" aria-pressed="{str(i == 0).lower()}" data-texto="{esc(d)}"><strong>{t}</strong></button></li>' for i, (t, d) in enumerate(flujo))
    meta = [('Sedes con servicio confirmado', 870, 1228, 'de 1.228 sedes por reactivar'), ('Aporte a la meta departamental', 870, 3414, 'de 3.414 sedes conectadas (Plan de Desarrollo 2024-2027)')]
    mil = lambda n: f'{n:,}'.replace(',', '.')
    barras_meta = ''.join(f'''<div data-aparece><p style="display:flex;justify-content:space-between;gap:12px;flex-wrap:wrap;margin:0 0 8px"><strong>{t}</strong><span><strong>{mil(v)}</strong> {txt} · {v / m * 100:.0f} %</span></p>
<div role="progressbar" aria-label="{t}" aria-valuemin="0" aria-valuemax="{m}" aria-valuenow="{v}" aria-valuetext="{mil(v)} {txt}" style="height:18px;border-radius:999px;background:#fff;border:1px solid var(--linea);overflow:hidden"><div style="width:{v / m * 100:.1f}%;height:100%;background:linear-gradient(90deg,var(--verde-600),var(--lima));border-radius:999px"></div></div></div>''' for t, v, m, txt in meta)
    cuerpo = f'''
<section class="cabeza-pagina">
  <div class="contenedor">
    <nav class="migas" aria-label="Ruta de navegación"><ol><li><a href="../index.html">Inicio</a></li><li><a href="../index.html#proyectos">Proyectos</a></li><li aria-current="page">Conectividad satelital</li></ol></nav>
    <p class="antetitulo">Estructuración y gerenciamiento de proyectos</p>
    <h1>Conectividad satelital para la ruralidad</h1>
    <p class="entrada" style="color:#c9d4e6">Internet de órbita baja para las sedes educativas rurales de Antioquia. Haz scroll y recorre el proyecto en 3D.</p>
  </div>
</section>
<section class="relato" id="relato-antena" aria-label="Recorrido 3D del proyecto">
  <div class="relato-escena" id="escena-antena">{AVISO_3D}<p class="ayuda-3d" aria-hidden="true">{ico('mano')} Arrastra para mirar alrededor</p></div>
  <div class="relato-pasos">{pasos_html}</div>
</section>
<section class="seccion marino" aria-labelledby="mapa-t">
  <div class="contenedor">
    <p class="antetitulo">¿Dónde estamos?</p>
    <h2 id="mapa-t">Sedes conectadas en el mapa de Antioquia</h2>
    <p class="entrada">Cada municipio se eleva según el número de sedes educativas conectadas. Gira el mapa, acércate y elige un municipio.</p>
  </div>
  <div class="contenedor grid g2" style="margin-top:30px;align-items:start">
    <div style="position:relative;height:min(72vh,640px);border-radius:var(--r-l);overflow:hidden;background:radial-gradient(circle at 50% 40%,#263b63,#0f1a30)" id="mapa-seccion" data-capa="conectividad">{CONTROL_3D}</div>
    {panel_mapa('panel-seccion', 'conectividad')}
  </div>
</section>
<section class="seccion celeste" aria-labelledby="dat-t">
  <div class="contenedor">
    <p class="antetitulo">Datos del proyecto</p>
    <h2 id="dat-t" data-aparece>Avance de la conectividad</h2>
    <div class="grid" style="margin-top:28px;gap:22px">{barras_meta}</div>
    <div class="grid g2" style="margin-top:32px;align-items:start">
      {grafica_barras('c-sub', 'Sedes por subregión y tecnología', datos_sub['metricas'], ['Por satélite', 'Por radioenlace'], NOTA_DATOS)}
      <figure class="grafica" data-tipo="dona" data-datos="c-tec" data-titulo="Sedes por tecnología" data-aparece>
        <header><h3>Sedes por tecnología</h3></header><div class="lienzo" style="max-width:340px;margin-inline:auto"></div>
        <figcaption class="nota">Selecciona un segmento para ver su valor.</figcaption>
        <details><summary>Ver los datos en tabla</summary><table class="tabla"><thead><tr><th scope="col">Tecnología</th><th scope="col">Sedes</th><th scope="col">%</th></tr></thead><tbody></tbody></table></details>
      </figure>
    </div>
  </div>
</section>
<section class="seccion" aria-labelledby="como-t">
  <div class="contenedor">
    <p class="antetitulo">Cómo lo hacemos</p>
    <h2 id="como-t" data-aparece>Del diagnóstico al aula conectada</h2>
    <ol class="flujo" data-detalle="det-con" style="margin-top:28px">{fl}</ol>
    <div class="flujo-detalle" id="det-con" aria-live="polite">{esc(flujo[0][1])}</div>
    <p style="margin-top:32px"><a class="boton marino" href="../atencion-ciudadania.html">¿Tu sede necesita conectividad? Escríbenos {ico('flecha')}</a></p>
  </div>
</section>'''
    pagina('proyectos/conectividad-satelital.html', 'Conectividad satelital para la ruralidad', 'Recorrido 3D del proyecto de internet de órbita baja para sedes educativas rurales de Antioquia.', 'proyectos', cuerpo,
           json_bloques=json_tag('c-sub', datos_sub) + json_tag('c-tec', datos_tec), vista='conectividad')


# ---------------------------------------------------------------- seguridad
def seguridad():
    datos_sub = {'categorias': SUBS, 'metricas': [{'nombre': 'Cámaras integradas', 'unidad': 'cámaras', 'valores': cam_sub}, {'nombre': 'Municipios conectados', 'unidad': 'municipios', 'valores': mun_seg_sub}]}
    nuevas = DAT['seguridad']['nuevas']
    datos_cam = {'etiquetas': ['Autodomo PTZ', 'Lectura de placas (LPR)', 'Multisensor'], 'valores': [nuevas['Autodomo PTZ'], nuevas['Lectura de placas (LPR)'], nuevas['Multisensor']], 'colores': ['#1c2d4c', '#b5c73a', '#8fbf9b'], 'centro': 'cámaras nuevas'}
    pasos = [
        ('La red', 'Una sola red para 48 municipios', 'Más de 900 cámaras de municipios de todas las subregiones envían su señal a un nodo departamental de seguridad. Gira el mapa: los arcos muestran el viaje de los datos.'),
        ('El nodo departamental', 'El centro que lo ve todo', 'En Medellín, el nodo departamental recibe, almacena y monitorea las cámaras. Desde allí se coordinan alertas con las autoridades.'),
        ('Nodos subregionales', 'Cerca de cada territorio', 'Los nodos subregionales concentran la señal de su zona y la retransmiten. Hay nodos en operación y otros en proceso de puesta en marcha.'),
        ('Operación continua', 'Instalación, soporte y mantenimiento', 'Valor+ gerencia la implementación, el mantenimiento preventivo y correctivo y la mesa de ayuda, para que cada cámara esté disponible cuando se necesita.'),
    ]
    pasos_html = ''.join(f'<article class="paso" data-paso="{i}"><div class="caja"><p class="num">0{i + 1} · {a}</p><h2>{t}</h2><p>{d}</p></div></article>' for i, (a, t, d) in enumerate(pasos))
    camaras = [
        ('Autodomo PTZ', 'Gira 360°, inclina y acerca con zoom óptico para seguir un evento en tiempo real.', ['Movimiento horizontal y vertical continuo', 'Zoom óptico para detalle a distancia', 'Ideal para plazas, parques e intersecciones']),
        ('Lectura de placas (LPR)', 'Reconoce automáticamente las placas de los vehículos que pasan por su campo de visión.', ['Lectura día y noche con iluminación infrarroja', 'Alertas de vehículos reportados', 'Ubicada en entradas y salidas de los municipios']),
        ('Multisensor', 'Cuatro sensores en un solo equipo cubren varias direcciones a la vez.', ['Vista panorámica sin puntos ciegos', 'Menos equipos para cubrir más área', 'Ideal para corredores y espacios amplios']),
    ]
    tabs = ''.join(f'<button type="button" role="tab" id="tab-c{i}" aria-controls="pan-c{i}" aria-selected="{str(i == 0).lower()}" tabindex="{0 if i == 0 else -1}">{n}</button>' for i, (n, d, s) in enumerate(camaras))
    panes = ''.join(f'<div role="tabpanel" id="pan-c{i}" aria-labelledby="tab-c{i}"{"" if i == 0 else " hidden"}><p class="entrada" style="font-size:1.05rem">{d}</p><ul class="specs">{"".join(f"<li>{x}</li>" for x in s)}</ul></div>' for i, (n, d, s) in enumerate(camaras))
    flujo = [('Captura', 'La cámara registra imagen de forma continua y, en el caso de las LPR, identifica placas automáticamente.'),
             ('Transmisión', 'La señal viaja por fibra o radioenlace hasta el nodo subregional y luego al nodo departamental.'),
             ('Monitoreo', 'Operadores en el nodo departamental observan, graban y analizan; las alertas se priorizan en tiempo real.'),
             ('Respuesta', 'La información se comparte con la Policía y las autoridades municipales para actuar con rapidez.')]
    fl = ''.join(f'<li><button type="button" aria-pressed="{str(i == 0).lower()}" data-texto="{esc(d)}"><strong>{t}</strong></button></li>' for i, (t, d) in enumerate(flujo))
    cuerpo = f'''
<section class="cabeza-pagina">
  <div class="contenedor">
    <nav class="migas" aria-label="Ruta de navegación"><ol><li><a href="../index.html">Inicio</a></li><li><a href="../index.html#proyectos">Proyectos</a></li><li aria-current="page">Red departamental de seguridad</li></ol></nav>
    <p class="antetitulo">Seguridad</p>
    <h1>Red departamental de seguridad</h1>
    <p class="entrada" style="color:#c9d4e6">Cámaras, nodos y operación continua para municipios más seguros. Haz scroll para recorrer la red en 3D.</p>
  </div>
</section>
<section class="relato" id="relato-red" aria-label="Recorrido 3D de la red de seguridad">
  <div class="relato-escena" id="escena-red">{CONTROL_3D}</div>
  <div class="relato-pasos">{pasos_html}</div>
</section>
<section class="seccion" aria-labelledby="cam-t">
  <div class="contenedor">
    <p class="antetitulo">Tecnología</p>
    <h2 id="cam-t" data-aparece>Conoce las cámaras de la red</h2>
    <p class="entrada" data-aparece>Gira cada equipo, acércate y mira su campo de visión. También puedes elegir un tipo de cámara en la gráfica.</p>
    <div class="visor" style="margin-top:28px">
      <div class="visor-escena" id="visor-camaras">{AVISO_3D}</div>
      <div class="visor-info">
        <div class="tabs" role="tablist" aria-label="Tipos de cámara" id="tabs-camaras">{tabs}</div>
        {panes}
        <figure class="grafica" data-tipo="dona" data-datos="s-cam" data-titulo="Cámaras nuevas por tipo" id="grafica-camaras">
          <header><h3>217 cámaras nuevas por tipo</h3></header><div class="lienzo" style="max-width:260px;margin-inline:auto"></div>
          <details><summary>Ver los datos en tabla</summary><table class="tabla"><thead><tr><th scope="col">Tipo</th><th scope="col">Cámaras</th><th scope="col">%</th></tr></thead><tbody></tbody></table></details>
        </figure>
      </div>
    </div>
  </div>
</section>
<section class="seccion marino" aria-labelledby="fl-t">
  <div class="contenedor">
    <p class="antetitulo">Cómo funciona</p>
    <h2 id="fl-t" data-aparece>De la cámara a la respuesta</h2>
    <ol class="flujo" data-detalle="det-seg" style="margin-top:28px">{fl}</ol>
    <div class="flujo-detalle" id="det-seg" aria-live="polite">{esc(flujo[0][1])}</div>
  </div>
</section>
<section class="seccion celeste" aria-labelledby="sd-t">
  <div class="contenedor">
    <p class="antetitulo">Datos de la red</p>
    <h2 id="sd-t" data-aparece>Cobertura por subregión</h2>
    <div style="margin-top:28px">{grafica_barras('s-sub', 'Cámaras y municipios por subregión', datos_sub['metricas'], ['Cámaras', 'Municipios'], NOTA_DATOS)}</div>
  </div>
</section>'''
    pagina('proyectos/seguridad-ciudadana.html', 'Red departamental de seguridad', 'Recorrido 3D de la red de cámaras de seguridad de Antioquia y su nodo departamental.', 'proyectos', cuerpo,
           json_bloques=json_tag('s-sub', datos_sub) + json_tag('s-cam', datos_cam), vista='seguridad')


# ---------------------------------------------------------------- institucionales
def cabeza(r, titulo, migas, ante, entrada=''):
    ol = ''.join(f'<li><a href="{r}{h}">{n}</a></li>' if h else f'<li aria-current="page">{n}</li>' for n, h in migas)
    e = f'<p class="entrada" style="color:#c9d4e6">{entrada}</p>' if entrada else ''
    return f'<section class="cabeza-pagina"><div class="contenedor"><nav class="migas" aria-label="Ruta de navegación"><ol>{ol}</ol></nav><p class="antetitulo">{ante}</p><h1>{titulo}</h1>{e}</div></section>'


def transparencia():
    cats = [('Información de la entidad', 'Misión, visión, estructura, procesos, directorios y junta directiva.'), ('Normativa', 'Normas aplicables, decisiones y buscador de normas.'),
            ('Contratación', 'Plan anual de adquisiciones, procesos y ejecución contractual.'), ('Planeación, presupuesto e informes', 'Presupuesto, ejecución, planes e informes de gestión y control.'),
            ('Trámites', 'Mecanismos para presentar solicitudes, quejas y reclamos.'), ('Participa', 'Participación ciudadana y rendición de cuentas.'),
            ('Datos abiertos', 'Instrumentos de gestión de la información y datos abiertos.'), ('Información para grupos de interés', 'Información para niñas, niños, adolescentes, mujeres y otros grupos.'),
            ('Reporte de información específica', 'Estados financieros y certificados de accesibilidad.'), ('Información tributaria', 'Aplicabilidad de la información tributaria territorial.'),
            ('Atención y servicios a la ciudadanía', 'Canales de atención, política de servicio y carta de trato digno.'), ('Noticias', 'Boletines y comunicados.'),
            ('Condiciones técnicas y seguridad web', 'Políticas de seguridad digital e incidentes.')]
    items = ''.join(f'<a class="cat" id="t{i + 1}" href="#t{i + 1}" data-aparece style="--d:{i * 30}"><span class="n" aria-hidden="true">{i + 1}</span><span><h3>{i + 1}. {t}</h3><p>{d}</p></span></a>' for i, (t, d) in enumerate(cats))
    cuerpo = cabeza('', 'Transparencia y acceso a la información pública', [('Inicio', 'index.html'), ('Transparencia', None)], 'Ley 1712 de 2014 · Resolución MinTIC 1519 de 2020',
                    'Información pública de Valor+ organizada en las 13 categorías del Índice de Transparencia y Acceso a la Información (ITA).') + f'''
<section class="seccion"><div class="contenedor">
  <p class="nota">Última actualización: {ACTUALIZADO} · Responsable: <a href="mailto:transparencia@valormas.gov.co">transparencia@valormas.gov.co</a> · En el prototipo las categorías muestran la estructura; los documentos se migran en la fase de implementación.</p>
  <h2 class="sr-only">Categorías de información</h2>
  <div class="grid g3" style="margin-top:24px">{items}</div>
</div></section>'''
    pagina('transparencia.html', 'Transparencia y acceso a la información pública', 'Información pública de Valor+ según la Ley 1712 de 2014.', 'transparencia', cuerpo, modulo=False)


def atencion():
    canales = [('formulario', 'Formulario PQRSD', '<a href="#pqrsd">Radicar en línea</a>'), ('correo', 'Correo electrónico', '<a href="mailto:pqrds@valormas.gov.co">pqrds@valormas.gov.co</a>'),
               ('telefono', 'Teléfono', '<a href="tel:+576044443747">+57 (604) 444 3747</a> ext. 204<br>Línea gratuita <a href="tel:018000415379">01 8000 415 379</a>'),
               ('ubicacion', 'Atención presencial', 'Calle 41 N.° 52-28, Edificio Edatel, piso 3, La Alpujarra, Medellín'),
               ('reloj', 'Horario', 'Lunes a jueves de 7:30 a. m. a 12:30 p. m. y de 1:30 p. m. a 5:30 p. m.; viernes de 7:30 a. m. a 1:30 p. m.'),
               ('balanza', 'Notificaciones judiciales', '<a href="mailto:notificaciones@valormas.gov.co">notificaciones@valormas.gov.co</a>')]
    c = ''.join(f'<div class="canal" data-aparece style="--d:{i * 60}">{ico(k)}<h3 style="margin:0;font-size:1.05rem">{t}</h3><p style="margin:0">{v}</p></div>' for i, (k, t, v) in enumerate(canales))
    campo = lambda id_, lab, tipo='text', req=True, extra='': f'<div class="campo"><label for="{id_}">{lab}{" *" if req else ""}</label><input id="{id_}" name="{id_}" type="{tipo}"{" required" if req else ""} aria-describedby="{id_}-error"{extra}><p class="error" id="{id_}-error" hidden></p></div>'
    cuerpo = cabeza('', 'Atención y servicios a la ciudadanía', [('Inicio', 'index.html'), ('Atención a la ciudadanía', None)], 'Estamos para servirte', 'Canales, horarios y radicación de peticiones, quejas, reclamos, sugerencias y denuncias.') + f'''
<section class="seccion"><div class="contenedor"><h2>Canales de atención</h2><div class="grid g3" style="margin-top:24px">{c}</div></div></section>
<section class="seccion celeste" id="pqrsd" aria-labelledby="pq-t"><div class="contenedor" style="max-width:820px">
  <p class="antetitulo">PQRSD</p><h2 id="pq-t">Radica tu solicitud</h2>
  <form class="formulario" data-validar>
    <div class="campo"><label for="tipo">Tipo de solicitud *</label><select id="tipo" name="tipo" required aria-describedby="tipo-error"><option value="">Selecciona una opción</option><option>Petición</option><option>Queja</option><option>Reclamo</option><option>Sugerencia</option><option>Denuncia</option><option>Solicitud de información</option></select><p class="error" id="tipo-error" hidden></p></div>
    {campo('nombre', 'Nombre completo', extra=' autocomplete="name"')}
    {campo('correo', 'Correo electrónico', 'email', extra=' autocomplete="email"')}
    <div class="campo"><label for="mensaje">Descripción *</label><textarea id="mensaje" name="mensaje" required aria-describedby="mensaje-error"></textarea><p class="error" id="mensaje-error" hidden></p></div>
    <div class="campo"><label style="display:flex;gap:10px;font-weight:500"><input type="checkbox" id="acepto" required aria-describedby="acepto-error"> Autorizo el tratamiento de mis datos personales según la <a href="politicas.html">política de datos</a> (Ley 1581 de 2012). *</label><p class="error" id="acepto-error" hidden></p></div>
    <div><button class="boton marino" type="submit">Radicar solicitud {ico('flecha')}</button></div>
    <p class="aviso-ok" tabindex="-1" hidden>Solicitud recibida. Te enviaremos el número de radicado a tu correo. (Simulación del prototipo).</p>
  </form>
</div></section>'''
    pagina('atencion-ciudadania.html', 'Atención y servicios a la ciudadanía', 'Canales de atención y radicación de PQRSD de Valor+.', 'atencion', cuerpo, modulo=False)


def participa():
    datos = {'categorias': ['Conectividad rural', 'Seguridad', 'Energía limpia', 'Recaudo', 'Datos del territorio'], 'metricas': [{'nombre': 'Votos', 'unidad': 'votos', 'valores': [42, 35, 28, 12, 19]}]}
    cuerpo = cabeza('', 'Participa', [('Inicio', 'index.html'), ('Participa', None)], 'Participación ciudadana', 'Rendición de cuentas, consulta ciudadana y espacios de diálogo.') + f'''
<section class="seccion"><div class="contenedor grid g2" style="align-items:start">
  <div><h2>Rendición de cuentas</h2><p>Cada año presentamos a la ciudadanía nuestros resultados, la ejecución de los proyectos y los planes de mejora. Consulta la estrategia, el calendario de diálogos y las memorias en <a href="transparencia.html#t6">Transparencia, categoría 6</a>.</p>
  <h2 style="margin-top:32px">Consulta ciudadana</h2><p>Antes de cada rendición de cuentas preguntamos a la ciudadanía qué temas quiere profundizar. La gráfica muestra un ejemplo de cómo se publicarían los resultados.</p></div>
  {grafica_barras('p-vot', 'Resultados de la consulta (ilustrativos)', datos['metricas'], ['Votos'], 'Datos de ejemplo para el prototipo.')}
</div></section>'''
    pagina('participa.html', 'Participa', 'Rendición de cuentas y participación ciudadana en Valor+.', 'participa', cuerpo, modulo=False, json_bloques=json_tag('p-vot', datos))


def simples():
    pagina('accesibilidad.html', 'Declaración de accesibilidad', 'Compromiso de accesibilidad de Valor+.', None, cabeza('', 'Declaración de accesibilidad', [('Inicio', 'index.html'), ('Accesibilidad', None)], 'Accesibilidad') + '''
<section class="seccion"><div class="contenedor" style="max-width:820px">
<h2>Estándares</h2><p>Este sitio busca cumplir las pautas WCAG 2.1 nivel AA adoptadas por la Resolución MinTIC 1519 de 2020 (Anexo 1) y la NTC 5854.</p>
<h2>Funciones</h2><ul><li>Enlace para saltar al contenido, navegación completa por teclado y foco visible.</li><li>Panel de accesibilidad: tamaño del texto, alto contraste y detener animaciones.</li><li>Las escenas 3D son complementarias: toda su información está en texto, en las gráficas y en tablas de datos.</li><li>Los mapas tienen un buscador de municipios usable con teclado y lector de pantalla.</li><li>Se respeta la preferencia del sistema de reducir el movimiento.</li></ul>
<h2>Reporta una barrera</h2><p>Escríbenos a <a href="mailto:pqrds@valormas.gov.co">pqrds@valormas.gov.co</a>.</p></div></section>''', modulo=False)
    pagina('politicas.html', 'Política de tratamiento de datos personales', 'Política de datos personales de Valor+.', None, cabeza('', 'Política de tratamiento de datos personales', [('Inicio', 'index.html'), ('Políticas', None)], 'Legal') + '''
<section class="seccion"><div class="contenedor" style="max-width:820px"><p>Valor+ S.A.S. trata los datos personales conforme a la Ley 1581 de 2012 y sus decretos reglamentarios. En la fase de implementación se publicará aquí la política vigente, las condiciones de uso y la política de cookies.</p></div></section>''', modulo=False)
    lista = ''.join(f'<li><a href="{r}">{esc(t)}</a></li>' for t, r in PAGINAS)
    pagina('mapa-del-sitio.html', 'Mapa del sitio', 'Todas las páginas del prototipo.', None, cabeza('', 'Mapa del sitio', [('Inicio', 'index.html'), ('Mapa del sitio', None)], 'Navegación') + f'<section class="seccion"><div class="contenedor"><ul>{lista}<li><a href="mapa-del-sitio.html">Mapa del sitio</a></li></ul></div></section>', modulo=False)


if __name__ == '__main__':
    inicio(); conectividad(); seguridad(); transparencia(); atencion(); participa(); simples()
    print(f'{len(PAGINAS)} páginas generadas')
