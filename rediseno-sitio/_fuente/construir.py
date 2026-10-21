#!/usr/bin/env python3
"""Genera el prototipo HTML del rediseño de valormas.gov.co.

Uso:  python3 _fuente/construir.py
Lee el contenido extraído del sitio actual (_fuente/contenido) y escribe las páginas
estáticas en la raíz de rediseno-sitio/. No requiere dependencias externas.
"""
import json
import re
from pathlib import Path

from componentes import esc, icon, fix, ENTIDAD, REDES, FECHA_ACTUALIZACION, extension
from contenido import (SERVICIOS, SERVICIO_POR_SLUG, casos as cargar_casos, transparencia as cargar_transparencia,
                       mision_vision, procesos, participa as cargar_participa, columna, CATEGORIAS)
from plantilla import documento, page_hero, json_ld_organizacion

BASE = Path(__file__).resolve().parent.parent
CASOS = cargar_casos()
TRANSP = cargar_transparencia()
MV = mision_vision()
INDICE = []          # índice de búsqueda
PAGINAS = []         # registro para el mapa del sitio
CUR = ' aria-current="page"'


def escribir(ruta, html):
    destino = BASE / ruta
    destino.parent.mkdir(parents=True, exist_ok=True)
    destino.write_text(html, encoding='utf-8')


def registrar(ruta, titulo, grupo, desc=''):
    PAGINAS.append((grupo, titulo, ruta))
    INDICE.append({'t': titulo, 's': desc[:120], 'u': ruta, 'k': 'pagina'})


def raiz(ruta):
    return '../' * ruta.count('/')


def flecha():
    return icon('flecha', 'arrow')


def href_doc(r, d):
    return (r + d['local']) if d.get('local') else d['href']


def doc_item(r, d):
    externo = not d.get('local')
    ext = d.get('ext', 'web')
    nombre_ext = {'web': 'Enlace', 'pdf': 'PDF', 'xlsx': 'Excel', 'xls': 'Excel', 'docx': 'Word', 'doc': 'Word',
                  'pptx': 'PowerPoint', 'zip': 'ZIP', 'csv': 'CSV', 'rar': 'RAR'}.get(ext, ext.upper())
    fecha = f'<span class="d">Fecha de publicación: {esc(d["fecha"])}</span>' if d.get('fecha') else ''
    nueva = ' (abre en una pestaña nueva)' if externo else ''
    tgt = ' target="_blank" rel="noopener"' if externo else ''
    ico = icon('externo' if ext == 'web' else 'descarga', 'dl')
    return (f'<li class="doc"><a href="{esc(href_doc(r, d))}"{tgt}><span class="ft {ext}" aria-hidden="true">{"WEB" if ext == "web" else ext.upper()}</span>'
            f'<span class="t">{esc(d["titulo"])}<span class="sr-only">, {nombre_ext}{nueva}</span>{fecha}</span>{ico}</a></li>')


def render_bloques(r, bloques, id_base='', usados=None):
    """Bloques genéricos → HTML. Los años abren acordeones (el más reciente abierto)."""
    out, docs, anio_abierto, primer_anio = [], [], False, True

    def cerrar_docs():
        nonlocal docs
        if docs:
            out.append('<ul class="docs">' + ''.join(doc_item(r, d) for d in docs) + '</ul>')
            docs = []

    def cerrar_anio():
        nonlocal anio_abierto
        cerrar_docs()
        if anio_abierto:
            out.append('</div></details>')
            anio_abierto = False

    usados = set() if usados is None else usados
    nivel = 2
    for b in bloques:
        k = b['k']
        if k == 'doc':
            docs.append(b)
            continue
        if k == 'anio':
            cerrar_anio()
            out.append(f'<details class="acc year-tabs"{" open" if primer_anio else ""}><summary>Vigencia {esc(b["text"])}</summary><div class="acc-body">')
            anio_abierto, primer_anio = True, False
            continue
        if k == 'h':
            cerrar_anio()
            primer_anio = True
            if b['num']:
                hid = 's-' + b['num'].replace('.', '-')
                while hid in usados:
                    hid += 'b'
                usados.add(hid)
                tag = 'h3' if b['depth'] <= 3 else 'h4'
                nivel = int(tag[1])
                out.append(f'<{tag} id="{hid}">{esc(b["num"])} {esc(b["text"])}</{tag}>')
            else:
                tag = f'h{min(nivel + 1, 4)}'
                out.append(f'<{tag}>{esc(b["text"])}</{tag}>')
            continue
        cerrar_docs()
        if k == 'p':
            out.append(f'<p>{esc(b["text"])}</p>')
        elif k == 'label':
            out.append(f'<p><strong>{esc(b["text"])}</strong></p>')
        elif k == 'link':
            lab = f'{esc(b["label"])}: ' if b['label'] else ''
            out.append(f'<p>{lab}<a href="{esc(b["href"])}">{esc(b["text"])}</a></p>')
        elif k == 'lista':
            out.append('<ul class="compact-list">' + ''.join(f'<li>{esc(x)}</li>' for x in b['items']) + '</ul>')
        elif k == 'tabla':
            filas = ''
            for f in b['filas']:
                celdas = ''
                for c in f:
                    if c.get('href'):
                        celdas += f'<td><a href="{esc(c["href"])}" target="_blank" rel="noopener">{esc(c["text"])}</a></td>'
                    else:
                        celdas += f'<td>{esc(c["text"])}</td>'
                filas += f'<tr>{celdas}</tr>'
            cab = ''.join(f'<th scope="col">{esc(c)}</th>' for c in b['cab'])
            out.append(f'<div class="table-wrap prose" tabindex="0" role="region" aria-label="Tabla: {esc(" · ".join(b["cab"]))} (desplazable)"><table><thead><tr>{cab}</tr></thead><tbody>{filas}</tbody></table></div>')
    cerrar_anio()
    return '\n'.join(out)


# ===========================================================================
# Inicio
# ===========================================================================
def caso_card(r, c, vt=True, reveal=True):
    serv = ' · '.join(SERVICIO_POR_SLUG[s]['corto'] for s in c['servicios'])
    st = f' style="view-transition-name:caso-{c["slug"]}"' if vt else ''
    resumen = esc(c['resumen']) if c['resumen'] else '<span class="pendiente">Contenido pendiente</span>'
    rv = ' data-reveal' if reveal else ''
    return f'''<article class="card case-card hover spotlight"{rv} data-tags="{' '.join(c['servicios'])}">
  <div class="media"><img src="{r}assets/img/{c['img']}" alt="" width="300" height="300" loading="lazy"{st}></div>
  <div class="body"><span class="badge">{esc(serv)}</span><h3><a href="{r}casos/{c['slug']}.html">{esc(c['titulo'])}</a></h3><p>{resumen}</p></div>
</article>'''


def pagina_inicio():
    r = ''
    orb = ''.join(f'<li style="--i:{i}"><img src="assets/img/{s["img"]}" alt="" width="64" height="64"></li>' for i, s in enumerate(SERVICIOS))
    plus = json.loads((BASE / '_fuente' / 'contenido' / 'logo_plus.json').read_text())['d']
    stats = [
        ('4', '$', 'billones', 'recaudados del impuesto vehicular de Antioquia entre 2021 y 2026', 'opinion/impuesto-vehicular-valor-y-politica-social.html', 'Ver la columna'),
        ('900', '', '+', 'cámaras integradas al nodo departamental de seguridad en 48 municipios', 'casos/nodos-seguridad.html', 'Ver el caso'),
        ('925', '', '', 'sedes educativas rurales con servicio de internet operativo', 'casos/conectividad.html', 'Ver el caso'),
        ('94000', '', '', 'cajas en custodia y más de 1,5 millones de imágenes digitalizadas', 'casos/gestion-documental.html', 'Ver el caso'),
        ('758', '', '', 'sensores de iluminación inteligente en la vía Las Palmas', 'casos/telegestion-las-palmas.html', 'Ver el caso'),
        ('2161', '', '', 'usuarios actualizados en distritos de adecuación de tierras de la ADR', 'casos/gestion-territorial-adr.html', 'Ver el caso'),
    ]
    stats_html = ''.join(
        f'<div class="stat" data-reveal style="--d:{i * 90}"><p class="num"><span class="grad-text">{pre}<span data-count="{n}">{int(n):,}</span>{(" <span class=suf>" + suf + "</span>") if len(suf) > 1 else suf}</span></p>'.replace(',', '.') +
        f'<p>{esc(t)}</p><a class="link-arrow" href="{u}">{l}<span class="sr-only">: {esc(t)}</span> {flecha()}</a></div>'
        for i, (n, pre, suf, t, u, l) in enumerate(stats))
    figs = ''.join(f'<figure style="--c:{s["color"]}"><img src="assets/img/{s["img"]}" alt="" width="360" height="360" loading="lazy"><figcaption aria-hidden="true">0{i + 1}</figcaption></figure>' for i, s in enumerate(SERVICIOS))
    pasos = ''.join(f'''<article class="scrolly-step">
  <img class="mobile-img" src="assets/img/{s["img"]}" alt="" width="120" height="120" loading="lazy">
  <span class="num">0{i + 1} / 0{len(SERVICIOS)}</span>
  <h3>{esc(s["nombre"])}</h3>
  <ul>{''.join(f"<li>{esc(c)}</li>" for c in s["capacidades"])}</ul>
  <a class="link-arrow" href="servicios/{s["slug"]}.html">Conocer el servicio<span class="sr-only">: {esc(s["nombre"])}</span> {flecha()}</a>
</article>''' for i, s in enumerate(SERVICIOS))
    rail = ''.join(caso_card(r, c, vt=False, reveal=False) for c in CASOS.values() if not c.get('pendiente'))
    total_docs = sum(c['docs'] for c in TRANSP['categorias'])
    clientes = [('Municipio de La Pintada', 1), ('Alcaldía de La Estrella', 2), ('Alcaldía de El Carmen de Viboral', 3),
                ('Fábrica de Licores y Alcoholes de Antioquia', 4), ('IU Digital de Antioquia', 5), ('Ferrocarril de Antioquia', 6),
                ('IDEA, Instituto para el Desarrollo de Antioquia', 7), ('CrediAntioquia', 8), ('Gobernación de Antioquia', 9),
                ('Alcaldía de Medellín', 10), ('Institución Universitaria Pascual Bravo', 11), ('Policía Nacional de Colombia', 12),
                ('Secretaría de Seguridad y Justicia', 13), ('Secretaría de Educación', 14), ('Secretaría de Suministros y Servicios', 15),
                ('Municipio de Montebello', 16)]
    logos = ''.join(f'<li><img src="assets/img/clientes/cliente-{n:02d}.webp" alt="{esc(a)}" width="160" height="100" loading="lazy"></li>' for a, n in clientes)
    redes = ''.join(f'<a class="btn ghost" href="{u}" target="_blank" rel="noopener">{icon(k)} {n}<span class="sr-only"> (abre en una pestaña nueva)</span></a>' for k, n, u in REDES)
    cuerpo = f'''
<section class="hero" aria-labelledby="hero-t">
  <div class="aurora" aria-hidden="true"><span></span><span></span><span></span><span></span></div>
  <canvas class="net" aria-hidden="true"></canvas>
  <div class="grain" aria-hidden="true"></div>
  <div class="container hero-grid">
    <div class="hero-inner">
      <p class="eyebrow">Nuestra tecnología a su servicio</p>
      <h1 id="hero-t" class="split-words">¡Somos especialistas en la integración de servicios y procesos <span class="hl">tecnológicos!</span></h1>
      <p class="lead" data-reveal style="--d:700">Comprendemos el funcionamiento del sector público; por eso, traducimos sus necesidades en soluciones articuladas con el sector privado.</p>
      <div class="btn-row" data-reveal style="--d:900">
        <a class="btn" href="servicios/index.html" data-magnetic>Conoce nuestros servicios {flecha()}</a>
        <a class="btn ghost" href="nosotros.html">Conoce más sobre nosotros</a>
      </div>
    </div>
    <div class="hero-orb" aria-hidden="true">
      <div class="orb-ring"></div>
      <div class="orb-core"><svg class="orb-plus" viewBox="216 22 22 20"><path fill="#b8d430" d="{plus}"/></svg></div>
      <ul class="orb-orbit">{orb}</ul>
    </div>
  </div>
  <button type="button" class="icon-btn hero-pause" aria-pressed="false" aria-label="Pausar animación de fondo">{icon('pausa')}</button>
  <a class="scroll-cue" href="#aliado"><i aria-hidden="true"></i>Desliza</a>
</section>

<section id="aliado" class="section" aria-labelledby="aliado-t">
  <div class="container center">
    <h2 id="aliado-t" class="sr-only">Quiénes somos</h2>
    <p class="statement">Somos el aliado estratégico del <span class="hl">sector público y privado</span> para brindar <span class="hl">soluciones + innovadoras</span> basadas en tecnología.</p>
    <p class="badge blue" data-reveal style="margin-top:2.5rem;font-size:.85rem;padding:.7em 1.2em">{icon('escudo')} Contamos con habilitación del Ministerio de Tecnologías de la Información y las Comunicaciones (MinTIC)</p>
  </div>
</section>

<section class="section soft" aria-labelledby="cifras-t">
  <div class="container">
    <p class="eyebrow">Impacto</p>
    <h2 id="cifras-t" data-reveal>Cifras destacadas</h2>
    <p class="lead" data-reveal>Datos publicados en los casos de éxito de Valor+.</p>
    <div class="stats" style="margin-top:2.5rem">{stats_html}</div>
  </div>
</section>

<section class="zoom-stage" aria-labelledby="zoom-t">
  <div class="zoom-sticky">
    <div class="zoom-title container"><p class="eyebrow">Conectividad rural</p><h2 id="zoom-t">Llevamos internet a comunidades donde antes no era posible conectarse.</h2></div>
    <div class="zoom-card">
      <img src="assets/img/general/conectividad-comunidades.webp" alt="Dos jóvenes sonríen mientras uno de ellos usa su teléfono celular." width="1010" height="535" loading="lazy">
      <div class="zoom-copy">
        <p>El proyecto busca reducir la brecha digital de las comunidades educativas rurales, a través de acciones de reactivación de los servicios de conectividad a internet en un aproximado de 1.228 sedes educativas.</p>
        <a class="btn light" href="casos/conectividad-satelital.html">Conoce el impacto {flecha()}</a>
      </div>
    </div>
  </div>
</section>

<section class="section" aria-labelledby="serv-t">
  <div class="container">
    <p class="eyebrow">Servicios</p>
    <h2 id="serv-t" data-reveal>Nuestra tecnología a su servicio</h2>
    <div class="scrolly" style="margin-top:2rem">
      <div class="scrolly-visual" aria-hidden="true">{figs}</div>
      <div class="scrolly-steps">{pasos}</div>
    </div>
  </div>
</section>

<section class="section soft" aria-labelledby="casos-t">
  <div class="container rail-wrap">
    <div class="rail-head">
      <div><p class="eyebrow">Casos de éxito</p><h2 id="casos-t" data-reveal>Ofertas de Valor+</h2></div>
      <div class="rail-controls">
        <button type="button" class="icon-btn" data-rail="prev" aria-label="Ver casos anteriores">{icon('flecha-izq')}</button>
        <button type="button" class="icon-btn" data-rail="next" aria-label="Ver más casos">{icon('flecha')}</button>
        <a class="btn sm ghost" href="casos/index.html">Ver todos</a>
      </div>
    </div>
    <div class="rail" tabindex="0" role="region" aria-label="Casos de éxito, desplazable horizontalmente">{rail}</div>
    <div class="rail-progress" aria-hidden="true"><span></span></div>
  </div>
</section>

<section class="section" aria-labelledby="accesos-t">
  <div class="container">
    <p class="eyebrow">Accesos rápidos</p>
    <h2 id="accesos-t" data-reveal>Información y trámites a un clic</h2>
    <div class="bento" style="margin-top:2rem" data-stagger="70">
      <a class="card navy b-wide hover spotlight" href="transparencia/index.html"><span class="go">{flecha()}</span><span class="tag badge">Ley 1712 de 2014</span><h3>Transparencia y acceso a la información pública</h3><p>{f"{total_docs:,}".replace(",", ".")} documentos publicados en 13 categorías.</p></a>
      <a class="card brand b-tall hover" href="pqrsd.html"><span class="go">{flecha()}</span><span class="card-icon" style="background:rgba(255,255,255,.18);color:#fff">{icon('chat')}</span><h3>PQRSD</h3><p>Radica y consulta peticiones, quejas, reclamos, sugerencias y denuncias.</p></a>
      <a class="card b-tall hover spotlight" href="participa.html"><span class="go">{flecha()}</span><span class="card-icon">{icon('personas')}</span><h3>Participa</h3><p>Rendición de cuentas y espacios de participación.</p></a>
      <a class="card hover spotlight" href="proveedores.html"><span class="go">{flecha()}</span><span class="card-icon">{icon('maletin')}</span><h3>Registro de proveedores</h3><p>Permítenos conocer tus servicios para entregar + valor a nuestra gestión.</p></a>
      <a class="card hover spotlight" href="hojas-de-vida.html"><span class="go">{flecha()}</span><span class="card-icon">{icon('personas')}</span><h3>Trabaja con nosotros</h3><p>Únete a nuestro equipo de trabajo.</p></a>
      <a class="card b-wide hover spotlight" href="convocatorias.html"><span class="go">{flecha()}</span><span class="card-icon">{icon('megafono')}</span><h3>Convocatorias públicas y abreviadas</h3><p>Descubre oportunidades para colaborar con nosotros en proyectos que impactan positivamente a la comunidad.</p></a>
      <a class="card b-wide hover spotlight" href="invitacion-abierta.html"><span class="go">{flecha()}</span><span class="card-icon">{icon('contrato')}</span><h3>Invitación abierta</h3><p>¡Únete a nuestras invitaciones abiertas!</p></a>
    </div>
  </div>
</section>

<section class="section soft" aria-labelledby="opinion-t">
  <div class="container split">
    <div data-reveal="left">
      <p class="eyebrow">Opinión · Última columna</p>
      <h2 id="opinion-t">Impuesto vehicular, Valor+ y política social</h2>
      <p class="lead">“Antioquia no ha dejado de generar ideas, programas, proyectos e instituciones que responden a solución de situaciones cotidianas…”</p>
      <div class="author" style="margin:1.5rem 0"><img src="assets/img/general/autor-alfazar.webp" alt="" width="64" height="64" loading="lazy"><span><strong>Félix Alfazar González Mira</strong>Asesor de la Gerencia General · 15 de octubre de 2026</span></span></div>
      <div class="btn-row"><a class="btn" href="opinion/impuesto-vehicular-valor-y-politica-social.html">Leer la columna {flecha()}</a><a class="btn ghost" href="opinion/index.html">Ver todas las columnas</a></div>
    </div>
    <div class="card tilt" data-reveal="right" style="padding:0;border-radius:var(--radius-lg)">
      <div class="prose" style="padding:clamp(20px,3vw,36px)">
        <p class="eyebrow" style="margin:0">Recaudo del impuesto vehicular</p>
        <p class="num" style="font:800 clamp(2.4rem,5vw,3.6rem)/1 var(--font-head);margin:.3em 0"><span class="grad-text">$4,0 billones</span></p>
        <p class="muted" style="margin:0">Total recaudado 2021–2026, según la columna.</p>
      </div>
    </div>
  </div>
</section>

<section class="section" aria-labelledby="equipo-t">
  <div class="container split rev">
    <figure data-reveal="scale" style="margin:0"><img src="assets/img/general/equipo-collage.webp" alt="Collage con fotografías de integrantes del equipo de Valor+ en sus puestos de trabajo." width="1308" height="611" loading="lazy" style="border-radius:var(--radius-lg)" data-parallax="0.06"></figure>
    <div data-reveal>
      <p class="eyebrow">Acerca del equipo</p>
      <h2 id="equipo-t">Personas que impulsan la transformación digital</h2>
      <p class="lead">Nuestro equipo de expertos en tecnología está comprometido con la excelencia, trabajando juntos para impulsar su éxito con soluciones innovadoras.</p>
      <a class="btn" href="nosotros.html#equipo">Conócenos {flecha()}</a>
    </div>
  </div>
</section>

<section class="section tight soft" aria-labelledby="clientes-t">
  <div class="container center">
    <p class="eyebrow">Confían en nosotros</p>
    <h2 id="clientes-t" data-reveal>Nuestros clientes</h2>
  </div>
  <div class="marquee-wrap" style="margin-top:1.5rem">
    <div class="marquee"><ul class="marquee-track" style="margin:0;padding-left:0">{logos}</ul></div>
    <button type="button" class="btn ghost sm pause-btn" aria-pressed="false">{icon('pausa')}<span>Pausar movimiento</span></button>
  </div>
</section>

<section class="section tight" aria-labelledby="siguenos-t">
  <div class="container center">
    <h2 id="siguenos-t" data-reveal>Síguenos</h2>
    <div class="btn-row" data-reveal>{redes}</div>
  </div>
</section>
'''
    escribir('index.html', documento(r, None, 'Valor+ S.A.S. integra servicios y procesos tecnológicos para el sector público y privado: recaudo, automatización, proyectos, consultoría, seguridad y energía.', cuerpo, 'inicio', json_ld_organizacion()))
    registrar('index.html', 'Inicio', 'Navegación principal', 'Valor+ integra servicios y procesos tecnológicos')


# ===========================================================================
# Nosotros
# ===========================================================================
EQUIPO = [('David Quintero', 'Gerente General', 'david-quintero'), ('Luisa Fernanda Echeverri', 'Secretaria General', 'luisa-echeverri'),
          ('Hernán Echavarría', 'Gerente de Tecnología, Innovación y Sostenibilidad', 'hernan-echavarria'),
          ('Carlos Echeverri', 'Gerente de Operaciones', 'carlos-echeverri'), ('Paula Andrea Toro Torres', 'Gerente Financiera', 'paula-toro'),
          ('Vanessa Urrea Gallo', 'Directora de Infraestructura', 'vanessa-urrea'), ('Carolina Gómez Jiménez', 'Directora Comercial', 'carolina-gomez'),
          ('Andrea Monsalve Franco', 'Directora Administrativa', 'andrea-monsalve')]


def pagina_nosotros():
    ruta = 'nosotros.html'
    r = raiz(ruta)
    equipo = ''.join(f'<li data-reveal style="--d:{i * 60}"><img src="{r}assets/img/equipo/{f}.webp" alt="Fotografía de {esc(n)}" width="480" height="600" loading="lazy"><div class="info"><strong>{esc(n)}</strong><span>{esc(c)}</span></div></li>' for i, (n, c, f) in enumerate(EQUIPO))
    valores = [('Compromiso', 'corazon'), ('Innovación', 'bombilla'), ('Excelencia', 'estrella'), ('Calidad humana', 'personas')]
    vals = ''.join(f'<div class="card value hover" data-reveal style="--d:{i * 80}"><div class="ring"><span>{icon(ic)}</span></div><h3>{n}</h3></div>' for i, (n, ic) in enumerate(valores))
    por_que = [('Orientación al servicio y el resultado', 'Vamos más allá de lo que nuestros clientes requieren, anticipándonos a sus necesidades y entregando resultados superiores.', 'objetivo'),
               ('Efectividad, oportunidad y eficiencia', 'Buscamos el camino óptimo de llegada a un objetivo, haciendo las cosas de forma eficiente.', 'rayo'),
               ('Integralidad (360°)', 'Consideramos diferentes alternativas de solución, desde la tecnología, experiencia del usuario, uso y la practicidad de su implementación.', 'datos')]
    pq = ''.join(f'<div class="card hover spotlight tilt" data-reveal style="--d:{i * 90}"><span class="card-icon">{icon(ic)}</span><h3>{t}</h3><p class="muted">{d}</p></div>' for i, (t, d, ic) in enumerate(por_que))
    vlist = lambda vs: ''.join(f'<li><strong>{esc(v["nombre"])}:</strong> {esc(v["texto"])}</li>' for v in vs)
    oes = ''.join(f'<details class="acc"{" open" if o["n"] == 1 else ""}><summary>OE {o["n"]} · {esc(o["titulo"])}</summary><div class="acc-body"><p>{esc(o["texto"])}</p></div></details>' for o in MV['objetivos'])
    cuerpo = page_hero(r, 'Trabajamos de la mano para brindarte soluciones tecnológicas', [('Inicio', 'index.html'), ('Nosotros', None)], 'Sobre nosotros',
                       esc(MV['propuesta'])) + f'''
<section class="section" aria-labelledby="proposito-t">
  <div class="container">
    <div class="split">
      <div data-reveal="left"><p class="eyebrow">Nuestro propósito</p><h2 id="proposito-t">Misión</h2><p class="lead">{esc(MV["mision"])}</p></div>
      <div data-reveal="right"><p class="eyebrow">Lo que buscamos ser</p><h2>Visión</h2><p class="lead">{esc(MV["vision"])}</p></div>
    </div>
  </div>
</section>
<section class="section soft" aria-labelledby="valores-t">
  <div class="container">
    <p class="eyebrow">Cultura</p>
    <h2 id="valores-t" data-reveal>Nuestros valores</h2>
    <div class="values" style="margin-top:2rem">{vals}</div>
    <div class="grid c2" style="margin-top:2.5rem">
      <div class="card" data-reveal><h3>Desde el ser</h3><ul class="checks">{vlist(MV["ser"])}</ul></div>
      <div class="card" data-reveal><h3>Desde el hacer</h3><ul class="checks">{vlist(MV["hacer"])}</ul></div>
    </div>
  </div>
</section>
<section class="section" aria-labelledby="porque-t">
  <div class="container">
    <p class="eyebrow">Diferenciales</p>
    <h2 id="porque-t" data-reveal>Por qué elegirnos</h2>
    <div class="grid c3" style="margin-top:2rem">{pq}</div>
  </div>
</section>
<section class="section soft" id="equipo" aria-labelledby="equipo-t">
  <div class="container">
    <p class="eyebrow">Liderazgo</p>
    <h2 id="equipo-t" data-reveal>Equipo principal</h2>
    <ul class="team" style="margin-top:2rem">{equipo}</ul>
  </div>
</section>
<section class="section" aria-labelledby="oe-t">
  <div class="container narrow">
    <p class="eyebrow">Plan estratégico</p>
    <h2 id="oe-t" data-reveal>Objetivos estratégicos</h2>
    <div style="margin-top:1.5rem" data-reveal>{oes}</div>
    <div class="btn-row" style="margin-top:2rem"><a class="btn" href="{r}transparencia/informacion-de-la-entidad.html#s-1-2">Estructura orgánica y junta directiva {flecha()}</a><a class="btn ghost" href="{r}transparencia/informacion-de-la-entidad.html#s-1-3">Mapa de procesos</a></div>
  </div>
</section>'''
    escribir(ruta, documento(r, 'Nosotros', 'Propósito, misión, visión, valores y equipo directivo de Valor+ S.A.S.', cuerpo, 'nosotros'))
    registrar(ruta, 'Nosotros', 'Navegación principal', 'Misión, visión, valores y equipo principal')


# ===========================================================================
# Servicios
# ===========================================================================
def pagina_servicios():
    ruta = 'servicios/index.html'
    r = raiz(ruta)
    cards = ''.join(f'''<article class="card hover spotlight tilt" data-reveal style="--d:{i * 70}">
  <img src="{r}assets/img/{s["img"]}" alt="" width="96" height="96" loading="lazy" style="width:96px;border-radius:50%;margin-bottom:18px">
  <h2 class="h3" style="font-size:1.3rem"><a href="{r}servicios/{s["slug"]}.html" style="color:inherit;text-decoration:none">{esc(s["nombre"])}</a></h2>
  <p class="muted">{esc(", ".join(s["capacidades"][:4]))}{"…" if len(s["capacidades"]) > 4 else "."}</p>
  <span class="link-arrow">{len(s["casos"])} {"caso" if len(s["casos"]) == 1 else "casos"} de éxito {flecha()}</span>
</article>''' for i, s in enumerate(SERVICIOS))
    cuerpo = page_hero(r, 'Nuestra tecnología a su servicio', [('Inicio', 'index.html'), ('Servicios', None)], 'Servicios',
                       'Comprendemos el funcionamiento del sector público; por eso, traducimos sus necesidades en soluciones articuladas con el sector privado.') + f'''
<section class="section"><div class="container"><div class="grid c3">{cards}</div></div></section>'''
    escribir(ruta, documento(r, 'Servicios', 'Servicios de Valor+: recaudo, automatización de la información, proyectos, consultoría, seguridad y energía limpia.', cuerpo, 'servicios'))
    registrar(ruta, 'Servicios', 'Navegación principal', 'Los seis servicios de Valor+')
    for i, s in enumerate(SERVICIOS):
        ruta = f'servicios/{s["slug"]}.html'
        r = raiz(ruta)
        caps = ''.join(f'<div class="card hover spotlight" data-reveal style="--d:{j * 60}"><span class="card-icon">{icon("check")}</span><h3 style="font-size:1.1rem;margin:0">{esc(c)}</h3></div>' for j, c in enumerate(s['capacidades']))
        cs = ''.join(caso_card(r, CASOS[c]) for c in s['casos'])
        prev_s, next_s = SERVICIOS[i - 1], SERVICIOS[(i + 1) % len(SERVICIOS)]
        cuerpo = page_hero(r, esc(s['nombre']), [('Inicio', 'index.html'), ('Servicios', 'servicios/index.html'), (s['nombre'], None)], 'Servicio',
                           f'{len(s["capacidades"])} capacidades · {len(s["casos"])} {"caso" if len(s["casos"]) == 1 else "casos"} de éxito', s['img']) + f'''
<section class="section"><div class="container">
  <p class="eyebrow">Lo que hacemos</p><h2 data-reveal>Capacidades</h2>
  <div class="grid c3" style="margin-top:1.5rem">{caps}</div>
  <p style="margin-top:1.5rem"><span class="pendiente">Pendiente: el sitio actual solo lista las capacidades; falta una descripción ampliada del servicio.</span></p>
</div></section>
<section class="section soft"><div class="container">
  <p class="eyebrow">Casos de éxito</p><h2 data-reveal>Ofertas de Valor+</h2>
  <div class="grid c3" style="margin-top:1.5rem">{cs}</div>
</div></section>
<section class="section tight"><div class="container">
  <nav aria-label="Otros servicios" class="grid c2">
    <a class="card hover" href="{r}servicios/{prev_s["slug"]}.html" style="text-decoration:none;color:inherit"><span class="muted small">Servicio anterior</span><h3 style="margin:.3em 0 0">{esc(prev_s["nombre"])}</h3></a>
    <a class="card hover" href="{r}servicios/{next_s["slug"]}.html" style="text-decoration:none;color:inherit;text-align:right"><span class="muted small">Siguiente servicio</span><h3 style="margin:.3em 0 0">{esc(next_s["nombre"])}</h3></a>
  </nav>
</div></section>'''
        escribir(ruta, documento(r, s['nombre'], f'{s["nombre"]}: {", ".join(s["capacidades"])}.', cuerpo, 'servicios'))
        PAGINAS.append(('Servicios', s['nombre'], ruta))
        INDICE.append({'t': s['nombre'], 's': ', '.join(s['capacidades']), 'u': ruta, 'k': 'servicio'})


# ===========================================================================
# Casos de éxito
# ===========================================================================
def render_caso(r, c):
    if c.get('pendiente'):
        return f'<div class="empty-note" style="font-size:1.05rem"><span class="pendiente">Contenido pendiente</span><p style="margin:.8em 0 0">{esc(c["pendiente"])}</p></div>'
    html = ''
    for b in c['bloques']:
        html += '<div class="case-block">'
        if b['titulo']:
            html += f'<h2 data-reveal>{esc(b["titulo"])}</h2>'
        for s in b['secciones']:
            tag = 'h3' if b['titulo'] else 'h2'
            if s.get('pendiente'):
                cont = f'<p><span class="pendiente">Pendiente</span> {esc(s["pendiente"])}</p>'
            elif s['nombre'] in ('Logros',):
                cont = '<ul class="checks">' + ''.join(f'<li>{esc(x)}</li>' for x in s['items']) + '</ul>'
            elif s['nombre'] == 'Cifras o datos destacables' and len(s['items']) > 1:
                items = s['items']
                cont = ''
                if items[0].endswith(':'):
                    cont, items = f'<p>{esc(items[0])}</p>', items[1:]
                cont += '<ul class="facts">' + ''.join(f'<li>{esc(x)}</li>' for x in items) + '</ul>'
            else:
                cont = ''.join(f'<p>{esc(x)}</p>' for x in s['items'])
            for f in s['figuras']:
                if 'grafica' in f or 'Grafica' in f or 'grafica-mesa' in f or 'mesa-de-servicios' in f:
                    cont += f'<figure style="margin:1rem 0 0"><img src="{r}assets/img/casos/mesa-grafica.webp" alt="Gráfica del informe de operación de la Mesa de Servicios MEGANT con el cumplimiento mensual de los acuerdos de nivel de servicio." width="1600" height="407" loading="lazy" style="border-radius:12px;background:#fff"><figcaption class="small muted">Meta mensual de cumplimiento de ANS: 95 %. Resultado de enero a diciembre: 97,49 %.</figcaption></figure>'
            html += f'<div class="case-sec" data-reveal><{tag}>{s["nombre"]}</{tag}><div class="prose">{cont}</div></div>'
        html += '</div>'
    return html


def pagina_casos():
    ruta = 'casos/index.html'
    r = raiz(ruta)
    chips = '<button type="button" class="chip" data-filter="todos" aria-pressed="true">Todos</button>' + ''.join(
        f'<button type="button" class="chip" data-filter="{s["slug"]}" aria-pressed="false">{esc(s["corto"])}</button>' for s in SERVICIOS)
    cards = ''.join(caso_card(r, c) for c in CASOS.values())
    cuerpo = page_hero(r, 'Ofertas de Valor+', [('Inicio', 'index.html'), ('Casos de éxito', None)], 'Casos de éxito',
                       f'{len(CASOS)} proyectos en los seis servicios de Valor+.') + f'''
<section class="section"><div class="container">
  <div class="chips" role="group" aria-label="Filtrar casos por servicio" data-filter-group="#lista-casos" data-status="#casos-estado">{chips}</div>
  <p id="casos-estado" class="sr-only" aria-live="polite"></p>
  <h2 class="sr-only">Listado de casos</h2>
  <div id="lista-casos" class="grid c3" style="margin-top:2rem">{cards}</div>
</div></section>'''
    escribir(ruta, documento(r, 'Casos de éxito', 'Casos de éxito y ofertas de valor de Valor+ S.A.S. en recaudo, catastro, conectividad, seguridad, consultoría y energía.', cuerpo, 'casos'))
    registrar(ruta, 'Casos de éxito', 'Navegación principal', 'Proyectos y ofertas de valor')
    lista = list(CASOS.values())
    for i, c in enumerate(lista):
        ruta = f'casos/{c["slug"]}.html'
        r = raiz(ruta)
        serv_links = ' · '.join(f'<a href="{r}servicios/{s}.html" style="color:#fff">{esc(SERVICIO_POR_SLUG[s]["nombre"])}</a>' for s in c['servicios'])
        lead = esc(' '.join(c['intro'])) if c['intro'] else (esc(c['resumen']) if c['resumen'] else None)
        if c['slug'] == 'conectividad-satelital':
            lead = 'Gerenciamiento del Fondo para la conectividad a internet de las escuelas rurales del Departamento de Antioquia.'
        if c['slug'] == 'migracion-ipv6':
            lead = 'La Gobernación de Antioquia, el Instituto para el Desarrollo de Antioquia (IDEA) e Indeportes Antioquia.'
        extra = f'<div class="btn-row" style="margin-top:1.5rem"><button type="button" class="btn light sm" data-share>{icon("compartir")} Compartir</button></div>'
        relacionados = [CASOS[x] for s in c['servicios'] for x in SERVICIO_POR_SLUG[s]['casos'] if x != c['slug']][:6]
        rel = ''.join(caso_card(r, x, vt=False, reveal=False) for x in relacionados)
        cuerpo = page_hero(r, esc(c['titulo']), [('Inicio', 'index.html'), ('Casos de éxito', 'casos/index.html'), (c['titulo'], None)],
                           serv_links, lead, c['img'], extra=extra, vt=f'caso-{c["slug"]}') + f'''
<section class="section"><div class="container narrow">{render_caso(r, c)}</div></section>
{f"""<section class="section soft"><div class="container rail-wrap"><div class="rail-head"><h2>Otros casos relacionados</h2><div class="rail-controls"><button type="button" class="icon-btn" data-rail="prev" aria-label="Anterior">{icon("flecha-izq")}</button><button type="button" class="icon-btn" data-rail="next" aria-label="Siguiente">{icon("flecha")}</button></div></div><div class="rail" tabindex="0" role="region" aria-label="Casos relacionados">{rel}</div><div class="rail-progress" aria-hidden="true"><span></span></div></div></section>""" if rel else ""}'''
        escribir(ruta, documento(r, c['titulo'], (c['resumen'] or c['titulo'])[:155], cuerpo, 'casos'))
        PAGINAS.append(('Casos de éxito', c['titulo'], ruta))
        INDICE.append({'t': c['titulo'], 's': c['resumen'], 'u': ruta, 'k': 'caso'})


# ===========================================================================
# Opinión
# ===========================================================================
def pagina_opinion():
    col = columna()
    ruta = 'opinion/index.html'
    r = raiz(ruta)
    cuerpo = page_hero(r, 'Opinión', [('Inicio', 'index.html'), ('Opinión', None)], 'Columnas', 'Todas las columnas de opinión publicadas por Valor+.') + f'''
<section class="section"><div class="container narrow">
  <article class="card hover spotlight" data-reveal>
    <div class="author"><img src="{r}assets/img/general/autor-alfazar.webp" alt="" width="64" height="64"><span><strong>Félix Alfazar González Mira</strong><span class="muted small">Asesor de la Gerencia General</span></span></div>
    <h2 style="margin-top:1rem"><a href="{r}opinion/impuesto-vehicular-valor-y-politica-social.html" style="color:inherit">Impuesto vehicular, Valor+ y política social</a></h2>
    <p class="muted"><time datetime="2026-10-15">15 de octubre de 2026</time></p>
    <p>Antioquia no ha dejado de generar ideas, programas, proyectos e instituciones que responden a solución de situaciones cotidianas, a interpretación de nuevas realidades o adelantarse a los acontecimientos…</p>
  </article>
</div></section>'''
    escribir(ruta, documento(r, 'Opinión', 'Columnas de opinión de Valor+ S.A.S.', cuerpo, 'opinion'))
    registrar(ruta, 'Opinión', 'Navegación principal', 'Columnas de opinión')

    ruta = 'opinion/impuesto-vehicular-valor-y-politica-social.html'
    r = raiz(ruta)
    filas = ''
    for f in col['filas']:
        tag = 'tfoot' if f[0] == 'Total' else ''
        celdas = f'<th scope="row">{esc(f[0])}</th>' + ''.join(f'<td>{esc(x)}</td>' for x in f[1:])
        filas += f'<tr>{celdas}</tr>' if not tag else ''
    total = next(f for f in col['filas'] if f[0] == 'Total')
    pie_t = f'<tfoot><tr><th scope="row">Total</th>{"".join(f"<td>{esc(x)}</td>" for x in total[1:])}</tr></tfoot>'
    cab = ''.join(f'<th scope="col">{esc(c)}</th>' for c in col['cab'])
    parrafos = ''.join(f'<p>{esc(p)}</p>' for p in col['antes'][:-1])
    tabla = f'<p>{esc(col["antes"][-1])}</p><div class="table-wrap" tabindex="0" role="region" aria-label="Tabla de recaudo del impuesto vehicular (desplazable)"><table><caption class="sr-only">Recaudo del impuesto vehicular de Antioquia por año, en pesos colombianos</caption><thead><tr>{cab}</tr></thead><tbody>{filas}</tbody>{pie_t}</table></div>'
    despues = ''.join(f'<p>{esc(p)}</p>' for p in col['despues'])
    meta = '<span>Por: Félix Alfazar González Mira, Asesor de la Gerencia General</span><span><time datetime="2026-10-15">15 de octubre de 2026</time></span><span>Lectura: 3 min</span>'
    extra = f'<div class="btn-row" style="margin-top:1.5rem"><button type="button" class="btn light sm" data-share>{icon("compartir")} Compartir</button></div>'
    cuerpo = page_hero(r, 'Impuesto vehicular, Valor+ y política social', [('Inicio', 'index.html'), ('Opinión', 'opinion/index.html'), ('Impuesto vehicular, Valor+ y política social', None)],
                       'Opinión', None, meta=meta, extra=extra) + f'''
<article class="section"><div class="container narrow prose">{parrafos}{tabla}{despues}
  <hr><div class="author"><img src="{r}assets/img/general/autor-alfazar.webp" alt="" width="64" height="64"><span><strong>Félix Alfazar González Mira</strong><span class="muted small">Asesor de la Gerencia General</span></span></div>
  <p class="small muted" style="margin-top:1.5rem">Las opiniones expresadas en esta columna son responsabilidad de su autor.</p>
</div></article>'''
    escribir(ruta, documento(r, 'Impuesto vehicular, Valor+ y política social', 'Columna de opinión de Félix Alfazar González Mira sobre el impuesto vehicular de Antioquia y su destinación social.', cuerpo, 'opinion'))
    PAGINAS.append(('Opinión', 'Impuesto vehicular, Valor+ y política social', ruta))
    INDICE.append({'t': 'Impuesto vehicular, Valor+ y política social', 's': 'Columna de opinión · Félix Alfazar González Mira', 'u': ruta, 'k': 'pagina'})


# ===========================================================================
# Transparencia
# ===========================================================================
def t_nav(r, actual):
    items = ''.join(
        f'<li><a href="{r}transparencia/{c["slug"]}.html"{CUR if c["num"] == actual else ""}><span>{c["num"]}.</span>{esc(c["nombre"])}</a></li>'
        for c in TRANSP['categorias'])
    return f'''<aside class="t-nav" aria-label="Categorías de transparencia">
  <details open><summary>Ver las 13 categorías {icon('chev')}</summary>
  <h2>Categorías</h2><ol>{items}</ol></details>
</aside>'''


def seccion_1_1():
    ser = ''.join(f'<li><strong>{esc(v["nombre"])}:</strong> {esc(v["texto"])}</li>' for v in MV['ser'])
    hacer = ''.join(f'<li><strong>{esc(v["nombre"])}:</strong> {esc(v["texto"])}</li>' for v in MV['hacer'])
    oes = ''.join(f'<li><strong>OE {o["n"]}. {esc(o["titulo"])}</strong> {esc(o["texto"])}</li>' for o in MV['objetivos'])
    return f'''<h3>Nuestra propuesta de valor</h3><p>{esc(MV["propuesta"])}</p>
<div class="grid c2"><div><h3>Misión</h3><p>{esc(MV["mision"])}</p></div><div><h3>Visión</h3><p>{esc(MV["vision"])}</p></div></div>
<h3>Valores corporativos</h3>
<div class="grid c2"><div><h4>Desde el ser</h4><ul class="checks">{ser}</ul></div><div><h4>Desde el hacer</h4><ul class="checks">{hacer}</ul></div></div>
<h3>Objetivos estratégicos</h3><ol class="stack">{oes}</ol>'''


def pagina_transparencia():
    ruta = 'transparencia/index.html'
    r = raiz(ruta)
    cards = ''.join(f'''<li data-reveal style="--d:{i * 40}"><a class="card t-cat hover spotlight" href="{r}transparencia/{c["slug"]}.html">
  <span class="n" aria-hidden="true">{c["num"]}</span>
  <span><h3>{c["num"]}. {esc(c["nombre"])}</h3><p>{esc(c["desc"])}</p><p style="margin-top:6px"><span class="badge">{c["docs"]} {"documento" if c["docs"] == 1 else "documentos"}</span></p></span>
</a></li>''' for i, c in enumerate(TRANSP['categorias']))
    total = sum(c['docs'] for c in TRANSP['categorias'])
    meta = f'<span>{icon("contrato")} {total:,} documentos publicados</span><span>Última actualización: {FECHA_ACTUALIZACION}</span><span>Responsable: <a href="mailto:{ENTIDAD["transparencia"]}" style="color:#fff">{ENTIDAD["transparencia"]}</a></span>'.replace(',', '.')
    intro = ' '.join(esc(p) for p in TRANSP['intro'])
    cuerpo = page_hero(r, 'Transparencia y acceso a la información pública', [('Inicio', 'index.html'), ('Transparencia', None)],
                       'Ley 1712 de 2014 · Resolución MinTIC 1519 de 2020', intro, meta=meta) + f'''
<section class="section"><div class="container">
  <form class="t-search" action="{r}buscar.html" role="search" data-reveal>
    {icon('buscar')}
    <label class="sr-only" for="t-buscar">Buscar documentos de transparencia</label>
    <input class="input" id="t-buscar" name="q" type="search" placeholder="Buscar entre {total:,} documentos: estados financieros, plan anual de adquisiciones, PQRSD…" autocomplete="off">
  </form>
  <h2 class="sr-only">Categorías de información</h2>
  <ul class="t-cats">{cards}</ul>
  <p class="small muted" style="margin-top:2rem">Estructura según el Anexo 2 de la Resolución MinTIC 1519 de 2020 y la matriz del Índice de Transparencia y Acceso a la Información (ITA) de la Procuraduría General de la Nación.</p>
</div></section>'''.replace(f'{total:,}', f'{total:,}'.replace(',', '.'))
    escribir(ruta, documento(r, 'Transparencia y acceso a la información pública', 'Información pública de Valor+ S.A.S. según la Ley 1712 de 2014 y la Resolución MinTIC 1519 de 2020.', cuerpo, 'transparencia'))
    registrar(ruta, 'Transparencia y acceso a la información pública', 'Transparencia', 'Ley 1712 de 2014')

    enlaces_categoria = {'6': ('participa.html', 'Ir a la página Participa'), '11': ('atencion-ciudadania.html', 'Ir a Atención y servicios a la ciudadanía')}
    for c in TRANSP['categorias']:
        ruta = f'transparencia/{c["slug"]}.html'
        r = raiz(ruta)
        toc = ''.join(f'<a class="chip" href="#s-{s["num"].replace(".", "-")}">{esc(s["num"])} {esc(s["titulo"][:48])}{"…" if len(s["titulo"]) > 48 else ""}</a>' for s in c['secciones'])
        secciones = ''
        intro_html = render_bloques(r, [b for b in c['intro'] if not (b['k'] == 'doc' and b.get('local') in [v[0] for v in enlaces_categoria.values()])], f'c{c["num"]}')
        if c['num'] in enlaces_categoria:
            u, t = enlaces_categoria[c['num']]
            intro_html = f'<p><a class="btn" href="{r}{u}">{t} {flecha()}</a></p>' + intro_html
        ids_usados = set()
        for s in c['secciones']:
            sid = 's-' + s['num'].replace('.', '-')
            cont = seccion_1_1() if s['num'] == '1.1' else render_bloques(r, s['bloques'], sid, ids_usados)
            if not cont.strip():
                cont = '<p class="empty-note">Esta sección no tiene información publicada en el sitio actual. <span class="pendiente">Revisar con el área responsable</span></p>'
            secciones += f'''<section class="t-section" id="{sid}" aria-labelledby="{sid}-t">
  <header><h2 id="{sid}-t">{esc(s["num"])} {esc(s["titulo"])}</h2><button type="button" class="icon-btn copy-link" data-copy="#{sid}" aria-label="Copiar enlace a la sección {esc(s["num"])}">{icon("enlace")}</button></header>
  {cont}
</section>'''
            INDICE.append({'t': f'{s["num"]} {s["titulo"]}', 's': f'Transparencia · {c["num"]}. {c["nombre"]}', 'u': f'{ruta}#{sid}', 'k': 'pagina'})
            for b in s['bloques']:
                if b['k'] == 'doc' and not b.get('local'):
                    INDICE.append({'t': b['titulo'], 's': f'{s["num"]} {s["titulo"]}' + (f' · {b["fecha"]}' if b.get('fecha') else ''), 'u': b['href'], 'k': 'doc', 'f': b['ext']})
        for b in c['intro']:
            if b['k'] == 'doc' and not b.get('local'):
                INDICE.append({'t': b['titulo'], 's': f'{c["num"]}. {c["nombre"]}', 'u': b['href'], 'k': 'doc', 'f': b['ext']})
        if not c['secciones'] and not intro_html.strip():
            intro_html = '<p class="empty-note">Esta categoría no tiene información publicada en el sitio actual.</p>'
        filtro = f'''<div class="t-search"><label class="sr-only" for="t-filtro">Filtrar documentos de esta categoría</label>{icon('buscar')}<input class="input" id="t-filtro" type="search" placeholder="Filtrar los {c["docs"]} documentos de esta categoría…" data-scope="#t-contenido" autocomplete="off"></div><p id="t-filtro-estado" class="small muted" aria-live="polite"></p>''' if c['docs'] > 8 else ''
        meta = f'<span>{c["docs"]} documentos</span><span>Última actualización: {FECHA_ACTUALIZACION}</span>'
        cuerpo = page_hero(r, f'{c["num"]}. {esc(c["nombre"])}', [('Inicio', 'index.html'), ('Transparencia', 'transparencia/index.html'), (c['nombre'], None)],
                           'Transparencia y acceso a la información pública', esc(c['desc']), meta=meta) + f'''
<section class="section tight"><div class="container t-layout">
  {t_nav(r, c["num"])}
  <div id="t-contenido">
    {filtro}
    {f'<nav aria-label="En esta categoría" class="chips" style="margin-bottom:2rem">{toc}</nav>' if toc else ''}
    {intro_html}
    {secciones}
  </div>
</div></section>'''
        escribir(ruta, documento(r, f'{c["num"]}. {c["nombre"]} · Transparencia', f'Transparencia: {c["nombre"]}. {c["desc"]}', cuerpo, 'transparencia'))
        PAGINAS.append(('Transparencia', f'{c["num"]}. {c["nombre"]}', ruta))
        INDICE.append({'t': f'{c["num"]}. {c["nombre"]}', 's': 'Transparencia · ' + c['desc'], 'u': ruta, 'k': 'pagina'})


# ===========================================================================
# Atención a la ciudadanía, PQRSD, Participa, Contacto
# ===========================================================================
def canales(r):
    e = ENTIDAD
    items = [
        ('formulario', 'Formulario electrónico de PQRSD', f'<a href="{r}pqrsd.html#radicar">Radicar una solicitud</a>'),
        ('correo', 'Correo electrónico', f'<a href="mailto:{e["pqrsd"]}">{e["pqrsd"]}</a>'),
        ('telefono', 'Canal telefónico', f'<a href="{e["tel_href"]}">{e["telefono"]}</a> {e["ext_pqrsd"]}<br>Línea gratuita: <a href="{e["lg_href"]}">{e["linea_gratuita"]}</a>'),
        ('ubicacion', 'Canal presencial', e['direccion']),
        ('reloj', 'Horario de atención', e['horario']),
        ('balanza', 'Notificaciones judiciales', f'<a href="mailto:{e["notificaciones"]}">{e["notificaciones"]}</a>'),
    ]
    return ''.join(f'<div class="card hover spotlight" data-reveal style="--d:{i * 60}"><span class="card-icon">{icon(ic)}</span><h3 style="font-size:1.05rem">{t}</h3><p style="margin:0">{v}</p></div>' for i, (ic, t, v) in enumerate(items))


def campo(id_, label, tipo='text', req=True, hint=None, auto=None, extra='', opciones=None, area=False):
    rq = '<span class="req" aria-hidden="true">*</span>' if req else ''
    desc = f'{id_}-error' + (f' {id_}-hint' if hint else '')
    h = f'<p class="hint" id="{id_}-hint">{hint}</p>' if hint else ''
    ac = f' autocomplete="{auto}"' if auto else ''
    r_ = ' required' if req else ''
    if opciones:
        ops = '<option value="">Selecciona una opción</option>' + ''.join(f'<option>{esc(o)}</option>' for o in opciones)
        ctrl = f'<select class="input" id="{id_}" name="{id_}"{r_} aria-describedby="{desc}"{extra}>{ops}</select>'
    elif area:
        ctrl = f'<textarea class="input" id="{id_}" name="{id_}"{r_} aria-describedby="{desc}"{extra}></textarea>'
    else:
        ctrl = f'<input class="input" id="{id_}" name="{id_}" type="{tipo}"{r_}{ac} aria-describedby="{desc}"{extra}>'
    return f'<div class="field"><label for="{id_}">{label} {rq}</label>{h}{ctrl}<p class="error-msg" id="{id_}-error" hidden></p></div>'


def autorizacion(r, id_='autoriza'):
    return f'''<div class="field"><div class="check"><input type="checkbox" id="{id_}" name="{id_}" required aria-describedby="{id_}-error"><label for="{id_}">Autorizo el tratamiento de mis datos personales de acuerdo con la <a href="{r}politicas.html">política de tratamiento de datos personales</a> de Valor+ S.A.S. (Ley 1581 de 2012). <span class="req" aria-hidden="true">*</span></label></div><p class="error-msg" id="{id_}-error" hidden></p></div>'''


def exito(texto):
    return f'<div class="form-alert ok" role="status" tabindex="-1" hidden>{icon("check")}<div><strong>¡Listo!</strong> {texto} <span class="small">(Simulación del prototipo: no se envió información).</span></div></div>'


def pagina_atencion():
    ruta = 'atencion-ciudadania.html'
    r = raiz(ruta)
    docs = [{'titulo': 'Política de servicio al ciudadano de Valor+', 'href': 'https://s3-site-vmas-cdn.s3.amazonaws.com/assets/2025/09/09083853/Politica-de-Servicio-al-Ciudadano-de-Valor.pdf', 'ext': 'pdf'},
            {'titulo': 'Carta de trato digno', 'href': 'https://s3-site-vmas-cdn.s3.amazonaws.com/assets/2025/11/04170223/Carta-de-Trato-Digno.pdf', 'ext': 'pdf'},
            {'titulo': 'Atención de PQRDS', 'href': 'https://s3-site-vmas-cdn.s3.amazonaws.com/wp-content/uploads/2024/07/Atenci%C3%B3n+de+PQRDS+1.pdf', 'ext': 'pdf'},
            {'titulo': 'Informes trimestrales de PQRSD', 'href': '', 'local': 'transparencia/planeacion-presupuesto-e-informes.html#s-4-10', 'ext': 'web'}]
    norma = ['Artículo 23 de la Constitución Política de Colombia', 'Ley 1437 de 2011', 'Ley 1712 de 2014', 'Ley 1755 de 2015', 'Decreto 1166 de 2016']
    cuerpo = page_hero(r, 'Atención y servicios a la ciudadanía', [('Inicio', 'index.html'), ('Atención al ciudadano', None)], 'Atención al ciudadano',
                       'Canales de atención, trámites y servicios disponibles para la ciudadanía.') + f'''
<section class="section"><div class="container">
  <p class="eyebrow">11.2</p><h2 data-reveal>Canales de atención</h2>
  <div class="grid c3" style="margin-top:1.5rem">{canales(r)}</div>
</div></section>
<section class="section soft"><div class="container split" style="align-items:start">
  <div data-reveal>
    <p class="eyebrow">11.1</p><h2>Trámites y otros procedimientos administrativos</h2>
    <p class="lead">La entidad no cuenta con trámites específicos para gestión de la ciudadanía; sin embargo, pone a disposición diferentes canales de atención para la atención de PQRSD.</p>
    <a class="btn" href="{r}pqrsd.html">Ir a PQRSD {flecha()}</a>
    <h3 style="margin-top:2.5rem">Normatividad en materia de atención de PQRSD</h3>
    <ul class="checks">{''.join(f"<li>{n}</li>" for n in norma)}</ul>
  </div>
  <div data-reveal>
    <p class="eyebrow">Documentos</p><h2>Políticas y protocolos</h2>
    <ul class="docs">{''.join(doc_item(r, d) for d in docs)}</ul>
  </div>
</div></section>
<section class="section" id="cita"><div class="container narrow">
  <p class="eyebrow">11.2 · Pida una cita</p><h2 data-reveal>Agenda una cita de atención presencial</h2>
  <p><span class="pendiente">Funcionalidad propuesta</span> El sitio actual no ofrece agendamiento en línea. Este formulario muestra cómo podría funcionar.</p>
  <form class="form card" data-validate style="margin-top:1.5rem">
    <div class="row">{campo('cita-nombre', 'Nombre completo', auto='name')}{campo('cita-correo', 'Correo electrónico', 'email', auto='email')}</div>
    <div class="row">{campo('cita-fecha', 'Fecha preferida', 'date')}{campo('cita-franja', 'Franja horaria', opciones=['7:30 a. m. – 12:30 p. m.', '1:30 p. m. – 5:30 p. m.'])}</div>
    {campo('cita-motivo', 'Motivo de la cita', area=True)}
    {autorizacion(r, 'cita-autoriza')}
    <div><button class="btn" type="submit">Solicitar cita {flecha()}</button></div>
    {exito('Recibimos tu solicitud de cita. Te confirmaremos por correo electrónico.')}
  </form>
</div></section>'''
    escribir(ruta, documento(r, 'Atención y servicios a la ciudadanía', 'Canales de atención, horarios, trámites y PQRSD de Valor+ S.A.S.', cuerpo, 'atencion'))
    registrar(ruta, 'Atención y servicios a la ciudadanía', 'Atención y participación', 'Canales de atención, horarios y trámites')


def pagina_pqrsd():
    ruta = 'pqrsd.html'
    r = raiz(ruta)
    tipos = [('Petición', 'Solicitud respetuosa de interés general o particular'), ('Queja / Reclamo', 'Inconformidad con la atención o el servicio'),
             ('Solicitud de información', 'Acceso a información pública'), ('Denuncia', 'Hechos irregulares o de corrupción'), ('Sugerencia / Propuesta', 'Ideas para mejorar')]
    radios = ''.join(f'<label><input type="radio" name="tipo" value="{esc(t)}" required aria-describedby="tipo-error">{esc(t)}<small>{esc(d)}</small></label>' for t, d in tipos)
    caras = lambda n: ''.join(f'<label><input type="radio" name="{n}" value="{v}" required>{e} {v}</label>' for e, v in [('🙂', 'Buena'), ('😐', 'Regular'), ('😞', 'Mala')])
    cuerpo = page_hero(r, 'Peticiones, quejas, reclamos, sugerencias y denuncias', [('Inicio', 'index.html'), ('Atención al ciudadano', 'atencion-ciudadania.html'), ('PQRSD', None)], 'PQRSD',
                       'Como usuario registrado o anónimo, presenta peticiones, quejas, reclamos, denuncias o sugerencias por motivos de interés general o particular. Valor+ S.A.S., a través de la oficina de atención al ciudadano, atenderá tu solicitud.') + f'''
<section class="section tight"><div class="container">
  <nav class="chips" aria-label="Opciones de PQRSD"><a class="chip" href="#radicar">{icon('formulario')} Radicar</a><a class="chip" href="#consultar">{icon('buscar')} Consultar</a><a class="chip" href="#encuesta">{icon('estrella')} Encuesta de satisfacción</a><a class="chip" href="https://s3-site-vmas-cdn.s3.amazonaws.com/wp-content/uploads/2024/10/31111216/Manual-de-Usuario-PQRDS.pdf" target="_blank" rel="noopener">{icon('descarga')} Guía del usuario (PDF)</a></nav>
</div></section>
<section class="section tight" id="radicar" aria-labelledby="radicar-t"><div class="container narrow">
  <p class="eyebrow">Radicar</p><h2 id="radicar-t">Radica tu solicitud en cuatro pasos</h2>
  <form id="pqrsd-asistente" class="card form" style="margin-top:1.5rem" novalidate>
    <ol class="stepper"><li>Tipo</li><li>Tus datos</li><li>Solicitud</li><li>Confirmar</li></ol>
    <div class="step-panel">
      <h3>1. ¿Qué tipo de solicitud quieres presentar?</h3>
      <fieldset class="field"><legend>Tipo de solicitud <span class="req" aria-hidden="true">*</span></legend><div class="radio-cards">{radios}</div><p class="error-msg" id="tipo-error" hidden></p></fieldset>
      {campo('solicitante', 'Tipo de solicitante', opciones=['Persona natural', 'Persona jurídica', 'Niñas, niños y adolescentes', 'Apoderado', 'Anónimo'])}
      <div class="btn-row"><button type="button" class="btn" data-next>Continuar {flecha()}</button></div>
    </div>
    <div class="step-panel" hidden>
      <h3>2. ¿Cómo te contactamos?</h3>
      <div data-identidad><div class="row">{campo('nombre', 'Nombres', auto='given-name')}{campo('apellido', 'Apellidos', auto='family-name')}</div>
      {campo('medio', 'Medio para recibir la respuesta', opciones=['Correo electrónico', 'Dirección de correspondencia'])}
      {campo('correo', 'Correo electrónico', 'email', auto='email', hint='Te enviaremos el número de radicado y la respuesta.')}</div>
      <div class="btn-row"><button type="button" class="btn ghost" data-prev>Atrás</button><button type="button" class="btn" data-next>Continuar {flecha()}</button></div>
    </div>
    <div class="step-panel" hidden>
      <h3>3. Cuéntanos tu solicitud</h3>
      {campo('asunto', 'Título de la solicitud', hint='Breve descripción del título de la solicitud.')}
      {campo('descripcion', 'Contenido de la solicitud', area=True, hint='Descripción detallada de la solicitud.')}
      <div class="field"><span class="label" style="font:700 .92rem var(--font-head)">Adjuntar archivos (opcional)</span>
        <label class="dropzone">{icon('descarga')}<span>Arrastra tus archivos aquí o <u>selecciónalos</u></span><span class="small">Texto, hojas de cálculo, video, audio, imágenes, entre otros.</span><input class="sr-only" type="file" name="adjuntos" multiple></label>
        <p class="file-list small muted" aria-live="polite"></p></div>
      <div class="btn-row"><button type="button" class="btn ghost" data-prev>Atrás</button><button type="button" class="btn" data-next>Revisar {flecha()}</button></div>
    </div>
    <div class="step-panel" hidden>
      <h3>4. Confirma y envía</h3>
      <ul id="pq-resumen" class="facts"></ul>
      {autorizacion(r, 'pq-autoriza')}
      <p class="small muted">Si la solicitud de información requiere reserva de identidad, debes hacer el trámite ante la Procuraduría General de la Nación: <a href="https://www.procuraduria.gov.co/portal/solicitud_informacion_identificacion_reservada.page" target="_blank" rel="noopener">solicitud de información con identificación reservada</a>.</p>
      <div class="btn-row"><button type="button" class="btn ghost" data-prev>Atrás</button><button type="submit" class="btn">Radicar solicitud {flecha()}</button></div>
    </div>
  </form>
  <div id="pq-listo" class="card" hidden tabindex="-1" style="margin-top:1.5rem;text-align:center">
    <span class="card-icon" style="margin-inline:auto">{icon('check')}</span>
    <h3>Tu solicitud fue radicada</h3>
    <p>Número de radicado: <strong id="pq-radicado"></strong></p>
    <p class="small muted">Simulación del prototipo: no se envió información.</p>
  </div>
</div></section>
<section class="section tight soft" id="consultar" aria-labelledby="consultar-t"><div class="container narrow">
  <p class="eyebrow">Consultar</p><h2 id="consultar-t">Consulta el estado de tu solicitud</h2>
  <form id="pq-consulta" class="form card" style="margin-top:1.5rem" novalidate>
    <div class="row">{campo('radicado', 'Número de radicado', extra=' placeholder="VM-2026-123456"')}{campo('consulta-correo', 'Correo electrónico registrado', 'email', auto='email')}</div>
    <div><button class="btn" type="submit">Consultar {flecha()}</button></div>
    <div id="pq-consulta-res" class="form-alert ok" role="status" tabindex="-1" hidden>{icon('reloj')}<div><strong>En trámite.</strong> Tu solicitud está siendo gestionada por el área responsable. <span class="small">(Simulación del prototipo).</span></div></div>
  </form>
</div></section>
<section class="section tight" id="encuesta" aria-labelledby="encuesta-t"><div class="container narrow">
  <p class="eyebrow">Encuesta</p><h2 id="encuesta-t">Encuesta de satisfacción</h2>
  <form class="form card" data-validate style="margin-top:1.5rem">
    {campo('enc-radicado', '1. Número de radicado')}
    <fieldset class="field"><legend>2. La atención, en términos de oportunidad y rapidez en el tiempo de respuesta, fue: <span class="req" aria-hidden="true">*</span></legend><div class="radio-cards">{caras('oportunidad')}</div></fieldset>
    <fieldset class="field"><legend>3. La respuesta de la dependencia o funcionario cumplió sus expectativas, en términos de solución o explicación de las razones de la respuesta, y fue: <span class="req" aria-hidden="true">*</span></legend><div class="radio-cards">{caras('respuesta')}</div></fieldset>
    <fieldset class="field"><legend>4. ¿Fue satisfactoria la respuesta a su petición, consulta, queja, reclamo o sugerencia? <span class="req" aria-hidden="true">*</span></legend><div class="radio-cards"><label><input type="radio" name="satisfecho" value="Sí" required>✅ Sí</label><label><input type="radio" name="satisfecho" value="No" required>❌ No</label></div></fieldset>
    <div><button class="btn" type="submit">Enviar respuesta {flecha()}</button></div>
    {exito('Gracias por calificar nuestra atención.')}
  </form>
</div></section>'''
    escribir(ruta, documento(r, 'PQRSD', 'Radica y consulta peticiones, quejas, reclamos, sugerencias y denuncias ante Valor+ S.A.S.', cuerpo, 'atencion'))
    registrar(ruta, 'PQRSD: peticiones, quejas, reclamos, sugerencias y denuncias', 'Atención y participación', 'Radicar, consultar, encuesta de satisfacción')


def pagina_participa():
    ruta = 'participa.html'
    r = raiz(ruta)
    bloques = cargar_participa()
    # dividir en secciones de primer nivel (6.1, 6.2)
    html, sec = '', []

    def volcar():
        nonlocal html, sec
        if sec:
            h = sec[0]
            sid = 's-' + h['num'].replace('.', '-')
            html += f'<section class="t-section" id="{sid}"><header><h2>{esc(h["num"])} {esc(h["text"])}</h2><button type="button" class="icon-btn copy-link" data-copy="#{sid}" aria-label="Copiar enlace a la sección {esc(h["num"])}">{icon("enlace")}</button></header>{render_bloques(r, sec[1:])}</section>'
        sec = []
    for b in bloques:
        if b['k'] == 'h' and b['num'] and b['depth'] == 2:
            volcar()
        if b['k'] == 'h' and not b['num']:
            b = dict(b, num=None)
        sec.append(b)
    volcar()
    cuerpo = page_hero(r, 'Participa', [('Inicio', 'index.html'), ('Participa', None)], 'Participación ciudadana',
                       'Conoce la información relevante de la entidad de cara a la ciudadanía y los espacios habilitados para brindar tu opinión.') + f'''
<section class="section tight"><div class="container">
  <div class="grid c3">
    <a class="card hover spotlight" href="#s-6-2" style="text-decoration:none;color:inherit"><span class="card-icon">{icon('megafono')}</span><h2 style="font-size:1.15rem">Rendición de cuentas</h2><p class="muted">Estrategia anual, calendario, informes y memorias.</p></a>
    <a class="card hover spotlight" href="{r}transparencia/planeacion-presupuesto-e-informes.html#s-4-3" style="text-decoration:none;color:inherit"><span class="card-icon">{icon('escudo')}</span><h2 style="font-size:1.15rem">Plan anticorrupción y de atención al ciudadano</h2><p class="muted">Programa de transparencia y ética pública.</p></a>
    <a class="card hover spotlight" href="{r}pqrsd.html" style="text-decoration:none;color:inherit"><span class="card-icon">{icon('chat')}</span><h2 style="font-size:1.15rem">Danos tu opinión</h2><p class="muted">Sugerencias y propuestas a través de PQRSD.</p></a>
  </div>
</div></section>
<section class="section tight"><div class="container narrow" id="t-contenido">{html}</div></section>'''
    escribir(ruta, documento(r, 'Participa', 'Participación ciudadana y rendición de cuentas de Valor+ S.A.S.', cuerpo, 'participa'))
    registrar(ruta, 'Participa', 'Atención y participación', 'Rendición de cuentas y participación ciudadana')


def pagina_contacto():
    ruta = 'contacto.html'
    r = raiz(ruta)
    cuerpo = page_hero(r, '¡Envíanos un mensaje!', [('Inicio', 'index.html'), ('Contáctanos', None)], 'Contáctanos', 'Los campos marcados con * son obligatorios.') + f'''
<section class="section"><div class="container split" style="align-items:start">
  <form class="form card" data-validate data-reveal="left" aria-labelledby="form-contacto-t">
    <h2 id="form-contacto-t" class="sr-only">Formulario de contacto</h2>
    <div class="row">{campo('c-nombre', 'Nombre', auto='name')}{campo('c-telefono', 'Teléfono', 'tel', auto='tel')}</div>
    {campo('c-correo', 'Dirección de correo electrónico', 'email', auto='email')}
    {campo('c-mensaje', 'Mensaje', area=True)}
    {autorizacion(r, 'c-autoriza')}
    <p class="small muted">La información suministrada será tratada de forma confidencial y utilizada únicamente para dar respuesta a su solicitud.</p>
    <div><button class="btn" type="submit" data-magnetic>Enviar {flecha()}</button></div>
    {exito('Recibimos tu mensaje. Te responderemos pronto.')}
  </form>
  <div class="grid" data-reveal="right">
    <h2 class="sr-only">Canales de atención</h2>
    {canales(r)}
    <a class="btn ghost" href="https://www.openstreetmap.org/search?query=Edificio%20Edatel%20La%20Alpujarra%20Medell%C3%ADn" target="_blank" rel="noopener">{icon('ubicacion')} Cómo llegar<span class="sr-only"> (abre OpenStreetMap en una pestaña nueva)</span></a>
  </div>
</div></section>'''
    escribir(ruta, documento(r, 'Contáctanos', 'Escríbele a Valor+ S.A.S. y conoce nuestros canales de contacto.', cuerpo, 'contacto'))
    registrar(ruta, 'Contáctanos', 'Navegación principal', 'Formulario de contacto y canales')


# ===========================================================================
# Oportunidades: proveedores, hojas de vida, convocatorias, invitación abierta
# ===========================================================================
def pagina_proveedores():
    ruta = 'proveedores.html'
    r = raiz(ruta)
    lineas = ['Infraestructura tecnológica', 'Administración y gestión de infraestructura tecnológica', 'Licencias tecnológicas',
              'Suministro y/o mantenimiento de equipos de cómputo y accesorios', 'Desarrollo de software', 'Conectividad e internet',
              'Servicios de impresión, fotocopiado, fax y escáner', 'Servicios de operador logístico', 'Catering', 'Contratación de personal',
              'Suministro de elementos de papelería e implementos de oficina', 'Suministro de elementos del servicio de aseo, cafetería y bioseguridad',
              'Diseño y publicidad', 'Otros']
    checks = ''.join(f'<div class="check"><input type="checkbox" id="l{i}" name="lineas" value="{esc(l)}"><label for="l{i}">{esc(l)}</label></div>' for i, l in enumerate(lineas))
    cuerpo = page_hero(r, 'Registro de proveedores', [('Inicio', 'index.html'), ('Registro de proveedores', None)], 'Oportunidades',
                       'Permítenos conocer tus servicios para entregar + valor a nuestra gestión.') + f'''
<section class="section"><div class="container narrow">
  <form class="form" data-validate>
    <fieldset class="card form"><legend class="h3" style="font:800 1.3rem var(--font-head);padding:0 .3em">A. Información general de la empresa</legend>
      <div class="row">{campo('p-tipo', 'Tipo de identificación', opciones=['Persona natural', 'NIT persona jurídica'])}{campo('p-id', 'Identificación')}</div>
      {campo('p-unspsc', 'Código UNSPSC', req=False, hint='Estándar de Productos y Servicios de Naciones Unidas.')}
      {campo('p-razon', 'Nombre como aparece en el RUT o en la Cámara de Comercio', auto='organization')}
      <div class="row">{campo('p-tdoc', 'Tipo de documento del representante legal', req=False, opciones=['Cédula de ciudadanía', 'Cédula de extranjería', 'Pasaporte'])}{campo('p-doc', 'Documento del representante legal')}</div>
      {campo('p-rep', 'Representante legal', auto='name')}
      <div class="row">{campo('p-dom', 'Domicilio', auto='street-address')}{campo('p-ciudad', 'Ciudad', req=False, auto='address-level2')}</div>
      <div class="row">{campo('p-depto', 'Departamento', req=False, auto='address-level1')}{campo('p-pais', 'País', req=False, auto='country-name', extra=' value="Colombia"')}</div>
    </fieldset>
    <fieldset class="card form"><legend style="font:800 1.3rem var(--font-head);padding:0 .3em">B. Datos de contacto</legend>
      <p><strong>Contacto principal</strong></p>
      <div class="row">{campo('p-cnom', 'Nombre', auto='name')}{campo('p-ccargo', 'Cargo', auto='organization-title')}</div>
      <div class="row">{campo('p-ctel', 'Teléfono', 'tel', req=False, auto='tel')}{campo('p-ccel', 'Celular', 'tel', auto='tel')}</div>
      {campo('p-cmail', 'Correo electrónico', 'email', auto='email')}
      <details class="acc"><summary>Agregar un contacto secundario (opcional)</summary><div class="acc-body form">
        <div class="row">{campo('p-c2nom', 'Nombre', req=False)}{campo('p-c2cargo', 'Cargo', req=False)}</div>
        <div class="row">{campo('p-c2tel', 'Teléfono', 'tel', req=False)}{campo('p-c2cel', 'Celular', 'tel', req=False)}</div>
        {campo('p-c2mail', 'Correo electrónico', 'email', req=False)}
      </div></details>
    </fieldset>
    <fieldset class="card form"><legend style="font:800 1.3rem var(--font-head);padding:0 .3em">C. Líneas de negocio</legend>
      <fieldset class="field"><legend>Categoría</legend><div class="radio-cards"><label><input type="radio" name="categoria" value="Bienes">Bienes</label><label><input type="radio" name="categoria" value="Servicios">Servicios</label></div></fieldset>
      <fieldset class="field"><legend>Líneas</legend><div class="grid c2" style="gap:10px">{checks}</div></fieldset>
      <div class="field"><span style="font:700 .92rem var(--font-head)">Documentación soporte</span>
        <p class="hint"><span class="pendiente">Por confirmar</span> El sitio actual pide “adjuntar la siguiente documentación” pero no lista los documentos.</p>
        <label class="dropzone">{icon('descarga')}<span>Arrastra tus archivos aquí o <u>selecciónalos</u></span><input class="sr-only" type="file" name="soportes" multiple></label><p class="file-list small muted" aria-live="polite"></p></div>
      {campo('p-contratos', '¿Tiene contratos suscritos con Valor+?', opciones=['Sí', 'No'])}
    </fieldset>
    <p class="small muted">Nota: la presente inscripción no tiene condición vinculante para las partes y por tanto no obliga a Valor+ a suscribir contrato alguno con el proveedor registrado.</p>
    {autorizacion(r, 'p-autoriza')}
    <div><button class="btn" type="submit">Enviar registro {flecha()}</button></div>
    {exito('Recibimos tu registro como proveedor.')}
  </form>
</div></section>'''
    escribir(ruta, documento(r, 'Registro de proveedores', 'Inscríbete como proveedor de bienes y servicios de Valor+ S.A.S.', cuerpo, None))
    registrar(ruta, 'Registro de proveedores', 'Oportunidades', 'Inscripción de proveedores de bienes y servicios')


def pagina_hojas_de_vida():
    ruta = 'hojas-de-vida.html'
    r = raiz(ruta)
    cuerpo = page_hero(r, 'Trabaja con nosotros', [('Inicio', 'index.html'), ('Trabaja con nosotros', None)], 'Banco de hojas de vida', 'Únete a nuestro equipo de trabajo.') + f'''
<section class="section"><div class="container narrow">
  <form class="form card" data-validate>
    <div class="row">{campo('h-nombre', 'Nombre', auto='given-name')}{campo('h-apellidos', 'Apellidos', auto='family-name')}</div>
    {campo('h-profesion', 'Profesión', auto='organization-title')}
    <div class="field"><label for="h-archivo">Cargar hoja de vida <span class="req" aria-hidden="true">*</span></label><p class="hint" id="h-archivo-hint">Formato PDF, máximo 5 MB.</p>
      <label class="dropzone" for="h-archivo">{icon('descarga')}<span>Arrastra tu hoja de vida aquí o <u>selecciónala</u></span></label>
      <input class="sr-only" type="file" id="h-archivo" name="hv" accept="application/pdf" required aria-describedby="h-archivo-hint h-archivo-error"><p class="file-list small muted" aria-live="polite"></p><p class="error-msg" id="h-archivo-error" hidden></p></div>
    {autorizacion(r, 'h-autoriza')}
    <div><button class="btn" type="submit">Enviar hoja de vida {flecha()}</button></div>
    {exito('Recibimos tu hoja de vida.')}
  </form>
</div></section>'''
    escribir(ruta, documento(r, 'Trabaja con nosotros', 'Envía tu hoja de vida al banco de talento de Valor+ S.A.S.', cuerpo, None))
    registrar(ruta, 'Trabaja con nosotros (banco de hojas de vida)', 'Oportunidades', 'Envía tu hoja de vida')


def pagina_procesos(ruta, json_name, titulo, lead, eyebrow, desc_meta):
    r = raiz(ruta)
    ps = procesos(json_name)
    anios = sorted({p['anio'] for p in ps if p['anio']}, reverse=True)
    chips = '<button type="button" class="chip" data-filter="todos" aria-pressed="true">Todos</button>' + ''.join(f'<button type="button" class="chip" data-filter="a{a}" aria-pressed="false">{a}</button>' for a in anios)
    items = ''
    for p in sorted(ps, key=lambda x: (x['anio'] or '0'), reverse=True):
        desc = ''.join(f'<p>{esc(d)}</p>' for d in p['desc'] if fix(d).rstrip('.').lower() != p['titulo'].rstrip('.').lower())
        secop = f'<p><a class="btn sm ghost" href="{esc(p["secop"])}" target="_blank" rel="noopener">{icon("externo")} Ver el proceso en SECOP II<span class="sr-only"> (abre en una pestaña nueva)</span></a></p>' if p['secop'] else ''
        docs = '<ul class="docs">' + ''.join(doc_item(r, d) for d in p['docs']) + '</ul>' if p['docs'] else ''
        items += f'<details class="acc" id="{p["id"]}" data-tags="a{p["anio"]}"><summary><span>{esc(p["titulo"])} <span class="badge blue" style="margin-left:6px">{p["anio"]}</span></span><span class="count">{len(p["docs"])} documentos</span></summary><div class="acc-body">{desc}{secop}{docs}</div></details>'
        objeto = next((d for d in p['desc'] if len(d) > 40), '')
        INDICE.append({'t': p['titulo'], 's': f'{titulo} · {p["anio"]}' + (f' · {objeto[:110]}' if objeto else ''), 'u': f'{ruta}#{p["id"]}', 'k': 'proceso'})
    cuerpo = page_hero(r, titulo, [('Inicio', 'index.html'), (titulo, None)], eyebrow, lead, meta=f'<span>{len(ps)} procesos publicados</span>') + f'''
<section class="section"><div class="container narrow">
  <div class="chips" role="group" aria-label="Filtrar por año" data-filter-group="#lista-procesos" data-status="#procesos-estado">{chips}</div>
  <p id="procesos-estado" class="sr-only" aria-live="polite"></p>
  <div id="lista-procesos" style="margin-top:1.5rem">{items}</div>
</div></section>'''
    escribir(ruta, documento(r, titulo, desc_meta, cuerpo, None))
    registrar(ruta, titulo, 'Oportunidades', desc_meta)


# ===========================================================================
# Páginas institucionales: mapa del sitio, políticas, accesibilidad, búsqueda, 404
# ===========================================================================
def pagina_politicas():
    ruta = 'politicas.html'
    r = raiz(ruta)
    docs = [{'titulo': 'Política y procedimientos de tratamiento de datos personales', 'fecha': '15 de agosto de 2025', 'ext': 'pdf',
             'href': 'https://s3-site-vmas-cdn.s3.amazonaws.com/assets/2025/08/15105919/Poli%CC%81tica-y-Procedimientos-de-Tratamiento-de-Datos-Personales.pdf'},
            {'titulo': 'Ley 1581 de 2012 (tratamiento de datos personales)', 'ext': 'pdf', 'href': 'https://s3-site-vmas-cdn.s3.amazonaws.com/wp-content/uploads/2024/06/Ley_1581_de_2012.pdf'},
            {'titulo': 'Ley 1266 de 2008 (hábeas data)', 'ext': 'pdf', 'href': 'https://s3-site-vmas-cdn.s3.amazonaws.com/wp-content/uploads/2024/06/Ley_1266_de_2008.pdf'}]
    cond = [{'titulo': 'Condiciones de uso de los canales digitales v1.0', 'ext': 'pdf', 'href': 'https://s3-site-vmas-cdn.s3.amazonaws.com/wp-content/uploads/2023/08/DA07-PO-GETI_Condiciones-de-uso-de-los-canales-digitales_v1.0.pdf'}]
    cuerpo = page_hero(r, 'Políticas de privacidad y condiciones de uso', [('Inicio', 'index.html'), ('Políticas', None)], 'Legal') + f'''
<section class="section"><div class="container narrow prose">
  <h2 id="datos">Política de tratamiento de datos personales</h2>
  <ul class="docs">{''.join(doc_item(r, d) for d in docs)}</ul>
  <h2 id="condiciones">Condiciones de uso</h2>
  <p>El contenido de este sitio web está sujeto a las condiciones aquí expuestas. Las personas (en adelante, ciudadanos-usuarios) al acceder, navegar o usar este sitio reconocen que han leído, entendido y se obligan a cumplir estos términos, leyes y reglamentos. Si el ciudadano-usuario no está de acuerdo con la presente política de privacidad, le sugerimos abstenerse de utilizar este sitio web.</p>
  <ul class="docs">{''.join(doc_item(r, d) for d in cond)}</ul>
  <h2 id="politica-cookies">Política de cookies</h2>
  <p><span class="pendiente">Por redactar</span> El sitio actual usa Google Analytics pero no publica una política de cookies. Este prototipo incluye el aviso de consentimiento.</p>
</div></section>'''
    escribir(ruta, documento(r, 'Políticas de privacidad y condiciones de uso', 'Política de tratamiento de datos personales y condiciones de uso del sitio de Valor+ S.A.S.', cuerpo, None))
    registrar(ruta, 'Políticas de privacidad y condiciones de uso', 'Legal', 'Tratamiento de datos personales')


def pagina_accesibilidad():
    ruta = 'accesibilidad.html'
    r = raiz(ruta)
    certs = [('2026', 'https://s3-site-vmas-cdn.s3.amazonaws.com/assets/2026/09/30201850/Certificado-de-Cumplimiento-de-Accesibilidad-Web-2026.pdf'),
             ('2025', 'https://s3-site-vmas-cdn.s3.amazonaws.com/assets/2025/07/07092244/Certificado-2025.pdf')]
    cd = ''.join(doc_item(r, {'titulo': f'Certificado de accesibilidad {a}', 'href': u, 'ext': 'pdf'}) for a, u in certs)
    cuerpo = page_hero(r, 'Declaración de accesibilidad', [('Inicio', 'index.html'), ('Accesibilidad', None)], 'Accesibilidad',
                       'Trabajamos para que todas las personas, incluidas las personas con discapacidad, puedan usar este sitio.') + f'''
<section class="section"><div class="container narrow prose">
  <h2>Estándares que seguimos</h2>
  <ul class="checks"><li>Pautas de Accesibilidad para el Contenido Web (WCAG) 2.1, nivel AA, adoptadas por la Resolución MinTIC 1519 de 2020, Anexo 1.</li><li>Norma Técnica Colombiana NTC 5854.</li><li>Ley 1618 de 2013 y Ley 1346 de 2009 sobre los derechos de las personas con discapacidad.</li></ul>
  <h2>Funciones de accesibilidad del sitio</h2>
  <ul class="checks">
    <li>Enlace “Saltar al contenido principal” al comienzo de cada página.</li>
    <li>Navegación completa con teclado y foco visible.</li>
    <li>Panel de accesibilidad: tamaño de texto, alto contraste, tema oscuro, detener animaciones, subrayar enlaces y fuente de lectura fácil.</li>
    <li>Respeto de la preferencia del sistema “reducir movimiento”; toda animación automática tiene botón de pausa.</li>
    <li>Textos alternativos en imágenes informativas y estructura de títulos ordenada.</li>
    <li>Formularios con etiquetas visibles, ayudas y mensajes de error descriptivos.</li>
    <li>Búsqueda global con atajo de teclado <kbd class="kbd">Ctrl</kbd> + <kbd class="kbd">K</kbd> o <kbd class="kbd">/</kbd>.</li>
  </ul>
  <h2>Certificados</h2>
  <ul class="docs">{cd}</ul>
  <h2>¿Encontraste una barrera?</h2>
  <p>Escríbenos a <a href="mailto:{ENTIDAD["pqrsd"]}">{ENTIDAD["pqrsd"]}</a> o usa el <a href="{r}pqrsd.html#radicar">formulario de PQRSD</a> indicando la página y el problema.</p>
</div></section>'''
    escribir(ruta, documento(r, 'Declaración de accesibilidad', 'Compromiso de accesibilidad web de Valor+ S.A.S.', cuerpo, None))
    registrar(ruta, 'Declaración de accesibilidad', 'Legal', 'WCAG 2.1 AA, Resolución 1519 de 2020')


def pagina_buscar():
    ruta = 'buscar.html'
    r = raiz(ruta)
    cuerpo = page_hero(r, 'Buscar en el sitio', [('Inicio', 'index.html'), ('Buscar', None)], 'Búsqueda') + f'''
<section class="section"><div class="container narrow">
  <form id="buscar-pagina" class="t-search" role="search">{icon('buscar')}<label class="sr-only" for="q">Buscar</label><input class="input" id="q" name="q" type="search" placeholder="Escribe lo que buscas y presiona Enter" autocomplete="off"></form>
  <div id="buscar-resultados" aria-live="polite"></div>
  <noscript><p>La búsqueda requiere JavaScript. Consulta el <a href="{r}mapa-del-sitio.html">mapa del sitio</a>.</p></noscript>
</div></section>'''
    escribir(ruta, documento(r, 'Buscar', 'Buscador del sitio de Valor+ S.A.S.', cuerpo, None))


def pagina_404():
    cuerpo = '''<section class="section e404"><div class="container">
  <p class="big grad-text" aria-hidden="true">404</p>
  <h1 style="font-size:clamp(1.6rem,3vw,2.4rem)">Página no encontrada</h1>
  <p class="lead mx-auto">Parece que la página que buscas ya no existe o cambió de nombre.</p>
  <div class="btn-row" style="justify-content:center"><a class="btn" href="index.html">Ir al inicio</a><a class="btn ghost" href="buscar.html" data-open-search>Buscar en el sitio</a></div>
</div></section>'''
    escribir('404.html', documento('', 'Página no encontrada', 'La página solicitada no existe.', cuerpo, None))


def pagina_mapa():
    ruta = 'mapa-del-sitio.html'
    r = raiz(ruta)
    registrar(ruta, 'Mapa del sitio', 'Legal', 'Todas las páginas del sitio')
    orden = ['Navegación principal', 'Servicios', 'Casos de éxito', 'Opinión', 'Transparencia', 'Atención y participación', 'Oportunidades', 'Legal']
    grupos = {g: [] for g in orden}
    for g, t, u in PAGINAS:
        grupos.setdefault(g, []).append((t, u))
    html = ''.join(f'<section><h2>{esc(g)}</h2><ul>{"".join(f"<li><a href={chr(34)}{r}{u}{chr(34)}>{esc(t)}</a></li>" for t, u in items)}</ul></section>' for g, items in grupos.items() if items)
    cuerpo = page_hero(r, 'Mapa del sitio', [('Inicio', 'index.html'), ('Mapa del sitio', None)], 'Navegación') + f'<section class="section"><div class="container"><div class="sitemap">{html}</div></div></section>'
    escribir(ruta, documento(r, 'Mapa del sitio', 'Todas las páginas del sitio de Valor+ S.A.S.', cuerpo, None))


def manifest_e_indice():
    manifest = {'name': 'Valor+ S.A.S.', 'short_name': 'Valor+', 'lang': 'es-CO', 'start_url': 'index.html', 'display': 'standalone',
                'background_color': '#0c264c', 'theme_color': '#0c264c', 'icons': [{'src': 'assets/img/marca/favicon.svg', 'sizes': 'any', 'type': 'image/svg+xml'}]}
    escribir('manifest.webmanifest', json.dumps(manifest, ensure_ascii=False, indent=2))
    vistos, limpio = set(), []
    for e in INDICE:
        clave = (e['t'], e['u'])
        if clave in vistos:
            continue
        vistos.add(clave)
        limpio.append({k: v for k, v in e.items() if v})
    escribir('assets/js/indice-busqueda.js', '/* Índice de búsqueda generado por _fuente/construir.py */\nwindow.VM_INDEX=' + json.dumps(limpio, ensure_ascii=False, separators=(',', ':')) + ';\n')
    return len(limpio)


def main():
    pagina_inicio()
    pagina_nosotros()
    pagina_servicios()
    pagina_casos()
    pagina_opinion()
    pagina_contacto()
    pagina_transparencia()
    pagina_atencion()
    pagina_pqrsd()
    pagina_participa()
    pagina_proveedores()
    pagina_hojas_de_vida()
    pagina_procesos('convocatorias.html', 'convocatorias.json', 'Convocatorias públicas y abreviadas',
                    'Descubre oportunidades para colaborar con nosotros en proyectos que impactan positivamente a la comunidad.', 'Contratación',
                    'Convocatorias públicas y abreviadas de Valor+ S.A.S. con sus documentos.')
    pagina_procesos('invitacion-abierta.html', 'invitacion.json', 'Invitación abierta', '¡Únete a nuestras invitaciones abiertas!', 'Contratación',
                    'Invitaciones abiertas de Valor+ S.A.S. para aliados proveedores.')
    pagina_politicas()
    pagina_accesibilidad()
    pagina_buscar()
    pagina_404()
    pagina_mapa()
    n = manifest_e_indice()
    print(f'{len(PAGINAS)} páginas en el mapa del sitio · {n} entradas en el índice de búsqueda')


if __name__ == '__main__':
    main()
