"""Plantilla base: <head>, barra GOV.CO, encabezado, menú, pie de página y diálogos globales."""
import json
from componentes import esc, icon, REDES, ENTIDAD, FECHA_ACTUALIZACION
from contenido import SERVICIOS

NAV = [
    ('Nosotros', 'nosotros.html', 'nosotros'),
    ('Servicios', None, 'servicios'),
    ('Casos de éxito', 'casos/index.html', 'casos'),
    ('Opinión', 'opinion/index.html', 'opinion'),
    None,
    ('Transparencia', 'transparencia/index.html', 'transparencia'),
    ('Atención al ciudadano', 'atencion-ciudadania.html', 'atencion'),
    ('Participa', 'participa.html', 'participa'),
]

PREFS_JS = ("(function(){try{var d=document.documentElement,s=localStorage,t=s.getItem('vm.theme'),c=s.getItem('vm.contrast'),"
            "f=s.getItem('vm.fs'),m=s.getItem('vm.motion'),l=s.getItem('vm.links'),g=s.getItem('vm.font');if(t)d.dataset.theme=t;"
            "if(c)d.dataset.contrast=c;if(f)d.style.setProperty('--fs-scale',f);if(l)d.dataset.links=l;if(g)d.dataset.font=g;"
            "d.dataset.motion=m||(matchMedia('(prefers-reduced-motion: reduce)').matches?'reduce':'full');}catch(e){}})();")


def cabeza(r, titulo, desc, extra=''):
    t = 'Valor+ | Tecnología para el sector público' if titulo is None else f'{titulo} | Valor+'
    return f'''<!doctype html>
<html lang="es-CO" class="no-js" data-root="{r}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(t)}</title>
<meta name="description" content="{esc(desc)}">
<meta name="theme-color" content="#0c264c">
<meta property="og:type" content="website">
<meta property="og:locale" content="es_CO">
<meta property="og:site_name" content="Valor+ S.A.S.">
<meta property="og:title" content="{esc(t)}">
<meta property="og:description" content="{esc(desc)}">
<meta name="robots" content="noindex">
<link rel="icon" href="{r}assets/img/marca/favicon.svg" type="image/svg+xml">
<link rel="manifest" href="{r}manifest.webmanifest">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Montserrat:wght@600;700;800;900&amp;family=Work+Sans:wght@400;500;600;700&amp;display=swap">
<link rel="stylesheet" href="{r}assets/css/estilos.css">
<script>{PREFS_JS}</script>
<script src="{r}assets/js/app.js" defer></script>
<link rel="modulepreload" href="{r}assets/js/vendor/three.module.min.js">
<script type="module" src="{r}assets/js/tres.js"></script>
{extra}</head>'''


def mega_menu(r):
    items = ''.join(
        f'<li class="mega-item" style="--i:{i}"><a href="{r}servicios/{s["slug"]}.html"><img src="{r}assets/img/{s["img"]}" alt="" width="52" height="52" loading="lazy"><strong>{esc(s["nombre"])}</strong></a></li>'
        for i, s in enumerate(SERVICIOS))
    return f'''<div class="mega" id="mega-servicios">
  <div class="container">
    <div class="mega-intro">
      <p class="eyebrow">Servicios</p>
      <h2 class="h3">Nuestra tecnología a su servicio</h2>
      <p>Integramos servicios y procesos tecnológicos para entidades públicas y privadas.</p>
      <a class="link-arrow" href="{r}servicios/index.html">Ver todos los servicios {icon('flecha')}</a>
    </div>
    <ul class="mega-grid">{items}</ul>
  </div>
</div>'''


def encabezado(r, activo):
    lis = []
    for item in NAV:
        if item is None:
            lis.append('<li class="nav-sep" aria-hidden="true"></li>')
            continue
        nombre, href, clave = item
        cur = ' aria-current="page"' if clave == activo else ''
        inst = ' class="nav-inst"' if clave in ('transparencia', 'atencion', 'participa') else ''
        if href is None:
            cur_s = ' aria-current="true"' if activo == 'servicios' else ''
            lis.append(f'<li><button class="nav-link" type="button" data-mega aria-expanded="false" aria-controls="mega-servicios"{cur_s}>Servicios {icon("chev", "chev")}</button></li>')
        else:
            lis.append(f'<li{inst}><a href="{r}{href}"{cur}>{esc(nombre)}</a></li>')
    return f'''<a class="skip-link" href="#contenido">Saltar al contenido principal</a>
<div class="scroll-progress" aria-hidden="true"></div>
<div class="govco-bar" role="region" aria-label="Barra del portal GOV.CO">
  <div class="container">
    <a href="https://www.gov.co/" target="_blank" rel="noopener"><img src="{r}assets/img/marca/govco.svg" alt="GOV.CO, portal único del Estado colombiano (abre en una pestaña nueva)" width="101" height="22"></a>
  </div>
</div>
<header class="site-header">
  <div class="container">
    <a class="brand" href="{r}index.html" aria-label="Valor+, ir a la página de inicio">
      <img class="logo-pos keep-color" src="{r}assets/img/marca/logo-valormas.svg" alt="" width="190" height="34">
      <img class="logo-neg keep-color" src="{r}assets/img/marca/logo-valormas-negativo.svg" alt="" width="190" height="34">
    </a>
    <nav class="main-nav" aria-label="Menú principal">
      <ul>{''.join(lis)}</ul>
    </nav>
    <div class="header-actions">
      <a class="icon-btn" href="{r}buscar.html" data-open-search aria-label="Buscar en el sitio (atajo: Control + K)">{icon('buscar')}</a>
      <span class="kbd" aria-hidden="true">Ctrl K</span>
      <button class="icon-btn" type="button" data-theme-toggle aria-label="Cambiar entre tema claro y oscuro">{icon('luna')}</button>
      <button class="icon-btn" type="button" data-open-a11y aria-haspopup="dialog" aria-label="Opciones de accesibilidad">{icon('accesibilidad')}</button>
      <button class="icon-btn nav-toggle" type="button" aria-expanded="false" aria-controls="menu-movil" aria-label="Abrir menú">{icon('menu')}</button>
    </div>
  </div>
  {mega_menu(r)}
</header>
{menu_movil(r)}'''


def menu_movil(r):
    serv = ''.join(f'<li><a href="{r}servicios/{s["slug"]}.html">{esc(s["nombre"])}</a></li>' for s in SERVICIOS)
    grupo = lambda t: f'<li class="mm-group" aria-hidden="true">{t}</li>'
    link = lambda t, h: f'<li><a href="{r}{h}">{t}</a></li>'
    return f'''<div class="mobile-menu" id="menu-movil" role="dialog" aria-modal="true" aria-label="Menú principal">
  <div class="container">
    <div class="mm-head">
      <a class="brand" href="{r}index.html" aria-label="Valor+, ir a la página de inicio"><img class="logo-pos keep-color" src="{r}assets/img/marca/logo-valormas.svg" alt="" width="170" height="30"><img class="logo-neg keep-color" src="{r}assets/img/marca/logo-valormas-negativo.svg" alt="" width="170" height="30"></a>
      <button class="icon-btn mm-close" type="button" aria-label="Cerrar menú">{icon('cerrar')}</button>
    </div>
    <nav aria-label="Menú principal (móvil)">
      <ul>
        {grupo('Valor+')}
        {link('Inicio', 'index.html')}
        {link('Nosotros', 'nosotros.html')}
        <li><a href="{r}servicios/index.html">Servicios</a><ul class="sub">{serv}</ul></li>
        {link('Casos de éxito', 'casos/index.html')}
        {link('Opinión', 'opinion/index.html')}
        {link('Contáctanos', 'contacto.html')}
        {grupo('Transparencia y atención')}
        {link('Transparencia y acceso a la información pública', 'transparencia/index.html')}
        {link('Atención y servicios a la ciudadanía', 'atencion-ciudadania.html')}
        {link('PQRSD', 'pqrsd.html')}
        {link('Participa', 'participa.html')}
        {grupo('Oportunidades')}
        {link('Registro de proveedores', 'proveedores.html')}
        {link('Trabaja con nosotros', 'hojas-de-vida.html')}
        {link('Convocatorias públicas y abreviadas', 'convocatorias.html')}
        {link('Invitación abierta', 'invitacion-abierta.html')}
      </ul>
    </nav>
  </div>
</div>'''


def pie(r):
    e = ENTIDAD
    redes = ''.join(f'<a href="{u}" target="_blank" rel="noopener" aria-label="{n} de Valor+ (abre en una pestaña nueva)">{icon(k)}</a>' for k, n, u in REDES)
    return f'''<footer class="site-footer">
  <div class="container">
    <div class="footer-grid">
      <div class="footer-brand">
        <img class="keep-color" src="{r}assets/img/marca/logo-valormas-negativo.svg" alt="Valor+" width="220" height="40">
        <p>Somos creadores e integradores de soluciones basadas en tecnología y procesos para entidades públicas y privadas.</p>
        <div class="socials">{redes}</div>
      </div>
      <div>
        <h2>Contacto</h2>
        <address>
          <span><strong>{e["nombre"]}</strong></span>
          <span>{e["direccion"]}</span>
          <span>Código postal: <span class="pendiente">por confirmar</span></span>
          <span>Horario de atención: {e["horario"]}</span>
          <span>Conmutador: <a href="{e["tel_href"]}">{e["telefono"]}</a></span>
          <span>Línea gratuita nacional: <a href="{e["lg_href"]}">{e["linea_gratuita"]}</a></span>
        </address>
      </div>
      <div>
        <h2>Canales oficiales</h2>
        <ul>
          <li>PQRSD: <a href="mailto:{e["pqrsd"]}">{e["pqrsd"]}</a></li>
          <li>Solicitudes de información: <a href="mailto:{e["recepcion"]}">{e["recepcion"]}</a></li>
          <li>Notificaciones judiciales: <a href="mailto:{e["notificaciones"]}">{e["notificaciones"]}</a></li>
          <li>Línea anticorrupción: <a href="{e["tel_href"]}">{e["telefono"]}</a> · <a href="mailto:{e["transparencia"]}">{e["transparencia"]}</a></li>
        </ul>
      </div>
      <div>
        <h2>Enlaces de interés</h2>
        <ul>
          <li><a href="{r}transparencia/index.html">Transparencia y acceso a la información</a></li>
          <li><a href="{r}pqrsd.html">Radicar o consultar una PQRSD</a></li>
          <li><a href="{r}participa.html">Participa</a></li>
          <li><a href="{r}proveedores.html">Registro de proveedores</a></li>
          <li><a href="{r}hojas-de-vida.html">Trabaja con nosotros</a></li>
          <li><a href="{r}convocatorias.html">Convocatorias públicas y abreviadas</a></li>
          <li><a href="{r}invitacion-abierta.html">Invitación abierta</a></li>
        </ul>
      </div>
    </div>
    <div class="footer-bottom">
      <p>© <span data-year>2026</span> Valor+ S.A.S. Todos los derechos reservados. Última actualización: {FECHA_ACTUALIZACION}.</p>
      <ul>
        <li><a href="{r}politicas.html">Política de tratamiento de datos personales</a></li>
        <li><a href="{r}politicas.html#condiciones">Condiciones de uso</a></li>
        <li><a href="{r}accesibilidad.html">Accesibilidad</a></li>
        <li><a href="{r}mapa-del-sitio.html">Mapa del sitio</a></li>
      </ul>
    </div>
  </div>
</footer>
<div class="govco-footer" role="region" aria-label="Pie de página GOV.CO">
  <div class="container">
    <a href="https://www.gov.co/" target="_blank" rel="noopener"><img class="keep-color" src="{r}assets/img/marca/co-govco.png" alt="Marca país Colombia y GOV.CO (abre el portal GOV.CO en una pestaña nueva)" width="172" height="40"></a>
    <p>Prototipo de rediseño · Contenido tomado de valormas.gov.co</p>
  </div>
</div>'''


def dialogos(r):
    filtros = [('todo', 'Todo'), ('pagina', 'Páginas'), ('servicio', 'Servicios y casos'), ('doc', 'Transparencia'), ('proceso', 'Contratación')]
    chips = ''.join(f'<button type="button" class="chip" data-f="{k}" aria-pressed="{str(k == "todo").lower()}">{n}</button>' for k, n in filtros)
    seg_fs = ''.join(f'<button type="button" data-fs="{v}" aria-pressed="false">{n}</button>' for v, n in [('0.9', 'A−'), ('1', 'A'), ('1.15', 'A+'), ('1.3', 'A++')])
    seg_th = ''.join(f'<button type="button" data-theme-set="{v}" aria-pressed="false">{n}</button>' for v, n in [('auto', 'Sistema'), ('light', 'Claro'), ('dark', 'Oscuro')])
    sw = lambda k, t, d: f'<div class="toggle-row"><span id="sw-{k}"><strong>{t}</strong><br><span class="small muted">{d}</span></span><button type="button" class="switch" role="switch" aria-checked="false" aria-labelledby="sw-{k}" data-sw="{k}"></button></div>'
    return f'''<dialog id="paleta" class="palette" aria-label="Buscar en el sitio">
  <div class="palette-head">
    {icon('buscar')}
    <label class="sr-only" for="paleta-q">Buscar páginas, servicios, casos y documentos</label>
    <input id="paleta-q" type="search" placeholder="Buscar páginas, servicios, casos y documentos…" autocomplete="off" spellcheck="false" role="combobox" aria-expanded="true" aria-controls="paleta-res" aria-autocomplete="list">
    <button type="button" class="icon-btn" data-close aria-label="Cerrar búsqueda">{icon('cerrar')}</button>
  </div>
  <div class="palette-filters" role="group" aria-label="Filtrar resultados">{chips}</div>
  <ul id="paleta-res" class="palette-results" role="listbox" aria-label="Resultados de búsqueda"></ul>
  <div class="palette-foot" aria-hidden="true"><span><span class="kbd">↑</span> <span class="kbd">↓</span> navegar</span><span><span class="kbd">Enter</span> abrir</span><span><span class="kbd">Esc</span> cerrar</span><span><span class="kbd">/</span> o <span class="kbd">Ctrl K</span> abrir desde cualquier página</span></div>
</dialog>
<dialog id="accesibilidad" class="a11y-panel" aria-labelledby="a11y-t">
  <header><h2 id="a11y-t">Accesibilidad</h2><button type="button" class="icon-btn" data-close aria-label="Cerrar opciones de accesibilidad">{icon('cerrar')}</button></header>
  <div class="a11y-body">
    <div class="a11y-group"><h3>Tamaño del texto</h3><div class="seg" role="group" aria-label="Tamaño del texto">{seg_fs}</div></div>
    <div class="a11y-group"><h3>Tema</h3><div class="seg" role="group" aria-label="Tema de color">{seg_th}</div></div>
    <div class="a11y-group"><h3>Ajustes</h3>
      {sw('contrast', 'Alto contraste', 'Fondo negro, texto blanco y enlaces amarillos.')}
      {sw('motion', 'Detener animaciones', 'Quita movimientos, transiciones y animaciones automáticas.')}
      {sw('links', 'Subrayar enlaces', 'Hace más fácil identificar los enlaces.')}
      {sw('font', 'Fuente de lectura fácil', 'Letra más amplia, con mayor espacio entre palabras.')}
    </div>
    <button type="button" class="btn ghost" data-a11y-reset>Restablecer preferencias</button>
    <p class="small muted">Este sitio busca cumplir las pautas WCAG 2.1 nivel AA (Resolución MinTIC 1519 de 2020, Anexo 1). <a href="{r}accesibilidad.html">Conoce nuestra declaración de accesibilidad</a>.</p>
  </div>
</dialog>
<section id="cookies" class="cookie" hidden aria-labelledby="cookies-t">
  <h2 id="cookies-t">Uso de cookies</h2>
  <p>Usamos cookies necesarias para que el sitio funcione y, si lo autorizas, cookies de medición para mejorar la experiencia. Consulta la <a href="{r}politicas.html">política de tratamiento de datos personales</a>.</p>
  <div class="btn-row"><button type="button" class="btn sm" data-cookies="todas">Aceptar todas</button><button type="button" class="btn ghost sm" data-cookies="necesarias">Solo necesarias</button></div>
</section>
<button type="button" class="to-top" aria-label="Volver al inicio de la página">
  <svg viewBox="0 0 52 52" aria-hidden="true" style="position:absolute;inset:0;width:52px;height:52px;transform:rotate(-90deg)"><circle class="p" cx="26" cy="26" r="22" fill="none" stroke="#b8d430" stroke-width="3" stroke-dasharray="138" stroke-dashoffset="138"/></svg>
  {icon('arriba')}
</button>'''


def page_hero(r, titulo, migas, eyebrow=None, lead=None, img=None, meta=None, extra='', vt=None):
    ol = ''.join(
        (f'<li><a href="{r}{h}">{esc(n)}</a></li>' if h else f'<li aria-current="page">{esc(n)}</li>') for n, h in migas)
    im = ''
    if img:
        st = f' style="view-transition-name:{vt}"' if vt else ''
        im = f'<img class="hero-img" src="{r}assets/img/{img}" alt="" width="340" height="340"{st}>'
    ey = f'<p class="eyebrow">{eyebrow}</p>' if eyebrow else ''
    le = f'<p class="lead">{lead}</p>' if lead else ''
    me = f'<div class="page-meta">{meta}</div>' if meta else ''
    return f'''<section class="page-hero{' has-img' if img else ''}">
  <div class="aurora" aria-hidden="true"><span></span><span></span><span></span></div>
  <div class="container">
    <nav class="breadcrumb" aria-label="Ruta de navegación"><ol>{ol}</ol></nav>
    {ey}
    <h1 class="split-words">{titulo}</h1>
    {le}{me}{extra}
  </div>
  {im}
  <button type="button" class="icon-btn hero-pause" aria-pressed="false" aria-label="Pausar animación de fondo">{icon('pausa')}</button>
</section>'''


def documento(r, titulo, desc, cuerpo, activo=None, extra_head=''):
    return f'''{cabeza(r, titulo, desc, extra_head)}
<body>
{encabezado(r, activo)}
<main id="contenido" tabindex="-1">
{cuerpo}
</main>
{pie(r)}
{dialogos(r)}
</body>
</html>
'''


def json_ld_organizacion():
    e = ENTIDAD
    data = {
        '@context': 'https://schema.org', '@type': 'GovernmentOrganization', 'name': 'Valor+ S.A.S.',
        'url': 'https://valormas.gov.co/', 'email': e['recepcion'], 'telephone': '+57 604 444 3747',
        'address': {'@type': 'PostalAddress', 'streetAddress': 'Calle 41 N.° 52 – 28, Edificio Edatel, piso 3',
                    'addressLocality': 'Medellín', 'addressRegion': 'Antioquia', 'addressCountry': 'CO'},
        'sameAs': [u for _, _, u in REDES],
    }
    return f'<script type="application/ld+json">{json.dumps(data, ensure_ascii=False)}</script>\n'
