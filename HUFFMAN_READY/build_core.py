"""Run with Python from any directory. Requires a GCC toolchain."""
from pathlib import Path
import os
import shutil
import subprocess
import sys
root = Path(__file__).resolve().parent
compiler = shutil.which('gcc')
if not compiler and os.name == 'nt':
    for p in (r'C:\msys64\ucrt64\bin\gcc.exe', r'C:\msys64\mingw64\bin\gcc.exe'):
        if Path(p).is_file():
            compiler = p
            break
if not compiler:
    sys.exit('Khong tim thay GCC. Cai GCC/MinGW-w64, sau do chay lai. Xem README.md.')
exe = root / 'core' / ('huffman_core.exe' if os.name == 'nt' else 'huffman_core')
command = [compiler, '-std=c11', '-O2', '-Wall', '-Wextra', '-Wpedantic']
if os.name == 'nt':
    command += ['-static']
command += [str(root/'core/main.c'), str(root/'core/huffman.c'), '-o', str(exe)]
subprocess.run(command, check=True)
print('Built:', exe)
