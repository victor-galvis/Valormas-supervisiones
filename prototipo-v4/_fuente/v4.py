"""Versión 4: página de inicio, tarjetas de proyecto con escenas 3D y páginas inmersivas de la versión 3.

Reúne el contenido completo de la versión 1 (transparencia, opinión, equipo, oportunidades…) con los
mapas y gráficas de la versión 3 y las escenas 3D por proyecto (assets/js/escenas.js).
"""
import importlib.util
import json
import re
from pathlib import Path

from componentes import esc, icon, REDES, ENTIDAD
from contenido import SERVICIOS, columna, procesos

# Módulo de la versión 3 (prototipo-v1): mapas, gráficas, ilustraciones y páginas inmersivas
_ruta_v3 = Path(__file__).resolve().parents[2] / 'prototipo-v1' / '_construir.py'
_spec = importlib.util.spec_from_file_location('v3', _ruta_v3)
V3 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(V3)

# Plantilla 3D de cada proyecto (assets/js/escenas.js)
PLANTILLA_CASO = {
    'impuesto-vehicular': 'recaudo', 'comparendos': 'recaudo', 'tasa-seguridad': 'recaudo', 'ica-predial': 'recaudo',
    'fotomultas': 'recaudo', 'crediantioquia': 'recaudo', 'catastro-antioquia': 'catastro', 'actualizacion-catastral': 'catastro',
    'gestion-territorial-adr': 'catastro', 'gestion-documental': 'documentos', 'telegestion-las-palmas': 'alumbrado',
    'conectividad-satelital': 'satelital', 'conectividad': 'satelital', 'video-vigilancia': 'camaras', 'mantenimiento-cctv': 'camaras',
    'nodos-seguridad': 'camaras', 'tecnologias-seguridad': 'camaras', 'infraestructura-vial': 'vial', 'mesa-de-servicios': 'datacenter',
    'migracion-ipv6': 'datacenter', 'licenciamiento': 'datacenter', 'software-iu-digital': 'datacenter', 'contact-center': 'datacenter',
    'consultores-sap': 'datacenter', 'energia-antioquia': 'energia',
}
PLANTILLA_SERVICIO = {'estrategias-tecnologicas-del-recaudo': 'recaudo', 'automatizacion-de-la-informacion': 'catastro',
                      'estructuracion-y-gerenciamiento-de-proyectos': 'satelital', 'soluciones-tecnologicas-y-consultoria-especializada': 'datacenter',
                      'seguridad': 'camaras', 'soluciones-energeticas-en-tecnologias-limpias': 'energia'}
ICONO_PLANTILLA = {'recaudo': 'recaudo', 'catastro': 'datos', 'documentos': 'datos', 'alumbrado': 'energia', 'satelital': 'proyectos',
                   'camaras': 'seguridad', 'vial': 'proyectos', 'datacenter': 'consultoria', 'energia': 'energia'}
NOMBRE_PLANTILLA = {'recaudo': 'Recaudo', 'catastro': 'Territorio', 'documentos': 'Archivo digital', 'alumbrado': 'Alumbrado inteligente',
                    'satelital': 'Conectividad', 'camaras': 'Seguridad', 'vial': 'Infraestructura', 'datacenter': 'Datacenter', 'energia': 'Energía'}
INMERSIVA = {'conectividad-satelital': 'proyectos/conectividad-satelital.html', 'conectividad': 'proyectos/conectividad-satelital.html',
             'nodos-seguridad': 'proyectos/seguridad-ciudadana.html', 'mantenimiento-cctv': 'proyectos/seguridad-ciudadana.html',
             'video-vigilancia': 'proyectos/seguridad-ciudadana.html', 'tecnologias-seguridad': 'proyectos/seguridad-ciudadana.html'}


def escena(plantilla, etiqueta):
    return (f'<div class="escena-caso" data-plantilla="{plantilla}" role="img" aria-label="{esc(etiqueta)}">'
            f'<p class="aviso-3d" role="status">Cargando la escena 3D…</p>'
            f'<span class="escena-ayuda" aria-hidden="true">Arrastra para girar</span></div>')


def tarjeta_proyecto(r, c, reveal=True):
    pl = PLANTILLA_CASO.get(c['slug'], 'datacenter')
    serv = ' · '.join(next(s['corto'] for s in SERVICIOS if s['slug'] == x) for x in c['servicios'])
    resumen = esc(c['resumen']) if c['resumen'] else '<span class="pendiente">Contenido pendiente</span>'
    rv = ' data-reveal' if reveal else ''
    inm = '<span class="sello-3d">Experiencia 3D</span>' if c['slug'] in INMERSIVA else '<span class="sello-3d suave">Escena 3D</span>'
    return f'''<article class="proy-card spotlight"{rv} data-tags="{' '.join(c['servicios'])}">
  <div class="proy-holo" aria-hidden="true">{V3.ico_servicio(ICONO_PLANTILLA[pl])}<span class="proy-tipo">{NOMBRE_PLANTILLA[pl]}</span>{inm}</div>
  <div class="proy-cuerpo"><span class="badge">{esc(serv)}</span><h3><a href="{r}casos/{c['slug']}.html">{esc(c['titulo'])}</a></h3><p>{resumen}</p><span class="link-arrow">Ver proyecto {icon('flecha')}</span></div>
</article>'''


def _pesos(t):
    return int(re.sub(r'[^\d]', '', t))


def datos_recaudo():
    col = columna()
    filas = [f for f in col['filas'] if f[0] != 'Total']
    return {'anios': [int(f[0]) for f in filas], 'impuesto': [_pesos(f[1]) for f in filas], 'sancion': [_pesos(f[2]) for f in filas],
            'intereses': [_pesos(f[3]) for f in filas], 'total': [_pesos(f[4]) for f in filas], 'sistematizacion': [_pesos(f[5]) for f in filas]}


def senales():
    """Señales simuladas para el panel en vivo del hero (a partir de los datos ilustrativos)."""
    con, seg = V3.CON, V3.SEG
    nombres = {m['c']: m['n'] for m in V3.GEO['municipios']}
    a = sorted(con, key=lambda c: -con[c]['s'])[:6]
    b = sorted(seg, key=lambda c: -seg[c])[:6]
    out = []
    for x, y in zip(a, b):
        out.append(('sede', f'Sede educativa en línea · {nombres[x]}'))
        out.append(('camara', f'Cámaras reportando al nodo · {nombres[y]}'))
    return out


def inicio(r, casos, mv, equipo, total_docs, cats):
    sub_tec = {'etiquetas': ['Satelital (órbita baja)', 'Radioenlace'], 'valores': [784, 86], 'colores': ['#b5c73a', '#1c2d4c'], 'centro': 'sedes conectadas'}
    d_sub = {'categorias': V3.SUBS, 'metricas': [{'nombre': 'Sedes educativas conectadas', 'unidad': 'sedes', 'valores': V3.sedes_sub}, {'nombre': 'Cámaras integradas', 'unidad': 'cámaras', 'valores': V3.cam_sub}]}
    s_sub = {'categorias': V3.SUBS, 'metricas': [{'nombre': 'Cámaras integradas', 'unidad': 'cámaras', 'valores': V3.cam_sub}, {'nombre': 'Municipios conectados', 'unidad': 'municipios', 'valores': V3.mun_seg_sub}]}
    rec = datos_recaudo()
    nombres = {m['c']: (m['n'], m['r']) for m in V3.GEO['municipios']}
    por_sub = {}
    for c, v in V3.SEG.items():
        if v > 0:
            por_sub.setdefault(nombres[c][1], []).append(nombres[c][0])
    lista48 = ''.join(f'<div class="sub-grupo"><h4>{esc(s)} <span>{len(ms)}</span></h4><p>{esc(", ".join(sorted(ms)))}</p></div>' for s, ms in sorted(por_sub.items(), key=lambda x: -len(x[1])))
    ticker = ''.join(f'<li class="{t}"><span class="pulso" aria-hidden="true"></span>{esc(x)}</li>' for t, x in senales())
    meta = ''.join(f'''<div class="meta-barra"><p><strong>{t}</strong><span>870 {txt} · {round(v / m * 100)} %</span></p><div role="progressbar" aria-label="{t}" aria-valuemin="0" aria-valuemax="{m}" aria-valuenow="{v}"><i style="width:{v / m * 100:.1f}%"></i></div></div>'''
                   for t, v, m, txt in [('Sedes con servicio confirmado', 870, 1228, 'de 1.228'), ('Aporte a la meta departamental 2024-2027', 870, 3414, 'de 3.414')])
    # servicios con objeto 3D por servicio (tres.js)
    figs = ''.join(f'<figure style="--c:{s["color"]}"><img src="{r}assets/img/{s["img"]}" alt="" width="360" height="360" loading="lazy"><figcaption aria-hidden="true">0{i + 1}</figcaption></figure>' for i, s in enumerate(SERVICIOS))
    pasos = ''.join(f'''<article class="scrolly-step"><span class="num">0{i + 1} / 0{len(SERVICIOS)}</span><h3>{esc(s["nombre"])}</h3>
  <ul>{''.join(f"<li>{esc(c)}</li>" for c in s["capacidades"])}</ul>
  <a class="link-arrow" href="{r}servicios/{s["slug"]}.html">Conocer el servicio<span class="sr-only">: {esc(s["nombre"])}</span> {icon('flecha')}</a></article>''' for i, s in enumerate(SERVICIOS))
    chips = '<button type="button" class="chip" data-filter="todos" aria-pressed="true">Todos</button>' + ''.join(f'<button type="button" class="chip" data-filter="{s["slug"]}" aria-pressed="false">{esc(s["corto"])}</button>' for s in SERVICIOS)
    tarjetas = ''.join(tarjeta_proyecto(r, c, reveal=False) for c in casos.values())
    avatares = ''.join(f'<li style="--i:{i}"><img src="{r}assets/img/equipo/{f}.webp" alt="{esc(n)}, {esc(c)}" width="96" height="96" loading="lazy"></li>' for i, (n, c, f) in enumerate(equipo))
    cat_chips = ''.join(f'<a class="chip" href="{r}transparencia/{c["slug"]}.html"><b>{c["num"]}</b> {esc(c["nombre"])}</a>' for c in cats)
    conv, inv = procesos('convocatorias.json'), procesos('invitacion.json')
    clientes = [('Municipio de La Pintada', 1), ('Alcaldía de La Estrella', 2), ('Alcaldía de El Carmen de Viboral', 3), ('Fábrica de Licores y Alcoholes de Antioquia', 4),
                ('IU Digital de Antioquia', 5), ('Ferrocarril de Antioquia', 6), ('IDEA, Instituto para el Desarrollo de Antioquia', 7), ('CrediAntioquia', 8),
                ('Gobernación de Antioquia', 9), ('Alcaldía de Medellín', 10), ('Institución Universitaria Pascual Bravo', 11), ('Policía Nacional de Colombia', 12),
                ('Secretaría de Seguridad y Justicia', 13), ('Secretaría de Educación', 14), ('Secretaría de Suministros y Servicios', 15), ('Municipio de Montebello', 16)]
    logos = ''.join(f'<li><img src="{r}assets/img/clientes/cliente-{n:02d}.webp" alt="{esc(a)}" width="160" height="100" loading="lazy"></li>' for a, n in clientes)
    redes = ''.join(f'<a class="red-card" href="{u}" target="_blank" rel="noopener">{icon(k)}<strong>{n}</strong><span>@valormas</span><span class="sr-only"> (abre en una pestaña nueva)</span></a>' for k, n, u in REDES)
    mil = lambda n: f'{n:,}'.replace(',', '.')

    cuerpo = f'''
<section class="hero-mapa" aria-labelledby="hero-t">
  <div class="hero-trama" aria-hidden="true"></div>
  <div class="hero-escena" id="mapa-hero">{V3.CONTROL_3D}</div>
  <div class="contenedor">
    <div>
      <p class="antetitulo">Valor+ · Gemelo digital de Antioquia</p>
      <h1 id="hero-t">Tecnología que <em>llega</em> a cada territorio</h1>
      <p class="entrada">Integramos conectividad, seguridad, datos y energía para que las entidades públicas de Antioquia presten mejores servicios a la ciudadanía.</p>
      <div class="botones"><a class="boton lima" href="#proyectos">Explorar proyectos en 3D {icon('flecha')}</a><a class="boton borde" href="pqrsd.html">Radicar una PQRSD</a></div>
      {V3.panel_mapa('panel-mapa', 'inicio')}
    </div>
  </div>
  <div class="hud" role="region" aria-label="Actividad de la red (simulación)">
    <p class="hud-titulo"><span class="pulso" aria-hidden="true"></span>En línea · simulación</p>
    <div class="ticker"><ul>{ticker}</ul><ul aria-hidden="true">{ticker}</ul></div>
  </div>
</section>

<section class="seccion celeste" id="cifras" aria-labelledby="cifras-t">
  <div class="contenedor">
    <p class="antetitulo">Impacto</p>
    <h2 id="cifras-t" data-aparece>Resultados que se ven en el territorio</h2>
    <p class="entrada" data-aparece>Toca una cifra para explorarla.</p>
    <div class="cifras cifras-vivas" role="tablist" aria-label="Cifras de impacto" data-aparece>
      <button type="button" class="cifra" role="tab" id="cf-0" aria-controls="cfp-0" aria-selected="true"><span class="n"><span data-cuenta="870">870</span></span><span class="t">sedes educativas rurales con internet confirmado</span><span class="explorar">Explorar {icon('flecha')}</span><svg class="spark" viewBox="0 0 100 30" aria-hidden="true"><path d="M0 28 15 24 30 25 45 18 60 14 75 9 100 3"/></svg></button>
      <button type="button" class="cifra" role="tab" id="cf-1" aria-controls="cfp-1" aria-selected="false" tabindex="-1"><span class="n">+<span data-cuenta="900">900</span></span><span class="t">cámaras integradas al nodo departamental de seguridad</span><span class="explorar">Explorar {icon('flecha')}</span><svg class="spark" viewBox="0 0 100 30" aria-hidden="true"><path d="M0 26 20 22 35 23 50 15 70 12 85 6 100 4"/></svg></button>
      <button type="button" class="cifra" role="tab" id="cf-2" aria-controls="cfp-2" aria-selected="false" tabindex="-1"><span class="n"><span data-cuenta="48">48</span></span><span class="t">municipios conectados a la red de seguridad</span><span class="explorar">Explorar {icon('flecha')}</span><svg class="spark" viewBox="0 0 100 30" aria-hidden="true"><path d="M0 27 25 21 40 22 60 13 80 9 100 5"/></svg></button>
      <button type="button" class="cifra" role="tab" id="cf-3" aria-controls="cfp-3" aria-selected="false" tabindex="-1"><span class="n"><span data-cuenta="9">9</span></span><span class="t">subregiones de Antioquia con presencia de Valor+</span><span class="explorar">Explorar {icon('flecha')}</span><svg class="spark" viewBox="0 0 100 30" aria-hidden="true"><path d="M0 20 12 16 25 21 37 12 50 17 62 9 75 13 87 6 100 8"/></svg></button>
    </div>
    <div class="cifra-panel" role="tabpanel" id="cfp-0" aria-labelledby="cf-0">
      <div class="grid g2" style="align-items:center">
        <figure class="grafica" data-tipo="dona" data-datos="c-tec" data-titulo="Sedes por tecnología"><header><h3>Sedes por tecnología</h3></header><div class="lienzo" style="max-width:300px;margin-inline:auto"></div><details><summary>Ver los datos en tabla</summary><table class="tabla"><thead><tr><th scope="col">Tecnología</th><th scope="col">Sedes</th><th scope="col">%</th></tr></thead><tbody></tbody></table></details></figure>
        <div class="stack">{meta}<a class="boton marino" href="proyectos/conectividad-satelital.html">Recorrer el proyecto en 3D {icon('flecha')}</a></div>
      </div>
    </div>
    <div class="cifra-panel" role="tabpanel" id="cfp-1" aria-labelledby="cf-1" hidden>{V3.grafica_barras('s-sub', 'Cámaras y municipios por subregión', s_sub['metricas'], ['Cámaras', 'Municipios'], V3.NOTA_DATOS)}<p style="margin-top:18px"><a class="boton marino" href="proyectos/seguridad-ciudadana.html">Recorrer la red en 3D {icon('flecha')}</a></p></div>
    <div class="cifra-panel" role="tabpanel" id="cfp-2" aria-labelledby="cf-2" hidden><h3>Municipios integrados a la red, por subregión</h3><div class="sub-grupos">{lista48}</div><p class="nota">{V3.NOTA_DATOS}</p></div>
    <div class="cifra-panel" role="tabpanel" id="cfp-3" aria-labelledby="cf-3" hidden>{V3.grafica_barras('d-sub', 'Presencia por subregión', d_sub['metricas'], ['Sedes conectadas', 'Cámaras integradas'], V3.NOTA_DATOS)}</div>
    <p class="nota" style="margin-top:14px">Cifras de referencia de las fichas de proyecto.</p>
  </div>
</section>

<section class="seccion" id="nosotros" aria-labelledby="nos-t">
  <div class="contenedor nosotros-v4">
    <div data-aparece>
      <p class="antetitulo">Conoce más sobre nosotros</p>
      <h2 id="nos-t">Diez años integrando tecnología para el sector público</h2>
      <p class="entrada">{esc(mv["mision"])}</p>
      <div class="btn-row"><a class="boton marino" href="nosotros.html">Conoce más sobre nosotros {icon('flecha')}</a><a class="boton borde" href="transparencia/informacion-de-la-entidad.html#s-1-2">Estructura orgánica</a></div>
    </div>
    <div class="mv-cards" data-aparece style="--d:120">
      <article class="vidrio"><span class="etq">Propuesta de valor</span><p>{esc(mv["propuesta"])}</p></article>
      <article class="vidrio"><span class="etq">Visión 2027</span><p>{esc(mv["vision"])}</p></article>
    </div>
  </div>
</section>

<section class="seccion celeste" aria-labelledby="serv-t" id="servicios">
  <div class="contenedor">
    <p class="antetitulo">Servicios</p>
    <h2 id="serv-t" data-aparece>Nuestra tecnología a su servicio</h2>
    <div class="scrolly" style="margin-top:2rem">
      <div class="scrolly-visual" aria-hidden="true">{figs}</div>
      <div class="scrolly-steps">{pasos}</div>
    </div>
  </div>
</section>

<section class="seccion marino" id="proyectos" aria-labelledby="proy-t">
  <div class="contenedor">
    <p class="antetitulo">Proyectos</p>
    <h2 id="proy-t" data-aparece>Explora nuestros proyectos en 3D</h2>
    <p class="entrada" data-aparece>Cada proyecto tiene su propia escena 3D. Empieza por los dos recorridos inmersivos.</p>
    <div class="grid g2" style="margin-top:32px">
      <a class="proyecto" href="proyectos/conectividad-satelital.html" data-aparece><div class="arte">{V3.ARTE_CONECTIVIDAD}</div><div class="texto"><span class="etiqueta">Experiencia inmersiva</span><h3>Conectividad satelital para la ruralidad</h3><p>Antenas de órbita baja que conectan sedes educativas donde la fibra no llega.</p><span class="ir">Recorrer en 3D {icon('flecha')}</span></div></a>
      <a class="proyecto" href="proyectos/seguridad-ciudadana.html" data-aparece style="--d:120"><div class="arte">{V3.ARTE_SEGURIDAD}</div><div class="texto"><span class="etiqueta">Experiencia inmersiva</span><h3>Red departamental de seguridad</h3><p>Cámaras en 48 municipios conectadas a un nodo departamental de monitoreo.</p><span class="ir">Recorrer en 3D {icon('flecha')}</span></div></a>
    </div>
    <div class="rail-wrap" style="margin-top:56px">
      <div class="rail-head">
        <div class="chips" role="group" aria-label="Filtrar proyectos por servicio" data-filter-group="#rail-proyectos" data-status="#proy-estado">{chips}</div>
        <div class="rail-controls"><button type="button" class="icon-btn" data-rail="prev" aria-label="Ver proyectos anteriores">{icon('flecha-izq')}</button><button type="button" class="icon-btn" data-rail="next" aria-label="Ver más proyectos">{icon('flecha')}</button></div>
      </div>
      <p id="proy-estado" class="sr-only" aria-live="polite"></p>
      <div class="rail" id="rail-proyectos" tabindex="0" role="region" aria-label="Todos los proyectos, desplazable horizontalmente">{tarjetas}</div>
      <div class="rail-progress" aria-hidden="true"><span></span></div>
    </div>
  </div>
</section>

<section class="seccion" id="opinion" aria-labelledby="op-t">
  <div class="contenedor grid g2" style="align-items:start">
    <div data-aparece>
      <p class="antetitulo">Opinión · Última columna</p>
      <h2 id="op-t">Impuesto vehicular, Valor+ y política social</h2>
      <p class="entrada">“Antioquia no ha dejado de generar ideas, programas, proyectos e instituciones que responden a solución de situaciones cotidianas…”</p>
      <div class="author" style="margin:1.5rem 0"><img src="{r}assets/img/general/autor-alfazar.webp" alt="" width="64" height="64" loading="lazy"><span><strong>Félix Alfazar González Mira</strong>Asesor de la Gerencia General · 15 de octubre de 2026</span></div>
      <div class="btn-row"><a class="boton marino" href="opinion/impuesto-vehicular-valor-y-politica-social.html">Leer la columna {icon('flecha')}</a><a class="boton borde" href="opinion/index.html">Ver todas las columnas</a></div>
    </div>
    <figure class="recaudo" data-aparece style="--d:120" aria-labelledby="rec-t">
      <h3 id="rec-t">Explora el recaudo del impuesto vehicular</h3>
      <p class="nota">Datos publicados en la columna. Mueve el control o presiona reproducir.</p>
      <div class="rec-controles"><button type="button" class="icono-btn" data-rec-play aria-label="Reproducir la evolución año a año">{icon('flecha')}</button><label for="rec-anio" class="sr-only">Año</label><input type="range" id="rec-anio" min="{rec['anios'][0]}" max="{rec['anios'][-1]}" step="1" value="{rec['anios'][-1]}"><output for="rec-anio" id="rec-anio-v">{rec['anios'][-1]}</output></div>
      <p class="rec-total"><span id="rec-total">—</span><small>recaudo total del año</small></p>
      <div class="rec-pila" aria-hidden="true"><i class="imp"></i><i class="san"></i><i class="int"></i></div>
      <dl class="rec-det"><div><dt><i class="imp"></i>Impuesto</dt><dd id="rec-imp">—</dd></div><div><dt><i class="san"></i>Sanción</dt><dd id="rec-san">—</dd></div><div><dt><i class="int"></i>Intereses</dt><dd id="rec-int">—</dd></div></dl>
      <div class="rec-anios" aria-hidden="true">{''.join(f'<span style="--h:{t / max(rec["total"]) * 100:.0f}%" data-rec="{a}"><b></b><em>{a}</em></span>' for a, t in zip(rec['anios'], rec['total']))}</div>
      <p class="sr-only" aria-live="polite" id="rec-vivo"></p>
      <details><summary>Ver los datos en tabla</summary><table class="tabla"><thead><tr><th scope="col">Año</th><th scope="col">Impuesto</th><th scope="col">Sanción</th><th scope="col">Intereses</th><th scope="col">Total</th></tr></thead><tbody>{''.join(f"<tr><th scope='row'>{a}</th><td>$ {mil(i)}</td><td>$ {mil(s)}</td><td>$ {mil(n)}</td><td>$ {mil(t)}</td></tr>" for a, i, s, n, t in zip(rec['anios'], rec['impuesto'], rec['sancion'], rec['intereses'], rec['total']))}</tbody></table></details>
    </figure>
  </div>
</section>

<section class="seccion celeste" id="equipo" aria-labelledby="eq-t">
  <div class="contenedor grid g2" style="align-items:center">
    <div class="equipo-orbita" data-aparece aria-hidden="true"><div class="nucleo"><img src="{r}assets/img/marca/favicon.svg" alt="" width="80" height="80"></div><ul>{avatares}</ul></div>
    <div data-aparece style="--d:120">
      <p class="antetitulo">Acerca del equipo</p>
      <h2 id="eq-t">Personas que impulsan la transformación digital</h2>
      <p class="entrada">Nuestro equipo de expertos en tecnología está comprometido con la excelencia, trabajando juntos para impulsar su éxito con soluciones innovadoras.</p>
      <a class="boton marino" href="nosotros.html#equipo">Conoce al equipo directivo {icon('flecha')}</a>
    </div>
  </div>
</section>

<section class="seccion" id="ciudadania" aria-labelledby="tr-t">
  <div class="contenedor">
    <p class="antetitulo">Transparencia y atención</p>
    <h2 id="tr-t" data-aparece>Información pública y PQRSD a un clic</h2>
    <div class="bento-v4" style="margin-top:28px">
      <div class="b4 b4-tr vidrio-oscuro" data-aparece>
        <span class="etq">Ley 1712 de 2014 · ITA</span>
        <h3>Transparencia y acceso a la información pública</h3>
        <p><strong class="enorme">{mil(total_docs)}</strong> documentos en 13 categorías</p>
        <form class="t-busca" action="buscar.html" role="search"><label for="tr-q" class="sr-only">Buscar documentos de transparencia</label>{icon('buscar')}<input id="tr-q" name="q" type="search" placeholder="Estados financieros, plan de adquisiciones…"><button class="boton lima mini" type="submit">Buscar</button></form>
        <div class="chips">{cat_chips}</div>
      </div>
      <a class="b4 b4-pq" href="pqrsd.html#radicar" data-aparece style="--d:80"><span class="etq">PQRSD</span><h3>Radica tu petición, queja, reclamo, sugerencia o denuncia</h3><p>Asistente en 4 pasos, consulta del estado y encuesta de satisfacción.</p><span class="link-arrow">Radicar ahora {icon('flecha')}</span></a>
      <a class="b4" href="pqrsd.html#consultar" data-aparece style="--d:120"><span class="etq">Consulta</span><h3>¿Ya radicaste?</h3><p>Consulta el estado con tu número de radicado.</p><span class="link-arrow">Consultar {icon('flecha')}</span></a>
      <a class="b4" href="participa.html" data-aparece style="--d:160"><span class="etq">Participa</span><h3>Rendición de cuentas</h3><p>Estrategia, calendario e informes.</p><span class="link-arrow">Participar {icon('flecha')}</span></a>
    </div>
  </div>
</section>

<section class="seccion marino" id="oportunidades" aria-labelledby="opo-t">
  <div class="contenedor">
    <p class="antetitulo">Oportunidades</p>
    <h2 id="opo-t" data-aparece>Trabaja y crece con Valor+</h2>
    <div class="grid g4" style="margin-top:28px">
      <a class="opo" href="proveedores.html" data-aparece><span class="opo-ico">{icon('maletin')}</span><h3>Registro de proveedores</h3><p>Permítenos conocer tus servicios para entregar + valor a nuestra gestión.</p><span class="link-arrow">Inscribirme {icon('flecha')}</span></a>
      <a class="opo" href="hojas-de-vida.html" data-aparece style="--d:80"><span class="opo-ico">{icon('personas')}</span><h3>Trabaja con nosotros</h3><p>Únete a nuestro equipo de trabajo.</p><span class="link-arrow">Enviar hoja de vida {icon('flecha')}</span></a>
      <a class="opo" href="convocatorias.html" data-aparece style="--d:160"><span class="opo-ico">{icon('megafono')}</span><h3>Convocatorias públicas y abreviadas</h3><p><strong class="cuenta-opo">{len(conv)}</strong> procesos publicados con sus documentos.</p><span class="link-arrow">Ver convocatorias {icon('flecha')}</span></a>
      <a class="opo" href="invitacion-abierta.html" data-aparece style="--d:240"><span class="opo-ico">{icon('contrato')}</span><h3>Invitaciones abiertas</h3><p><strong class="cuenta-opo">{len(inv)}</strong> invitaciones para aliados proveedores.</p><span class="link-arrow">Ver invitaciones {icon('flecha')}</span></a>
    </div>
  </div>
</section>

<section class="section tight soft" aria-labelledby="clientes-t">
  <div class="container center"><p class="antetitulo">Confían en nosotros</p><h2 id="clientes-t" data-reveal>Nuestros clientes</h2></div>
  <div class="marquee-wrap" style="margin-top:1.5rem">
    <div class="marquee"><ul class="marquee-track" style="margin:0;padding-left:0">{logos}</ul></div>
    <button type="button" class="btn ghost sm pause-btn" aria-pressed="false">{icon('pausa')}<span>Pausar movimiento</span></button>
  </div>
</section>

<section class="seccion" aria-labelledby="red-t">
  <div class="contenedor">
    <p class="antetitulo">Redes sociales</p>
    <h2 id="red-t" data-aparece>Síguenos</h2>
    <div class="redes-v4" data-aparece>{redes}</div>
  </div>
</section>
'''
    bloques = ''.join(f'<script type="application/json" id="{i}">{json.dumps(d, ensure_ascii=False)}</script>' for i, d in
                      [('c-tec', sub_tec), ('s-sub', s_sub), ('d-sub', d_sub), ('recaudo-datos', rec)])
    return cuerpo + bloques


def paginas_inmersivas():
    """Captura las páginas de proyecto inmersivas de la versión 3 (conectividad y seguridad)."""
    capturas = []
    V3.pagina = lambda ruta, titulo, desc, activo, cuerpo, modulo=True, json_bloques='', vista=None: capturas.append((ruta, titulo, desc, cuerpo + json_bloques, vista))
    V3.conectividad()
    V3.seguridad()
    return capturas
