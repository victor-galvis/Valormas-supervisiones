# Valor+ · Prototipo v1.0 (propuesta desde cero)

Prototipo HTML interactivo con un diseño, contenido e ilustraciones creados desde cero. Solo toma del manual de marca vigente la paleta y el logo:

| Color | Hex | Uso |
|---|---|---|
| Marino | `#1C2D4C` | Fondos inmersivos, textos y botones |
| Lima | `#B5C73A` | Acentos, botones principales, datos destacados (nunca como color de texto sobre blanco) |
| Verde bosque | `#194A2B` | Títulos y enlaces sobre fondos claros |
| Celeste | `#D8EFFB` | Fondos suaves y datos de seguridad |
| Blanco | `#FFFFFF` | Fondo base |

Los valores se tomaron de la pieza de referencia enviada. Conviene confirmarlos con el manual de marca oficial; todos están definidos como variables al inicio de `assets/css/app.css`.

## Cómo verlo

```bash
cd prototipo-v1
python3 -m http.server 8000
# abrir http://localhost:8000
```

Las escenas 3D necesitan servidor: este comando local, Netlify u otro hosting. Si el sitio se abre con doble clic o en un navegador sin WebGL, sigue funcionando: muestra un aviso en lugar del 3D y la información está en las gráficas y tablas.

Para publicarlo en Netlify, sube el ZIP o la carpeta completa.

## Qué incluye

| Página | Experiencia |
|---|---|
| **Inicio** | Mapa 3D de Antioquia con los 125 municipios en relieve. Se puede girar, acercar, pasar el cursor y elegir municipio. Tiene capas (subregiones, conectividad, seguridad), buscador de municipios con ficha y gráfica interactiva por subregión |
| **Conectividad satelital** | Recorrido 3D guiado por el scroll: valle rural → antena de órbita baja con 4 puntos de información → constelación de satélites y enlace → sede conectada con ondas Wi‑Fi. Incluye mapa 3D de sedes conectadas, avance hacia la meta, gráficas y el proceso de trabajo |
| **Red de seguridad** | Mapa 3D con 48 municipios, más de 900 cámaras y arcos de datos animados hacia los nodos subregionales y el nodo departamental. Visor 3D de cámaras (autodomo PTZ, lectura de placas, multisensor) con su campo de visión, sincronizado con una gráfica de dona. Incluye el flujo "de la cámara a la respuesta" |
| **Transparencia** | Las 13 categorías del ITA (Ley 1712 de 2014, Res. 1519 de 2020) |
| **Atención a la ciudadanía** | Canales, horarios y formulario de PQRSD con validación accesible (envío simulado) |
| **Participa**, **Accesibilidad**, **Política de datos**, **Mapa del sitio** | Páginas institucionales obligatorias |

Las ilustraciones son SVG y 3D generados en código, sin fotografías ni imágenes del sitio actual. El mapa usa los límites municipales oficiales (base DANE), simplificados.

## Datos

- Los **totales** salen de las fichas de proyecto de Valor+:
  - Conectividad: 870 sedes con servicio confirmado (784 satelitales y 86 por radioenlace), 1.228 por reactivar y meta departamental de 3.414.
  - Seguridad: 48 municipios, más de 900 cámaras y 217 cámaras nuevas (154 autodomos, 48 LPR y 15 multisensor).
- La **distribución por municipio es ilustrativa** y así se indica en el sitio. Antes de publicar se debe reemplazar con los datos reales en `assets/data/proyectos.js`. Las gráficas se recalculan con `python3 _construir.py`.

## Lineamientos

| Norma | En el prototipo |
|---|---|
| GOV.CO (Res. MinTIC 2893/2020) | Barra superior y pie con marca país y GOV.CO |
| Res. 1519/2020, Anexo 1 (WCAG 2.1 AA) | Enlace para saltar al contenido, navegación por teclado, foco visible y contraste AA. Panel de accesibilidad con tamaño de texto, alto contraste y opción para detener animaciones. Se respeta "reducir movimiento". Todo el 3D es complementario: su información también está en texto, gráficas y tablas. El buscador de municipios funciona con teclado y lector de pantalla |
| Res. 1519/2020, Anexo 2 / ITA | Menú de Transparencia con las 13 categorías; Atención a la ciudadanía y Participa en el encabezado; pie con datos de contacto, horarios, canales oficiales, notificaciones judiciales, políticas y mapa del sitio |
| FURAG / MIPG | PQRSD en línea, rendición de cuentas, datos abiertos y accesibilidad |
| Ley 1581/2012 | Autorización de datos en el formulario |

**Validación:** axe-core (WCAG 2.0, 2.1 y 2.2 A/AA y buenas prácticas) en las 9 páginas, en modo normal y en alto contraste: **0 violaciones**. También pasan 18 pruebas de interacción (teclado, buscador, capas, gráficas, puntos de información, pestañas, formulario, menú móvil) sin errores de JavaScript. La validación automática no reemplaza la prueba con lectores de pantalla.

## Referencias de diseño consultadas

- **Bogotá (bogota.gov.co):** premiado internacionalmente por un portal centrado en el ciudadano con información georreferenciada. De ahí sale la idea de "busca tu municipio" en el mapa.
- **Narrativas con mapas a pantalla completa (scrollytelling, como Esri Story Maps):** inspiran los recorridos 3D guiados por el scroll de las páginas de proyectos.
- **Visualizaciones interactivas de movilidad premiadas en Red Dot (por ejemplo, District Mobility de Washington D. C.):** inspiran combinar datos y gráficas para contar un proyecto.
- **Kit UI de GOV.CO (MinTIC):** barra superior y pie obligatorios. MinTIC anunció una renovación de la imagen de GOV.CO, pero no se pudo consultar desde el entorno de trabajo; hay que verificar la versión vigente de la barra y del pie antes de implementar.

## Pendientes antes de producción

- Confirmar los colores, el logo oficial en SVG (el del prototipo es una vectorización) y la tipografía del manual de marca.
- Reemplazar la distribución ilustrativa por los datos reales por municipio.
- Verificar con MinTIC la versión vigente de la barra y del pie GOV.CO.
- Migrar los documentos de Transparencia y conectar el formulario de PQRSD al sistema real.
- Validar con el área jurídica la mención de la marca Starlink en el texto.

## Estructura

```
prototipo-v1/
├── index.html, transparencia.html, atencion-ciudadania.html, participa.html, …
├── proyectos/conectividad-satelital.html, proyectos/seguridad-ciudadana.html
├── assets/css/app.css           sistema visual (paleta del manual de marca)
├── assets/js/base.js            accesibilidad, menú, gráficas SVG, formularios (sin servidor)
├── assets/js/mapa3d.js          mapa 3D de Antioquia (capas, selección, arcos de datos)
├── assets/js/antena3d.js        escena de la antena satelital
├── assets/js/camaras3d.js       visor de cámaras
├── assets/js/interaccion.js     buscador de municipios y arranque por página
├── assets/js/vendor/            Three.js r170 y OrbitControls (MIT)
├── assets/data/antioquia.js     límites municipales simplificados (base DANE)
├── assets/data/proyectos.js     datos de los proyectos (ver nota)
└── _construir.py                genera las páginas (Python 3, sin dependencias)
```
