"""Lectura y estructuración del contenido extraído del sitio actual (valormas.gov.co)."""
import json
import re
from pathlib import Path
from componentes import fix, tipo_oracion, nombre_archivo, extension

SRC = Path(__file__).resolve().parent / 'contenido'

# ---------------------------------------------------------------------------
# Servicios (textos actuales de cada página de servicio)
# ---------------------------------------------------------------------------
SERVICIOS = [
    {'slug': 'estrategias-tecnologicas-del-recaudo', 'nombre': 'Estrategias tecnológicas del recaudo', 'corto': 'Recaudo',
     'img': 'servicios/recaudo.webp', 'color': '#00a3e0',
     'capacidades': ['Gestión de liquidación de impuestos', 'Apoyo a la gestión del cobro persuasivo, coactivo y acuerdos de pago',
                     'Actualización de bases de datos fiscales'],
     'casos': ['impuesto-vehicular', 'comparendos', 'tasa-seguridad', 'ica-predial', 'fotomultas']},
    {'slug': 'automatizacion-de-la-informacion', 'nombre': 'Automatización de la información', 'corto': 'Automatización',
     'img': 'servicios/automatizacion.webp', 'color': '#009549',
     'capacidades': ['Catastro multipropósito', 'Levantamiento, procesamiento y análisis de datos en el territorio', 'Telegestión',
                     'Transformación digital de la gestión documental'],
     'casos': ['catastro-antioquia', 'actualizacion-catastral', 'gestion-documental', 'gestion-territorial-adr', 'telegestion-las-palmas']},
    {'slug': 'estructuracion-y-gerenciamiento-de-proyectos', 'nombre': 'Estructuración y gerenciamiento de proyectos', 'corto': 'Proyectos',
     'img': 'servicios/proyectos.webp', 'color': '#1f6fc4',
     'capacidades': ['Gerenciamiento de proyectos', 'Prestación de servicios de la naturaleza de los centros de servicios compartidos'],
     'casos': ['conectividad-satelital', 'video-vigilancia', 'crediantioquia', 'infraestructura-vial', 'mantenimiento-cctv', 'tecnologias-seguridad']},
    {'slug': 'soluciones-tecnologicas-y-consultoria-especializada', 'nombre': 'Soluciones tecnológicas y consultoría especializada', 'corto': 'Consultoría',
     'img': 'servicios/consultoria.webp', 'color': '#6c5ce7',
     'capacidades': ['Datacenter', 'Migración a protocolo IPv6', 'Licenciamiento', 'Hardware y software', 'Mesa de servicios',
                     'Conectividad', 'Ciberseguridad', 'Especialistas SAP', 'Contact Center'],
     'casos': ['mesa-de-servicios', 'migracion-ipv6', 'licenciamiento', 'conectividad', 'software-iu-digital', 'contact-center', 'consultores-sap']},
    {'slug': 'seguridad', 'nombre': 'Seguridad', 'corto': 'Seguridad',
     'img': 'servicios/seguridad.webp', 'color': '#e17055',
     'capacidades': ['Centros de monitoreo y control', 'Circuitos cerrados de televisión (CCTV)', 'Sistemas de control de acceso'],
     'casos': ['mantenimiento-cctv', 'nodos-seguridad']},
    {'slug': 'soluciones-energeticas-en-tecnologias-limpias', 'nombre': 'Soluciones energéticas en tecnologías limpias', 'corto': 'Energía',
     'img': 'servicios/energia.webp', 'color': '#b8d430',
     'capacidades': ['Soluciones fotovoltaicas', 'Iluminación eficiente', 'Energías renovables'],
     'casos': ['energia-antioquia']},
]
SERVICIO_POR_SLUG = {s['slug']: s for s in SERVICIOS}

# ---------------------------------------------------------------------------
# Casos de éxito ("Ofertas de Valor+")
# ---------------------------------------------------------------------------
CASOS_FUENTE = {
    'impuesto-vehicular': ('recaudo-del-impuesto-vehicular-del-departamento-de-antioquia', 'Recaudo del impuesto vehicular de Antioquia', None),
    'comparendos': ('recaudo-de-comparendos-gerencia-de-seguridad-vial-del-departamento-de-antioquia', 'Recaudo de comparendos del Departamento de Antioquia', None),
    'tasa-seguridad': ('recaudo-tasa-de-seguridad', 'Recaudo de la tasa de seguridad', 'vacio'),
    'ica-predial': ('gestion-de-recaudo-y-notificaciones-del-ica-y-predial-secretaria-de-hacienda-de-la-alcaldia-de-medellin', 'Recaudo ICA y predial de Medellín', None),
    'fotomultas': ('gestion-de-recaudo-y-notificacionesde-las-fotomultas-secretaria-de-movilidad-de-la-alcaldia-de-medellin', 'Recaudo de fotomultas de Movilidad Medellín', None),
    'catastro-antioquia': ('concesion-catastro-departamental-de-antioquia', 'Concesión Catastro Antioquia', None),
    'actualizacion-catastral': ('actualizacion-catastral-municipios-de-antioquia', 'Actualización catastral', None),
    'gestion-documental': ('transformacion-digital-del-la-gestion-documental', 'Gestión documental', None),
    'gestion-territorial-adr': ('gestion-territorial-agencia-de-desarrollo-rural-adr', 'Gestión territorial ADR', None),
    'telegestion-las-palmas': ('telegestion-avenida-las-palmas', 'Telegestión avenida Las Palmas', None),
    'conectividad-satelital': ('conectividad-starlink', 'Conectividad a internet satelital', None),
    'video-vigilancia': ('video-vigilancia-ciudadana', 'Videovigilancia ciudadana', 'duplicado:Contact Center'),
    'crediantioquia': ('estructuracion-de-la-primera-fintech-publica-crediantioquia', 'CrediAntioquia', None),
    'infraestructura-vial': ('infraestructura-vial', 'Infraestructura vial', None),
    'mantenimiento-cctv': ('mantenimiento-preventivo-y-correctivo-de-circuitos-cerrados-de-television-de-los-municipios-de-antioquia', 'Mantenimiento de CCTV', None),
    'tecnologias-seguridad': ('estructuracion-del-proyecto-de-integracion-de-sistemas-de-informacion-y-tecnologias-para-la-seguridad-convivencia-y-acceso-a-la-justicia-en-el-departamento-de-antioquia', 'Tecnologías para la seguridad', 'duplicado:Infraestructura vial'),
    'mesa-de-servicios': ('mesa-de-servicios', 'Mesa de servicios', None),
    'migracion-ipv6': ('migracion-ipv6', 'Migración IPv6', None),
    'licenciamiento': ('licenciamiento', 'Licenciamiento', None),
    'conectividad': ('conectividad-proyectos', 'Conectividad en sedes educativas', None),
    'software-iu-digital': ('software-iu-digital', 'Software – IU Digital', None),
    'contact-center': ('contact-center-para-elagendamiento-de-citas-dela-unidad-prestadora-de-saludde-antioquia-policia-nacional', 'Contact Center', None),
    'consultores-sap': ('consultores-especializados-en-sap', 'Consultores especializados en SAP', None),
    'nodos-seguridad': ('implementacion-de-sistemas-tecnologicos-para-la-seguridad-perimetral-camaras-de-seguridad-centros-de-monitoreo-y-control', 'Nodos para la seguridad', None),
    'energia-antioquia': ('energia-por-antioquia', 'Energía por Antioquia', None),
}
SECCIONES = {'OBJETIVO': 'Objetivo', 'IMPACTO': 'Impacto', 'LOGROS': 'Logros', 'CIFRAS O DATOS DESTACABLES': 'Cifras o datos destacables',
             'ALCANCE': 'Alcance', 'DURACIÓN': 'Duración'}
ALT_GRAFICA_MESA = 'Gráfica del informe de operación de la Mesa de Servicios MEGANT con el cumplimiento mensual de los acuerdos de nivel de servicio'


def _leer_caso(slug):
    archivo, titulo, nota = CASOS_FUENTE[slug]
    lineas = [l.strip() for l in (SRC / 'casos' / f'{archivo}.txt').read_text(encoding='utf-8').splitlines()]
    lineas = [l for l in lineas if l and not l.startswith('[A]')]
    # saltar encabezado ("Oferta de Valor +", imagen y título original)
    i = 0
    while i < len(lineas) and not lineas[i].startswith('[IMG]'):
        i += 1
    i += 2  # imagen + título
    if slug == 'energia-antioquia':
        i = next(k for k, l in enumerate(lineas) if l.startswith('Energía Por Antioquia')) + 1
    intro, bloques, actual = [], [], None
    resto = lineas[i:]
    for k, l in enumerate(resto):
        sig = resto[k + 1] if k + 1 < len(resto) else ''
        if l in SECCIONES:
            if actual is None:
                actual = {'titulo': None, 'secciones': []}
                bloques.append(actual)
            actual['secciones'].append({'nombre': SECCIONES[l], 'items': [], 'figuras': []})
        elif sig == 'OBJETIVO' and actual is not None:
            actual = {'titulo': fix(l), 'secciones': []}
            bloques.append(actual)
        elif sig == 'OBJETIVO' and actual is None and k > 0:
            actual = {'titulo': fix(l), 'secciones': []}
            bloques.append(actual)
        elif l.startswith('[IMG]'):
            if actual and actual['secciones']:
                actual['secciones'][-1]['figuras'].append(l.split()[1])
        elif actual is None:
            intro.append(fix(l))
        else:
            actual['secciones'][-1]['items'].append(fix(l))
    # limpiar marcadores de posición ("Lorem ipsum") y secciones vacías
    for b in bloques:
        for s in b['secciones']:
            if any('lorem ipsum' in x.lower() for x in s['items']):
                s['items'], s['pendiente'] = [], 'El sitio actual muestra texto de relleno (“Lorem ipsum”) en esta sección.'
            elif not s['items'] and not s['figuras']:
                s['pendiente'] = 'Sección sin contenido en el sitio actual.'
    if slug == 'mantenimiento-cctv' and intro and intro[0] == 'Mantenimiento CCTV':
        intro = intro[1:]
    return {'slug': slug, 'titulo': titulo, 'intro': intro, 'bloques': bloques, 'nota': nota, 'img': f'casos/{slug}.webp'}


def casos():
    out = {}
    for slug in CASOS_FUENTE:
        c = _leer_caso(slug)
        c['servicios'] = [s['slug'] for s in SERVICIOS if slug in s['casos']]
        if c['nota'] and c['nota'].startswith('duplicado'):
            otro = c['nota'].split(':', 1)[1]
            c['bloques'] = []
            c['pendiente'] = (f'En el sitio actual esta ficha repite el contenido del caso “{otro}”. '
                              'Se requiere el texto propio de este proyecto.')
        elif c['nota'] == 'vacio':
            c['bloques'] = []
            c['pendiente'] = 'En el sitio actual esta ficha no tiene contenido.'
        elif all(s.get('pendiente') for b in c['bloques'] for s in b['secciones']):
            c['bloques'] = []
            c['pendiente'] = 'En el sitio actual esta ficha solo tiene texto de relleno (“Lorem ipsum”).'
        resumen = ''
        for b in c['bloques']:
            for s in b['secciones']:
                if s['nombre'] == 'Objetivo' and s['items']:
                    resumen = ' '.join(s['items'])
                    break
            if resumen:
                break
        resumen = re.sub(r'^(Gobernación de Antioquia|La Gobernación de Antioquia):\s*', '', resumen)
        c['resumen'] = (resumen[:150].rsplit(' ', 1)[0] + '…') if len(resumen) > 150 else resumen
        out[slug] = c
    return out


# ---------------------------------------------------------------------------
# Bloques genéricos a partir de la extracción secuencial (h / t / a)
# ---------------------------------------------------------------------------
PAGINAS_ANTIGUAS = {
    '/pqrds/': 'pqrsd.html', '/radicar/': 'pqrsd.html#radicar', '/pqrds-consultar/': 'pqrsd.html#consultar',
    '/encuesta-de-satisfaccion-pqrds/': 'pqrsd.html#encuesta', '/mecanismos-de-contacto/': 'pqrsd.html',
    '/participa/': 'participa.html', '/proveedores/': 'proveedores.html', '/transparencia/': 'transparencia/index.html',
    '/atencion-y-servicios-a-la-ciudadania/': 'atencion-ciudadania.html', '/contactanos/': 'contacto.html',
    '/convocatorias-publicas-abreviadas/': 'convocatorias.html', '/invitacion-abierta/': 'invitacion-abierta.html',
    '/sobre-nosotros/': 'nosotros.html', '/banco-hojas-de-vida/': 'hojas-de-vida.html', '/opinion/': 'opinion/index.html',
}
CABECERAS_TABLA = [
    ['ENTIDAD', 'PAGINA WEB', 'TELÉFONO'],
    ['Nombre', 'Fecha', 'Año'],
    ['Tipo de acto', 'Fecha de expedición', 'Descripción corta', 'Enlace de descarga'],
]
RUIDO = {'Search', 'Busca en', 'Ir a la página de'}
RE_FECHA = re.compile(r'^\(?\s*(?:fecha\s+de\s+publicaci[oó]n|publicado)\s*:?\s*(.+?)\)?\.?$', re.I)
RE_FECHA_EN_TITULO = re.compile(r'\s*\(\s*(?:fecha\s+de\s+publicaci[oó]n|publicado)\s*:?\s*([^)]*)\)\s*', re.I)
RE_NUM = re.compile(r'^(\d{1,2}(?:\.\d{1,2})*)\.?\s+(.*)$')
RE_ANIO = re.compile(r'^(20\d\d)(\s*-\s*20\d\d)?$')


def interno(href):
    """Devuelve (ruta_local | None) para enlaces al sitio antiguo que tienen equivalente en el prototipo."""
    m = re.match(r'^https?://(?:www\.)?valormas\.gov\.co(/[^?#]*)?$', href or '')
    if not m:
        return None
    path = m.group(1) or '/'
    if path in ('', '/'):
        return 'index.html'
    return PAGINAS_ANTIGUAS.get(path if path.endswith('/') else path + '/')


def titulo_enlace(texto, href):
    t = fix(texto)
    if not t or t.upper() in ('ENLACE', 'AQUÍ', 'AQUI', 'LINK', 'IMG') or re.match(r'^https?://', t):
        if 'secop' in href:
            return 'Consultar el proceso en SECOP II' if 'community.secop' in href else 'Consultar en SECOP'
        if 'datos.gov.co' in href:
            return 'Consultar en el portal de datos abiertos (datos.gov.co)'
        if re.search(r'\.(pdf|xlsx?|docx?|pptx|zip)$', href, re.I):
            return nombre_archivo(href)
        dom = re.sub(r'^www\.', '', re.sub(r'^https?://', '', href).split('/')[0])
        return f'Ir a {dom}'
    return t


def bloques_desde_nodos(nodos):
    """Convierte la secuencia extraída en bloques: h, p, label, doc, link, tabla, lista."""
    out, buf, i = [], [], 0

    def vaciar():
        nonlocal buf
        parrafos = []
        for t in buf:
            t = t.strip()
            if not t or t in RUIDO:
                continue
            prev = parrafos[-1] if parrafos else None
            prev_mayus = prev is not None and prev.upper() == prev and any(c.isalpha() for c in prev)
            cur_mayus = t.upper() == t and any(c.isalpha() for c in t) and len(t) > 3
            if prev is not None and not prev_mayus and not cur_mayus and (
                    not prev.rstrip().endswith(('.', ':', ';', '?', '!', ')')) or re.match(r'^[a-záéíóúñ(.,;:)–\-"“”]', t) or prev.endswith('(')):
                parrafos[-1] = prev + ' ' + t
            else:
                parrafos.append(t)
        for p in parrafos:
            p = fix(p)
            mf = RE_FECHA.match(p)
            if mf and out and out[-1]['k'] == 'doc' and not out[-1].get('fecha'):
                out[-1]['fecha'] = mf.group(1).strip(' )')
                continue
            if p.upper() == p and any(c.isalpha() for c in p) and len(p) < 90:
                out.append({'k': 'label', 'text': tipo_oracion(p)})
            else:
                out.append({'k': 'p', 'text': p})
        buf = []

    while i < len(nodos):
        n = nodos[i]
        if n['k'] == 't':
            # ¿inicio de una tabla conocida?
            for cab in CABECERAS_TABLA:
                if [x.get('text') for x in nodos[i:i + len(cab)]] == cab and all(x['k'] == 't' for x in nodos[i:i + len(cab)]):
                    vaciar()
                    j, celdas = i + len(cab), []
                    while j < len(nodos) and nodos[j]['k'] != 'h':
                        x = nodos[j]
                        if x['k'] == 't' and x['text'] not in RUIDO:
                            celdas.append({'text': fix(x['text'])})
                        elif x['k'] == 'a':
                            celdas.append({'text': titulo_enlace(x['text'], x['href']), 'href': x['href']})
                        j += 1
                    filas = [celdas[k:k + len(cab)] for k in range(0, len(celdas), len(cab))]
                    out.append({'k': 'tabla', 'cab': [tipo_oracion(c) for c in cab], 'filas': filas})
                    i = j
                    break
            else:
                buf.append(n['text'])
                i += 1
            continue
        vaciar()
        if n['k'] == 'h':
            txt = fix(n['text'])
            if n.get('lvl', 3) >= 4 and (len(txt) > 90 or n.get('lvl') >= 5):
                out.append({'k': 'p', 'text': txt})
            else:
                m = RE_NUM.match(txt)
                if RE_ANIO.match(txt):
                    out.append({'k': 'anio', 'text': txt})
                elif m:
                    out.append({'k': 'h', 'num': m.group(1), 'text': tipo_oracion(m.group(2)), 'depth': m.group(1).count('.') + 1})
                else:
                    out.append({'k': 'h', 'num': None, 'text': tipo_oracion(txt), 'depth': 9})
        elif n['k'] == 'a':
            href = n['href']
            if href.startswith('mailto:') or href.startswith('tel:'):
                txt = fix(n['text']) or href.split(':', 1)[1]
                if out and out[-1]['k'] in ('p', 'label') and len(out[-1]['text']) < 40:
                    prev = out.pop()
                    out.append({'k': 'link', 'label': prev['text'].rstrip(':'), 'text': txt, 'href': href})
                else:
                    out.append({'k': 'link', 'label': None, 'text': txt, 'href': href})
            else:
                titulo = titulo_enlace(n['text'], href)
                fecha = None
                mf = RE_FECHA_EN_TITULO.search(titulo)
                if mf:
                    fecha = mf.group(1).strip()
                    titulo = RE_FECHA_EN_TITULO.sub(' ', titulo).strip(' -–')
                local = interno(href)
                out.append({'k': 'doc', 'titulo': titulo, 'href': href, 'local': local, 'fecha': fecha,
                            'ext': 'web' if local else extension(href)})
        i += 1
    vaciar()
    # listas compactas: rachas de 6+ párrafos cortos sin punto final
    res, k = [], 0
    while k < len(out):
        j = k
        while j < len(out) and out[j]['k'] == 'p' and len(out[j]['text']) < 70 and not out[j]['text'].endswith('.'):
            j += 1
        if j - k >= 6:
            res.append({'k': 'lista', 'items': [x['text'] for x in out[k:j]]})
            k = j
        else:
            res.append(out[k])
            k += 1
    return res


# ---------------------------------------------------------------------------
# Transparencia (Ley 1712 de 2014 — Res. MinTIC 1519 de 2020, Anexo 2)
# ---------------------------------------------------------------------------
CATEGORIAS = {
    '1': ('informacion-de-la-entidad', 'Información de la entidad', 'Misión, visión, estructura orgánica, procesos, directorios y junta directiva.', 'edificio'),
    '2': ('normativa', 'Normativa', 'Normas aplicables, decisiones empresariales y buscador de normas.', 'balanza'),
    '3': ('contratacion', 'Contratación', 'Plan anual de adquisiciones, información y ejecución contractual, manual de contratación.', 'contrato'),
    '4': ('planeacion-presupuesto-e-informes', 'Planeación, presupuesto e informes', 'Presupuesto, ejecución, planes institucionales, informes de gestión y de control.', 'grafica'),
    '5': ('tramites', 'Trámites', 'Mecanismos para presentar solicitudes, quejas y reclamos.', 'tramite'),
    '6': ('participa', 'Participa', 'Participación ciudadana y rendición de cuentas.', 'personas'),
    '7': ('datos-abiertos', 'Datos abiertos', 'Instrumentos de gestión de la información y datos abiertos.', 'datos'),
    '8': ('grupos-de-interes', 'Información específica para grupos de interés', 'Información para niñas, niños, adolescentes, mujeres y otros grupos.', 'corazon'),
    '9': ('reporte-de-informacion-especifica', 'Obligación de reporte de información específica', 'Estados financieros y certificados de accesibilidad.', 'pesos'),
    '10': ('informacion-tributaria', 'Información tributaria en entidades territoriales locales', 'Aplicabilidad de la información tributaria territorial.', 'pesos'),
    '11': ('atencion-y-servicios-a-la-ciudadania', 'Atención y servicios a la ciudadanía', 'Canales de atención, política de servicio y carta de trato digno.', 'chat'),
    '12': ('noticias', 'Noticias', 'Boletines “Hitos de Valor”.', 'noticias'),
    '13': ('condiciones-tecnicas-y-seguridad-web', 'Condiciones técnicas mínimas y de seguridad web', 'Políticas de seguridad digital e incidentes.', 'candado'),
}


def transparencia():
    nodos = json.loads((SRC / 'transparencia.json').read_text(encoding='utf-8'))
    # quitar la introducción y el título de página
    inicio = next(k for k, x in enumerate(nodos) if x['k'] == 'h' and x['text'].startswith('1. Información'))
    intro = [x['text'] for x in nodos[:inicio] if x['k'] == 't']
    bloques = bloques_desde_nodos(nodos[inicio:])
    cats, cat, sec = [], None, None
    for b in bloques:
        if b['k'] == 'h' and b['num'] and b['depth'] == 1 and b['num'] in CATEGORIAS:
            slug, nombre, desc, ico = CATEGORIAS[b['num']]
            cat = {'num': b['num'], 'slug': slug, 'nombre': nombre, 'desc': desc, 'icono': ico, 'intro': [], 'secciones': []}
            cats.append(cat)
            sec = None
            continue
        if b['k'] == 'h' and b['num'] and b['depth'] == 2:
            sec = {'num': b['num'], 'titulo': b['text'], 'bloques': []}
            cat['secciones'].append(sec)
            continue
        (sec['bloques'] if sec else cat['intro']).append(b)
    for c in cats:
        c['docs'] = sum(1 for s in c['secciones'] for b in s['bloques'] if b['k'] == 'doc') + sum(1 for b in c['intro'] if b['k'] == 'doc')
    return {'intro': [fix(p) for p in re.split(r'(?<=\.)\s+(?=Según)', ' '.join(intro))], 'categorias': cats}


def mision_vision():
    """Textos de la sección 1.1 (los bloques genéricos no conservan el orden de columnas)."""
    nodos = json.loads((SRC / 'transparencia.json').read_text(encoding='utf-8'))
    textos = [fix(x['text']) for x in nodos if x['k'] == 't']
    buscar = lambda pref: next((t for t in textos if t.startswith(pref)), '')
    i = textos.index('DESDE EL HACER') + 1
    valores = []
    while i < len(textos) and not textos[i].startswith('OE 1'):
        nombre = textos[i].rstrip(':')
        desc = textos[i + 1].lstrip(': ').strip()
        valores.append({'nombre': nombre, 'texto': desc[:1].upper() + desc[1:]})
        i += 2
    integridad = {'Honestidad', 'Respeto', 'Compromiso', 'Diligencia', 'Justicia'}
    objetivos = []
    while i < len(textos) and textos[i].startswith('OE '):
        m = re.match(r'OE (\d)\s+(.*)$', textos[i])
        objetivos.append({'n': int(m.group(1)), 'titulo': m.group(2), 'texto': textos[i + 1]})
        i += 2
    return {
        'propuesta': buscar('Habilitador'),
        'mision': buscar('Creadores e integradores'),
        'vision': buscar('Para 2027'),
        'ser': [v for v in valores if v['nombre'] in integridad],
        'hacer': [v for v in valores if v['nombre'] not in integridad],
        'objetivos': objetivos,
    }


# ---------------------------------------------------------------------------
# Convocatorias e invitaciones
# ---------------------------------------------------------------------------
def procesos(nombre_json):
    nodos = json.loads((SRC / nombre_json).read_text(encoding='utf-8'))
    out, anio, proc = [], None, None
    for n in nodos:
        if n['k'] == 'h':
            t = fix(n['text'])
            if RE_ANIO.match(t):
                anio, proc = t, None
            elif t.rstrip(':') in ('Documentos del proceso', 'Documentos') and proc:
                continue
            elif proc and not re.search(r'convocatoria|invitaci[oó]n|proceso|solicitud', t, re.I):
                proc['desc'].append(t if t.endswith(':') else t + ':')
            else:
                proc = {'anio': anio, 'titulo': tipo_oracion(t), 'desc': [], 'docs': [], 'secop': None}
                out.append(proc)
        elif n['k'] == 't':
            t = fix(n['text'])
            if not t or t.startswith('<') or t in ('Enlace SECOP:', 'Documentos del proceso:', '“', '”', ':') or len(t) < 3:
                continue
            if proc is None:
                proc = {'anio': anio, 'titulo': f'Procesos {anio}', 'desc': [], 'docs': [], 'secop': None}
                out.append(proc)
            if proc['desc'] and not proc['desc'][-1].endswith(('.', ':')):
                proc['desc'][-1] += ' ' + t
            else:
                proc['desc'].append(t)
        elif n['k'] == 'a':
            if proc is None or (proc['titulo'].startswith('Procesos') is False and proc['anio'] != anio):
                proc = {'anio': anio, 'titulo': f'Procesos {anio}', 'desc': [], 'docs': [], 'secop': None}
                out.append(proc)
            href = n['href']
            if 'secop' in href and re.match(r'^https?://', fix(n['text']) or 'http'):
                proc['secop'] = href
                continue
            proc['docs'].append({'titulo': titulo_enlace(n['text'], href), 'href': href, 'ext': extension(href)})
    for p in out:
        p['desc'] = [tipo_oracion(d.replace('“ ', '“').replace(' ”', '”')) for d in p['desc']]
        p['id'] = re.sub(r'[^a-z0-9]+', '-', p['titulo'].lower().replace('°', '')).strip('-')
    return [p for p in out if p['docs'] or p['desc'] or p['secop']]


def participa():
    nodos = json.loads((SRC / 'participa.json').read_text(encoding='utf-8'))
    inicio = next(k for k, x in enumerate(nodos) if x['k'] == 'h' and x['text'].startswith('6.1'))
    return bloques_desde_nodos(nodos[inicio:])


# ---------------------------------------------------------------------------
# Columna de opinión
# ---------------------------------------------------------------------------
def columna():
    lineas = [l.strip() for l in (SRC / 'columna-impuesto-vehicular.txt').read_text(encoding='utf-8').splitlines() if l.strip()]
    cuerpo = [l for l in lineas if not l.startswith(('[IMG]', '#'))]
    k = cuerpo.index('Veamos cifras:')
    antes = cuerpo[:k + 1]
    cab = cuerpo[k + 1:k + 7]
    filas, j = [], k + 7
    while j + 6 <= len(cuerpo) and (re.match(r'^(20\d\d|Total)$', cuerpo[j])):
        filas.append(cuerpo[j:j + 6])
        j += 6
    despues = [l for l in cuerpo[j:] if not l.startswith('Por:')]
    return {'antes': [fix(x) for x in antes], 'cab': cab, 'filas': filas, 'despues': [fix(x) for x in despues]}
