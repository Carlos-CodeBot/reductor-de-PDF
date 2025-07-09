#!/usr/bin/env python3
"""
compress_pdf.py
---------------
Comprime un PDF hasta que pese ≤50 MB usando Ghostscript.
Uso:
    python compress_pdf.py "ruta/al/archivo.pdf"
Opciones:
    -o, --output  Nombre del PDF de salida (por defecto _compressed.pdf).
    -t, --target  Tamaño máximo en MB (por defecto 50).
"""

import argparse
import os
import shutil
import subprocess
import sys
from pathlib import Path

# RUTA a Ghostscript (déjala vacía si está en el PATH)
GS_PATH = r"gswin64c"  # o r"C:\Program Files\gs\gs10.03.0\bin\gswin64c.exe"

PDF_SETTINGS = [
    "/printer",  # compresión ligera
    "/ebook",    # compresión media (ideal para pantalla)
    "/screen",   # compresión fuerte
]

def mb(size_bytes: int) -> float:
    return size_bytes / (1024 ** 2)

def run_gs(input_pdf: Path, output_pdf: Path, preset: str):
    cmd = [
        GS_PATH,
        "-sDEVICE=pdfwrite",
        "-dCompatibilityLevel=1.4",
        f"-dPDFSETTINGS={preset}",
        "-dNOPAUSE", "-dQUIET", "-dBATCH",
        f"-sOutputFile={output_pdf}",
        str(input_pdf),
    ]
    print(f" 🛠️  Ejecutando Ghostscript con {preset} …")
    subprocess.run(cmd, check=True)

def main():
    parser = argparse.ArgumentParser(description="Comprimir PDF con Ghostscript")
    parser.add_argument("input_pdf", type=Path, help="PDF de entrada")
    parser.add_argument("-o", "--output", type=Path,
                        help="PDF de salida (predeterminado *_compressed.pdf)")
    parser.add_argument("-t", "--target", type=float, default=50,
                        help="Tamaño objetivo en MB (default 50)")
    args = parser.parse_args()

    src = args.input_pdf.resolve()
    if not src.is_file():
        sys.exit(f"❌ El archivo {src} no existe")

    dst = (args.output or src.with_name(src.stem + "_compressed.pdf")).resolve()
    tmp = src.with_suffix(".tmp.pdf")

    print(f"📄 Archivo original: {src.name} — {mb(src.stat().st_size):.1f} MB")

    for preset in PDF_SETTINGS:
        run_gs(src, tmp, preset)
        size = mb(tmp.stat().st_size)
        print(f"   ➜ Tamaño tras {preset}: {size:.1f} MB")

        if size <= args.target:
            shutil.move(tmp, dst)
            print(f"✅ ¡Listo! {dst.name} pesa {size:.1f} MB (≤ {args.target} MB)")
            break
    else:
        # Si ninguno cumple, deja el último y avisa
        shutil.move(tmp, dst)
        print(f"⚠️  El mejor resultado ({dst.name}) aún es {size:.1f} MB "
              f"(> {args.target} MB). Prueba ajustes más agresivos.")

if __name__ == "__main__":
    main()
