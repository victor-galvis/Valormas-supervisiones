"""Componentes compartidos del prototipo: íconos, utilidades de texto y plantilla base."""
import html
import re
import datetime
from urllib.parse import urlparse, unquote

MESES = ['enero', 'febrero', 'marzo', 'abril', 'mayo', 'junio', 'julio', 'agosto',
         'septiembre', 'octubre', 'noviembre', 'diciembre']
HOY = datetime.date.today()
FECHA_ACTUALIZACION = f'{HOY.day} de {MESES[HOY.month - 1]} de {HOY.year}'


def esc(s):
    return html.escape(str(s or ''), quote=True)


# Correcciones ortográficas evidentes del contenido actual del sitio
CORRECCIONES = [
    (r'\bContac [Cc]enter', 'Contact Center'), (r'\bCONTAC CENTER', 'CONTACT CENTER'), (r'\bContac center', 'Contact Center'),
    (r'Transformáremos', 'Transformaremos'), (r'Licenciámiento', 'Licenciamiento'), (r'dispoción', 'disposición'),
    (r'dispisición', 'disposición'), (r'multiproposito', 'multipropósito'), (r'Energías renovable\b', 'Energías renovables'),
    (r'enviarlas notificaciones', 'enviar las notificaciones'), (r'\batravés\b', 'a través'), (r'Finacieros', 'Financieros'),
    (r'INFOMACIÓN', 'INFORMACIÓN'), (r'incporporada', 'incorporada'), (r'Adolecentes', 'Adolescentes'),
    (r'\binteres\b', 'interés'), (r'encuenta', 'en cuenta'), (r'esta comprometido', 'está comprometido'),
    (r'Pesosm\.', 'Pesos'), (r'Iva Incluido', 'IVA incluido'), (r'auto mores', 'automotores'), (r'ortófono', 'ortofoto'),
    (r'Economico', 'Económico'), (r'Cartografia\b', 'Cartografía'), (r'Interventoria\b', 'Interventoría'),
    (r'Actualizacion\b', 'Actualización'), (r'Cómo servicio', 'Como servicio'), (r'Indeportes Antioqui\b', 'Indeportes Antioquia'), (r'en el momentos', 'en el momento'),
]


def fix(s):
    s = s or ''
    for a, b in CORRECCIONES:
        s = re.sub(a, b, s)
    s = re.sub(r'\s+', ' ', s)
    s = re.sub(r'([a-záéíóúñ0-9)])\.([A-ZÁÉÍÓÚÑ])', r'\1. \2', s)
    s = re.sub(r'\s+([.,;:)])', r'\1', s)
    s = re.sub(r'\(\s+', '(', s)
    return s.strip()


SIGLAS = ['PQRSD', 'PQRDS', 'SGSST', 'PETI', 'CGA', 'PEI', 'PINAR', 'SUIN', 'TRD', 'SECOP', 'TI', 'IPv6', 'ADR', 'SAP',
          'CCTV', 'ITA', 'MIPG', 'S.A.S', 'POA', 'Valor+', 'PMO', 'MinTIC', 'Antioquia', 'Medellín', 'Colombia', 'IDEA',
          'Ley', 'Decreto', 'Contraloría', 'General', 'Nación', 'N°', 'NUSE', 'LED', 'PTT', 'POC', 'IGAC', 'Rionegro', 'CDP', 'SARLAFT']


def tipo_oracion(s):
    """Convierte TÍTULOS EN MAYÚSCULA a tipo oración, conservando siglas."""
    s = fix(s)
    letras = [c for c in s if c.isalpha()]
    if not letras or sum(c.isupper() for c in letras) / len(letras) < .7:
        return s
    t = s.lower()
    t = t[0].upper() + t[1:] if t else t
    for sig in SIGLAS:
        t = re.sub(r'(?<![\wÁÉÍÓÚáéíóú])' + re.escape(sig.lower()) + r'(?![\wÁÉÍÓÚáéíóú])', sig, t)
    t = re.sub(r',(?=\S)', ', ', t)
    return t


def nombre_archivo(href):
    """Nombre legible a partir de la URL de un archivo."""
    p = unquote(urlparse(href).path).rstrip('/').split('/')[-1]
    p = re.sub(r'\.[a-z0-9]{2,5}$', '', p, flags=re.I)
    p = re.sub(r'[-_+]+', ' ', p).strip()
    return p[:1].upper() + p[1:] if p else href


def extension(href):
    m = re.search(r'\.([a-z0-9]{2,5})(?:$|\?)', urlparse(href).path, flags=re.I)
    ext = (m.group(1).lower() if m else '')
    return ext if ext in ('pdf', 'xlsx', 'xls', 'docx', 'doc', 'pptx', 'zip', 'csv', 'rar') else 'web'


# ---------- Íconos (trazos estilo "lucide", hechos a mano) ----------
I = {
    'buscar': '<circle cx="11" cy="11" r="7"/><path d="m20 20-3.5-3.5"/>',
    'menu': '<path d="M4 7h16M4 12h16M4 17h16"/>',
    'cerrar': '<path d="M6 6l12 12M18 6 6 18"/>',
    'flecha': '<path d="M5 12h14M13 6l6 6-6 6"/>',
    'flecha-izq': '<path d="M19 12H5M11 6l-6 6 6 6"/>',
    'chev': '<path d="m6 9 6 6 6-6"/>',
    'arriba': '<path d="M12 19V5M6 11l6-6 6 6"/>',
    'descarga': '<path d="M12 4v11M7 10l5 5 5-5M5 20h14"/>',
    'externo': '<path d="M14 4h6v6M20 4l-9 9M18 14v5a1 1 0 0 1-1 1H5a1 1 0 0 1-1-1V7a1 1 0 0 1 1-1h5"/>',
    'enlace': '<path d="M10 14a4 4 0 0 0 5.7 0l3-3a4 4 0 0 0-5.7-5.7l-1 1"/><path d="M14 10a4 4 0 0 0-5.7 0l-3 3a4 4 0 0 0 5.7 5.7l1-1"/>',
    'compartir': '<circle cx="18" cy="5" r="3"/><circle cx="6" cy="12" r="3"/><circle cx="18" cy="19" r="3"/><path d="m8.6 13.5 6.8 4M15.4 6.5l-6.8 4"/>',
    'sol': '<circle cx="12" cy="12" r="4"/><path d="M12 2v2M12 20v2M4.9 4.9l1.4 1.4M17.7 17.7l1.4 1.4M2 12h2M20 12h2M4.9 19.1l1.4-1.4M17.7 6.3l1.4-1.4"/>',
    'luna': '<path d="M20 14.5A8 8 0 1 1 9.5 4a6.5 6.5 0 0 0 10.5 10.5z"/>',
    'accesibilidad': '<circle cx="12" cy="4.5" r="1.8"/><path d="M5 8.5c2.3.7 4.6 1 7 1s4.7-.3 7-1M12 9.5v4.5M12 14l-3 6.5M12 14l3 6.5"/>',
    'telefono': '<path d="M5 4h4l2 5-2.5 1.5a11 11 0 0 0 5 5L15 13l5 2v4a2 2 0 0 1-2 2A16 16 0 0 1 3 6a2 2 0 0 1 2-2"/>',
    'correo': '<rect x="3" y="5" width="18" height="14" rx="2"/><path d="m3 7 9 6 9-6"/>',
    'ubicacion': '<path d="M12 21s-7-6.2-7-11.5A7 7 0 0 1 19 9.5C19 14.8 12 21 12 21z"/><circle cx="12" cy="9.5" r="2.5"/>',
    'reloj': '<circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/>',
    'formulario': '<rect x="5" y="3" width="14" height="18" rx="2"/><path d="M9 8h6M9 12h6M9 16h4"/>',
    'escudo': '<path d="M12 3 4 6v6c0 5 3.5 8 8 9 4.5-1 8-4 8-9V6z"/><path d="m9 12 2 2 4-4"/>',
    'edificio': '<rect x="4" y="3" width="16" height="18" rx="1"/><path d="M9 7h1M14 7h1M9 11h1M14 11h1M9 15h1M14 15h1M10 21v-3h4v3"/>',
    'balanza': '<path d="M12 3v18M7 21h10M5 7h14M5 7l-3 6a3 3 0 0 0 6 0zM19 7l-3 6a3 3 0 0 0 6 0z"/>',
    'contrato': '<path d="M14 3H6a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V9z"/><path d="M14 3v6h6M8 13h8M8 17h5"/>',
    'grafica': '<path d="M4 20V10M10 20V4M16 20v-8M22 20H2"/>',
    'personas': '<circle cx="9" cy="8" r="3.5"/><path d="M2.5 20a6.5 6.5 0 0 1 13 0"/><circle cx="17.5" cy="9" r="2.5"/><path d="M16 14.2A5 5 0 0 1 22 19"/>',
    'datos': '<ellipse cx="12" cy="5.5" rx="8" ry="2.5"/><path d="M4 5.5v13c0 1.4 3.6 2.5 8 2.5s8-1.1 8-2.5v-13M4 12c0 1.4 3.6 2.5 8 2.5s8-1.1 8-2.5"/>',
    'estrella': '<path d="m12 3 2.8 5.7 6.2.9-4.5 4.4 1 6.2L12 17.3 6.5 20.2l1-6.2L3 9.6l6.2-.9z"/>',
    'noticias': '<rect x="3" y="4" width="18" height="16" rx="2"/><path d="M7 8h10M7 12h10M7 16h6"/>',
    'candado': '<rect x="5" y="11" width="14" height="10" rx="2"/><path d="M8 11V7a4 4 0 0 1 8 0v4"/>',
    'pesos': '<circle cx="12" cy="12" r="9"/><path d="M15 9.5c-.5-1.2-1.7-2-3-2-1.7 0-3 1-3 2.3 0 3 6 1.7 6 4.6 0 1.3-1.3 2.3-3 2.3-1.4 0-2.6-.8-3-2M12 5.5v13"/>',
    'tramite': '<path d="M9 11l3 3 8-8"/><path d="M20 12v7a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h9"/>',
    'mas': '<path d="M12 5v14M5 12h14"/>',
    'check': '<path d="m5 12 5 5 9-10"/>',
    'chat': '<path d="M4 5h16v11H8l-4 4z"/>',
    'calendario': '<rect x="3" y="5" width="18" height="16" rx="2"/><path d="M3 10h18M8 3v4M16 3v4"/>',
    'maletin': '<rect x="3" y="7" width="18" height="13" rx="2"/><path d="M9 7V5a2 2 0 0 1 2-2h2a2 2 0 0 1 2 2v2M3 13h18"/>',
    'megafono': '<path d="M3 11v2a1 1 0 0 0 1 1h3l6 4V6L7 10H4a1 1 0 0 0-1 1zM17 8a5 5 0 0 1 0 8"/>',
    'corazon': '<path d="M12 20s-7-4.4-7-10a4 4 0 0 1 7-2.6A4 4 0 0 1 19 10c0 5.6-7 10-7 10z"/>',
    'rayo': '<path d="M13 2 4 14h7l-1 8 9-12h-7z"/>',
    'bombilla': '<path d="M9 18h6M10 21h4M12 3a6 6 0 0 0-4 10.5c.7.7 1 1.5 1 2.5h6c0-1 .3-1.8 1-2.5A6 6 0 0 0 12 3z"/>',
    'objetivo': '<circle cx="12" cy="12" r="9"/><circle cx="12" cy="12" r="5"/><circle cx="12" cy="12" r="1"/>',
    'pausa': '<rect x="6" y="5" width="4" height="14" rx="1"/><rect x="14" y="5" width="4" height="14" rx="1"/>',
}
# Redes sociales (relleno)
F = {
    'facebook': '<path d="M14 8h3V4h-3c-2.8 0-4 1.7-4 4.3V10H7v4h3v8h4v-8h3l1-4h-4V8.6c0-.4.3-.6.6-.6z"/>',
    'instagram': '<path d="M12 7a5 5 0 1 0 0 10 5 5 0 0 0 0-10zm0 8.2a3.2 3.2 0 1 1 0-6.4 3.2 3.2 0 0 1 0 6.4zM17.3 5.5a1.2 1.2 0 1 0 0 2.4 1.2 1.2 0 0 0 0-2.4zM12 2c-2.7 0-3 0-4.1.1C4 2.3 2.3 4 2.1 7.9 2 9 2 9.3 2 12s0 3 .1 4.1C2.3 20 4 21.7 7.9 21.9c1.1.1 1.4.1 4.1.1s3 0 4.1-.1c3.9-.2 5.6-1.9 5.8-5.8.1-1.1.1-1.4.1-4.1s0-3-.1-4.1C21.7 4 20 2.3 16.1 2.1 15 2 14.7 2 12 2zm0 1.8c2.7 0 3 0 4 .1 2.7.1 4 1.4 4.1 4.1.1 1 .1 1.3.1 4s0 3-.1 4c-.1 2.7-1.4 4-4.1 4.1-1 .1-1.3.1-4 .1s-3 0-4-.1C5.3 20 4 18.7 3.9 16c-.1-1-.1-1.3-.1-4s0-3 .1-4C4 5.3 5.3 4 8 3.9c1-.1 1.3-.1 4-.1z"/>',
    'x': '<path d="M17.8 3h3.1l-6.8 7.8L22 21h-6.3l-4.9-6.4L5.2 21H2.1l7.3-8.3L1.8 3h6.4l4.4 5.9zm-1.1 16.2h1.7L7.4 4.7H5.6z"/>',
    'linkedin': '<path d="M4.98 3.5a2.5 2.5 0 1 1 0 5 2.5 2.5 0 0 1 0-5zM3 9.5h4V21H3zM9.5 9.5h3.8v1.6h.1c.5-1 1.8-2 3.8-2 4 0 4.8 2.6 4.8 6V21h-4v-5.1c0-1.2 0-2.8-1.7-2.8s-2 1.3-2 2.7V21h-4z"/>',
    'youtube': '<path d="M23 7.2a3 3 0 0 0-2.1-2.1C19 4.6 12 4.6 12 4.6s-7 0-8.9.5A3 3 0 0 0 1 7.2 31 31 0 0 0 .5 12 31 31 0 0 0 1 16.8a3 3 0 0 0 2.1 2.1c1.9.5 8.9.5 8.9.5s7 0 8.9-.5a3 3 0 0 0 2.1-2.1c.4-1.6.5-3.2.5-4.8s-.1-3.2-.5-4.8zM9.8 15V9l5.7 3z"/>',
}


def icon(name, cls=''):
    c = f' class="{cls}"' if cls else ''
    if name in F:
        return f'<svg{c} viewBox="0 0 24 24" fill="currentColor" aria-hidden="true" focusable="false">{F[name]}</svg>'
    return (f'<svg{c} viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" '
            f'stroke-linejoin="round" aria-hidden="true" focusable="false">{I[name]}</svg>')


REDES = [
    ('facebook', 'Facebook', 'https://www.facebook.com/ValorMasOficial/'),
    ('instagram', 'Instagram', 'https://www.instagram.com/valormas/'),
    ('x', 'X (antes Twitter)', 'https://x.com/valormas'),
    ('linkedin', 'LinkedIn', 'https://co.linkedin.com/company/valormasoficial'),
    ('youtube', 'YouTube', 'https://www.youtube.com/channel/UCZujESMNvxTBXYIGdxpMITw'),
]

ENTIDAD = {
    'nombre': 'Valor+ S.A.S.',
    'direccion': 'Calle 41 N.° 52 – 28, Edificio Edatel, piso 3, sector La Alpujarra. Medellín, Antioquia, Colombia',
    'horario': 'Lunes a jueves de 7:30 a. m. a 12:30 p. m. y de 1:30 p. m. a 5:30 p. m. Viernes de 7:30 a. m. a 1:30 p. m. (jornada continua)',
    'telefono': '+57 (604) 444 3747',
    'tel_href': 'tel:+576044443747',
    'ext_pqrsd': 'Ext. 204',
    'linea_gratuita': '01 8000 415 379',
    'lg_href': 'tel:018000415379',
    'pqrsd': 'pqrds@valormas.gov.co',
    'recepcion': 'recepcion@valormas.gov.co',
    'notificaciones': 'notificaciones@valormas.gov.co',
    'transparencia': 'transparencia@valormas.gov.co',
}
