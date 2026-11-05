# Prototipo v4.0 · Rediseño valormas.gov.co

Une el **contenido completo de la versión 1** (64 páginas, transparencia con 2.344 documentos, PQRSD, atención al
ciudadano, casos, opinión) con el **diseño de la versión 3** (paleta del manual de marca vigente, mapa 3D de Antioquia,
antena satelital, red de cámaras, gráficas interactivas), más una capa nueva más viva y tecnológica.

## Cómo verlo

```bash
cd prototipo-v4
python3 -m http.server 8000
# abrir http://localhost:8000
```

Las escenas 3D usan módulos de JavaScript: **necesitan servidor** (el de arriba, Netlify o cualquier hosting).
Si se abre con doble clic (`file://`) el sitio funciona, pero se muestra un aviso en lugar del 3D.

## Novedades de la v4

| Bloque | Qué hace |
|---|---|
| Hero | Mapa 3D de Antioquia con capas (subregiones, conectividad, seguridad), buscador de municipio y cinta de señales en vivo |
| Cifras | Tarjetas interactivas (pestañas accesibles): cada cifra abre su gráfica, barras de meta o municipios por subregión |
| Proyectos | Las 2 experiencias inmersivas (conectividad satelital y red de seguridad) + carrusel con filtro de los 25 casos, cada uno con su escena 3D |
| Casos de éxito | Cada ficha tiene una **escena 3D propia** en el encabezado (recaudo, territorio, archivo digital, alumbrado, centro de datos, cámaras, vías, satélite, energía) |
| Nosotros | Misión, visión y acceso a "conoce más sobre nosotros" |
| Opinión | Columna de Félix Alfazar con **explorador del recaudo** del impuesto vehicular (control deslizante, reproducción año a año) |
| Equipo | Órbita animada con el equipo |
| Transparencia y PQRSD | Buscador de documentos, 13 categorías, radicación y consulta de PQRSD, rendición de cuentas |
| Oportunidades | Registro de proveedores, trabaja con nosotros, convocatorias públicas e invitaciones abiertas |
| Clientes y redes | Carrusel 3D de clientes y tarjetas de redes sociales |
| Pie de página | Verde bosque de la marca, con ola de partículas |

## Cumplimiento

- **MinTIC / GOV.CO** (Res. 1519 de 2020 y 2893 de 2020): barra GOV.CO, pie con datos de contacto, canales y enlaces obligatorios.
- **Ley 1712 de 2014 / ITA**: menú de transparencia con las 13 categorías del Anexo 2.
- **WCAG 2.2 AA**: auditoría axe-core sin violaciones (modo normal y alto contraste); botón global de pausa,
  movimiento reducido, alto contraste, tamaño de texto; tablas de datos como alternativa a cada gráfica y escena.
- **Ley 1581 de 2012**: aviso de cookies y política de datos.

## Regenerar

```bash
python3 _fuente/construir.py     # genera las páginas
python3 _fuente/empaquetar.py    # crea dist/valormas-prototipo-v4.zip
```

`_fuente/v4.py` reutiliza el generador de la versión 3 (`../prototipo-v1/_construir.py`) para los mapas,
gráficas y experiencias inmersivas.
