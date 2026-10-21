#!/usr/bin/env python3
"""Genera los ZIP listos para subir a Netlify (o a cualquier hosting estático).

Uso:  python3 _fuente/empaquetar.py [carpeta_salida]

Crea dos versiones a partir de las páginas ya generadas por construir.py:
  - valormas-prototipo-clasica.zip  animaciones CSS/2D, sin Three.js
  - valormas-prototipo-3d.zip       con las escenas 3D corporativas (assets/js/tres.js)
"""
import re
import sys
import zipfile
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
SALIDA = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else BASE / 'dist'
EXCLUIR = ('_fuente/', 'dist/', '.gitignore', 'README.md')
ARCHIVOS_3D = ('assets/js/tres.js', 'assets/js/vendor/')
RE_3D = re.compile(r'^<link rel="modulepreload"[^>]*three[^>]*>\n|^<script type="module" src="[^"]*tres\.js"></script>\n', re.M)


def empaquetar(nombre, con_3d):
    destino = SALIDA / nombre
    n = 0
    with zipfile.ZipFile(destino, 'w', zipfile.ZIP_DEFLATED) as z:
        for f in sorted(BASE.rglob('*')):
            rel = f.relative_to(BASE).as_posix()
            if f.is_dir() or rel.startswith(EXCLUIR) or '__pycache__' in rel:
                continue
            if not con_3d and rel.startswith(ARCHIVOS_3D):
                continue
            if f.suffix == '.html' and not con_3d:
                z.writestr(rel, RE_3D.sub('', f.read_text(encoding='utf-8')))
            else:
                z.write(f, rel)
            n += 1
    print(f'{destino}  ({n} archivos, {destino.stat().st_size / 1e6:.1f} MB)')


if __name__ == '__main__':
    SALIDA.mkdir(parents=True, exist_ok=True)
    empaquetar('valormas-prototipo-clasica.zip', con_3d=False)
    empaquetar('valormas-prototipo-3d.zip', con_3d=True)
