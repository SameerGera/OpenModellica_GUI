#!/usr/bin/env python3
"""Copy the required OpenModelica runtime DLLs into resources/model/runtime/.

Run this script once after installing OpenModelica to populate the
packaged runtime directory.  The list of DLLs was determined by
recursive PE import analysis of TwoConnectedTanks.exe.

Usage
-----
    python scripts/copy_runtime.py

Adjust ``OM_BIN`` below if your OpenModelica installation path differs.
"""

from __future__ import annotations

import os
import shutil
import sys

#: OpenModelica ``bin/`` directory containing the runtime DLLs.
OM_BIN = r"C:\Program Files\OpenModelica1.27.0-64bit\bin"

#: Destination directory (relative to this script's parent).
RUNTIME_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "resources",
    "model",
    "runtime",
)

#: The 20 DLLs required by TwoConnectedTanks.exe (recursively resolved).
REQUIRED_DLLS: list[str] = [
    "libSimulationRuntimeC.dll",
    "libgcc_s_seh-1.dll",
    "libgfortran-5.dll",
    "libgomp-1.dll",
    "libiconv-2.dll",
    "libintl-8.dll",
    "libomcgc-1.dll",
    "libopenblas.dll",
    "libquadmath-0.dll",
    "libstdc++-6.dll",
    "libsundials_cvode.dll",
    "libsundials_idas.dll",
    "libsundials_kinsol.dll",
    "libsundials_sunlinsolklu.dll",
    "libsundials_sunlinsollapackdense.dll",
    "libsundials_sunmatrixdense.dll",
    "libsundials_sunmatrixsparse.dll",
    "libsystre-0.dll",
    "libtre-5.dll",
    "libwinpthread-1.dll",
]


def main() -> int:
    """Copy DLLs and report results."""
    if not os.path.isdir(OM_BIN):
        print(f"ERROR: OpenModelica bin not found at {OM_BIN}")
        print("       Edit OM_BIN in this script to match your installation.")
        return 1

    os.makedirs(RUNTIME_DIR, exist_ok=True)

    copied = 0
    total_bytes = 0
    for dll in REQUIRED_DLLS:
        src = os.path.join(OM_BIN, dll)
        dst = os.path.join(RUNTIME_DIR, dll)
        if not os.path.isfile(src):
            print(f"  MISSING: {dll}")
            continue
        shutil.copy2(src, dst)
        size = os.path.getsize(dst)
        total_bytes += size
        print(f"  Copied: {dll:50s} ({size / 1024:.1f} KB)")
        copied += 1

    print(f"\nDone: {copied}/{len(REQUIRED_DLLS)} DLLs copied "
          f"({total_bytes / 1024 / 1024:.1f} MB total)")
    print(f"Destination: {RUNTIME_DIR}")
    return 0 if copied == len(REQUIRED_DLLS) else 1


if __name__ == "__main__":
    sys.exit(main())
