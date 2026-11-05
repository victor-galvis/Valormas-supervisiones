#!/usr/bin/env python3
"""Genera el ZIP listo para subir a Netlify (o a cualquier hosting estático).

Uso:  python3 _fuente/empaquetar.py [carpeta_salida]
Crea valormas-prototipo-v4.zip con las páginas ya generadas por construir.py.
"""
import sys
import zipfile
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
SALIDA = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else BASE / 'dist'
EXCLUIR = ('_fuente/', 'dist/', '.gitignore', 'README.md')

if __name__ == '__main__':
    SALIDA.mkdir(parents=True, exist_ok=True)
    destino = SALIDA / 'valormas-prototipo-v4.zip'
    n = 0
    with zipfile.ZipFile(destino, 'w', zipfile.ZIP_DEFLATED) as z:
        for f in sorted(BASE.rglob('*')):
            rel = f.relative_to(BASE).as_posix()
            if f.is_dir() or rel.startswith(EXCLUIR) or '__pycache__' in rel:
                continue
            z.write(f, rel)
            n += 1
    print(f'{destino}  ({n} archivos, {destino.stat().st_size / 1e6:.1f} MB)')
