# Prototipo de rediseño · valormas.gov.co

Prototipo navegable en HTML, CSS y JavaScript (sin frameworks) para el nuevo sitio de **Valor+ S.A.S.**
Usa la marca actual (logo, colores) y **los textos reales del sitio vigente**. El diseño es moderno y animado,
con animaciones al estilo de apple.com, y cumple los lineamientos de MinTIC, GOV.CO, el ITA y WCAG.

## Cómo verlo

```bash
cd rediseno-sitio
python3 -m http.server 8000
# abrir http://localhost:8000
```

También funciona abriendo `index.html` directamente en el navegador, pero **las escenas 3D necesitan un servidor**
(el servidor local de arriba, Netlify o cualquier hosting). Sin servidor se ven las animaciones CSS y 2D de respaldo.

## Qué incluye (64 páginas)

| Sección | Páginas |
|---|---|
| Inicio | Hero animado, cifras, efecto de zoom con scroll, servicios en narrativa fija, casos, accesos rápidos, opinión, equipo, clientes |
| Nosotros | Misión, visión, valores (desde el ser / desde el hacer), por qué elegirnos, equipo principal, objetivos estratégicos |
| Servicios | Página general y 6 páginas de servicio |
| Casos de éxito | Listado con filtro por servicio y 25 fichas de caso |
| Opinión | Listado y columna con tabla de datos accesible |
| Transparencia | Página principal y **13 categorías** (Ley 1712 / Res. 1519, Anexo 2) con **2.344 documentos** organizados por sección y vigencia |
| Atención al ciudadano | Canales, trámites, normatividad, documentos y agendamiento de citas (propuesto) |
| PQRSD | Asistente de radicación en 4 pasos, consulta por radicado y encuesta de satisfacción |
| Participa | Menú participa y rendición de cuentas |
| Oportunidades | Registro de proveedores, banco de hojas de vida, 29 convocatorias y 3 invitaciones abiertas con filtro por año |
| Institucional | Contacto, políticas, declaración de accesibilidad, mapa del sitio, búsqueda y 404 |

## Animaciones y funciones nuevas

**Animaciones (referencia apple.com):**
- Red de partículas interactiva en el hero, con auroras de color de la marca.
- Titulares que aparecen palabra por palabra con desenfoque.
- Orbe con el "+" del logo y los servicios girando a su alrededor.
- Frase que se ilumina palabra por palabra a medida que se hace scroll.
- Tarjeta que se expande a pantalla completa con el scroll ("zoom").
- Narrativa de servicios con panel visual fijo que cambia según la sección.
- Contadores animados.
- Carrusel horizontal con arrastre y barra de progreso.
- Marquesina infinita de clientes.
- Tarjetas con inclinación 3D y brillo que sigue el cursor.
- Botones magnéticos.
- Transiciones entre páginas (View Transitions API).
- Encabezado de vidrio que se oculta al bajar y reaparece al subir.
- Barra de progreso de lectura.

**Dos versiones del prototipo:**

| Versión | Qué incluye |
|---|---|
| **Clásica** | Todas las animaciones CSS y 2D anteriores |
| **3D corporativa** | Lo mismo, más las escenas Three.js de `assets/js/tres.js` (Three.js r170 incluido en `assets/js/vendor/`, licencia MIT) |

La versión 3D sigue la línea gráfica de valormas.gov.co:
- Verdes institucionales, lima del "+", azul marino y blanco.
- Objetos sólidos y mates con iluminación de estudio, como un render de producto.
- Sin brillos neón ni mezcla aditiva.

Escenas de la versión 3D:
- **Hero de inicio:** el "+" de la marca en 3D, con anillos institucionales y medallones de los servicios en órbita.
- **Servicios:** un objeto 3D por servicio sobre un pedestal blanco, que cambia al hacer scroll: pila de monedas (recaudo), globo de datos (automatización), gráfico de barras (proyectos), servidores (consultoría), candado (seguridad) y panel solar con sol (energía).
- **Cifras y pie de página:** malla de puntos verde que ondula suavemente y reacciona al cursor.
- **Clientes:** carrusel 3D en anillo con los logos; se puede arrastrar.
- **Encabezados internos:** signos "+" de la marca flotando.

**Rendimiento y accesibilidad del 3D:**
- Las escenas solo se dibujan cuando están en pantalla y se detienen si la pestaña está oculta o el menú móvil abierto.
- En celulares y equipos modestos se reduce la cantidad de puntos; en el celular el hero muestra la versión 2D.
- El botón de pausa (en cada encabezado) detiene todas las animaciones de fondo en todo el sitio y la preferencia se recuerda.
- Con "reducir movimiento" las escenas quedan quietas.
- Sin WebGL, o al abrir el sitio como archivo local, se usan las animaciones CSS y 2D.

**Funciones nuevas:**
- **Búsqueda global** con `Ctrl + K` o `/`: páginas, servicios, casos, 1.867 documentos de transparencia y procesos de contratación, con filtros y navegación por teclado.
- **Panel de accesibilidad**: tamaño de texto, tema claro/oscuro, alto contraste, detener animaciones, subrayar enlaces y fuente de lectura fácil. Las preferencias se recuerdan.
- **Modo oscuro** automático según el sistema, o manual.
- Filtro en vivo dentro de cada categoría de transparencia.
- Enlace copiable a cada sección, útil para auditorías ITA.
- Asistente de PQRSD por pasos, formularios con validación accesible, carga de archivos por arrastre, botón compartir y aviso de cookies.

## Cumplimiento normativo

| Norma | Cómo se atiende en el prototipo |
|---|---|
| **Res. MinTIC 1519/2020 – Anexo 1 (accesibilidad, WCAG 2.1 AA)** | Enlace "Saltar al contenido", estructura de títulos y regiones, foco visible, navegación completa por teclado, textos alternativos, zoom permitido, contraste AA, formularios con etiquetas y errores descriptivos, tablas con encabezados, `lang="es-CO"` y pausa para toda animación automática |
| **Res. 1519 – Anexo 2 (publicación)** | Menú "Transparencia y acceso a la información pública" con las 13 categorías y su numeración; "Atención y servicios a la ciudadanía" y "Participa" en el encabezado; pie de página institucional completo; mapa del sitio y buscador |
| **Res. 1519 – Anexo 3 (seguridad)** | Sección 13 de transparencia; políticas de seguridad y de datos enlazadas |
| **Res. 1519 – Anexo 4 (datos abiertos)** | Categoría 7 con instrumentos de gestión de la información y enlaces a datos.gov.co |
| **Res. MinTIC 2893/2020 (GOV.CO)** | Barra superior GOV.CO, pie con logos CO y GOV.CO, tipografías del kit (Montserrat y Work Sans) |
| **ITA (Procuraduría)** | Cada categoría y subsección tiene URL propia (`transparencia/<categoria>.html#s-1-2`), lo que facilita diligenciar la matriz; cada documento muestra su fecha de publicación |
| **FURAG / MIPG (Gobierno Digital y Transparencia)** | PQRSD en línea, rendición de cuentas, datos abiertos, accesibilidad e información actualizada |
| **Ley 1581/2012** | Autorización de tratamiento de datos en todos los formularios y aviso de cookies con consentimiento |

**Validación automática:** se ejecutó axe-core (WCAG 2.0/2.1/2.2 A y AA y buenas prácticas) sobre las 64 páginas en tema claro y sobre una muestra en tema oscuro: **0 violaciones**. También se ejecutaron 18 pruebas de interacción (búsqueda, menús, panel de accesibilidad, filtros, PQRSD, validación, teclado, movimiento reducido): todas pasan y no hay errores de JavaScript.
La validación automática no reemplaza la prueba manual con lectores de pantalla (NVDA, VoiceOver) ni la certificación de accesibilidad.

## Contenido pendiente o a corregir (detectado en el sitio actual)

Estos puntos se marcan en el prototipo con la etiqueta amarilla **"Pendiente"**:

- **Casos con texto de relleno ("Lorem ipsum")**: Licenciamiento, Migración IPv6 y Mantenimiento CCTV (ficha corta).
- **Casos con contenido copiado de otro caso**: Videovigilancia ciudadana (repite Contact Center) y Tecnologías para la seguridad (repite Infraestructura vial).
- **Casos sin contenido**: Recaudo de la tasa de seguridad.
- **Energía por Antioquia**: la cifra "Total de 1.772.752.119" no indica unidad.
- **Servicios**: el sitio actual solo lista capacidades; falta una descripción de cada servicio.
- **Dirección inconsistente**: el sitio publica tres direcciones (Calle 41 N.° 52–28; Calle 42 N.° 52–27; Carrera 53A N.° 42–161, Torre B, piso 6). El prototipo usa la del pie de página actual.
- **Código postal**: no está publicado y es obligatorio en el pie de página GOV.CO.
- **Teléfono**: se escribe con el plan de marcación vigente, +57 (604) 444 3747. El sitio actual muestra +57 (4).
- **Proveedores**: el formulario actual pide "adjuntar la siguiente documentación" sin decir cuál.
- **Política de cookies**: no existe, aunque el sitio usa Google Analytics.
- **Numeración**: en Datos abiertos, "Costos de reproducción" aparece como 7.1.3, repetido; debería ser 7.3.
- **Pida una cita** (11.2): no existe en el sitio actual; el prototipo propone un formulario.
- **Logo**: se vectorizó a partir del PNG publicado. Para producción se debe usar el SVG oficial del manual de marca.

Además, en los textos se corrigieron errores de ortografía evidentes ("Contac Center", "Transformáremos", "dispoción", entre otros). Los títulos en mayúscula sostenida se pasaron a tipo oración para facilitar la lectura.

## Limitaciones del prototipo

- **Formularios simulados.** PQRSD, contacto, proveedores, hojas de vida, citas y encuesta no envían datos; muestran un mensaje de simulación. En producción se deben conectar al sistema de PQRSD y agregar reCAPTCHA.
- **Documentos en el servidor actual.** Los PDF y XLSX de transparencia apuntan al almacenamiento actual de Valor+ (S3).
- **Fuentes externas.** Las tipografías se cargan desde Google Fonts.
- **Fuera de buscadores.** Las páginas llevan `noindex` para que el prototipo no se indexe.

## Estructura

```
rediseno-sitio/
├── index.html, nosotros.html, … (páginas generadas)
├── servicios/ casos/ opinion/ transparencia/
├── assets/
│   ├── css/estilos.css        tokens de marca, temas, componentes y animaciones
│   ├── js/app.js              interacción y animación (sin dependencias)
│   ├── js/tres.js             escenas 3D corporativas (Three.js)
│   ├── js/vendor/             Three.js r170 (MIT)
│   ├── js/indice-busqueda.js  índice de búsqueda (generado)
│   └── img/                   logos, servicios, casos, equipo y clientes (WebP optimizado)
└── _fuente/                   generador del sitio
    ├── construir.py           páginas
    ├── empaquetar.py          ZIP de las versiones clásica y 3D
    ├── plantilla.py           encabezado, menú, pie y diálogos
    ├── contenido.py           lectura del contenido extraído
    ├── componentes.py         íconos, textos y datos de la entidad
    └── contenido/             contenido extraído de valormas.gov.co
```

Para regenerar las páginas después de editar el contenido o las plantillas:

```bash
python3 _fuente/construir.py
```

Para generar los ZIP de las dos versiones (quedan en `dist/`, listos para arrastrar a Netlify):

```bash
python3 _fuente/empaquetar.py
```

Solo requiere Python 3.8 o superior, sin dependencias.
