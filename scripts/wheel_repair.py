#!/usr/bin/env python

# Modified from https://github.com/vinayak-mehta/pdftopng/blob/main/scripts/wheel_repair.py

import os
import shutil
import hashlib
import zipfile
import argparse
from tempfile import TemporaryDirectory
from collections import defaultdict

import pefile
from machomachomangler.pe import redll


def hash_filename(filepath, blocksize=65536):
    hasher = hashlib.sha256()

    with open(filepath, "rb") as afile:
        buf = afile.read(blocksize)
        while len(buf) > 0:
            hasher.update(buf)
            buf = afile.read(blocksize)

    root, ext = os.path.splitext(filepath)
    return f"{os.path.basename(root)}-{hasher.hexdigest()[:8]}{ext}"


def find_dll_dependencies(dll_filepath, vcpkg_bin_dir):
    pe = pefile.PE(dll_filepath)
    if not hasattr(pe, 'DIRECTORY_ENTRY_IMPORT'):
        pe.close()
        return

    for entry in pe.DIRECTORY_ENTRY_IMPORT:
        entry_name = entry.dll.decode("utf-8")
        if entry_name in os.listdir(vcpkg_bin_dir):
            dll_dependencies[dll_filepath].add(entry_name)
            _dll_filepath = os.path.join(vcpkg_bin_dir, entry_name)
            find_dll_dependencies(_dll_filepath, vcpkg_bin_dir)
    pe.close()


def mangle_filename(old_filename, new_filename, mapping):
    with open(old_filename, "rb") as f:
        buf = f.read()

    new_buf = redll(buf, mapping)

    with open(new_filename, "wb") as f:
        f.write(new_buf)


def import_dll_dependencies(tmp_pyd_path, dll_dir, old_wheel_dir, new_wheel_dir): 
    find_dll_dependencies(tmp_pyd_path, args.DLL_DIR)

    for dll, dependencies in dll_dependencies.items():
        mapping = {}

        for dep in dependencies:
            # Skip Windows APIs
            if 'api-ms-win' in dep:
                mapping[dep.encode("ascii")] = dep.encode("ascii")
                continue
            hashed_name = hash_filename(os.path.join(args.DLL_DIR, dep))  # already basename
            mapping[dep.encode("ascii")] = hashed_name.encode("ascii")
            shutil.copy(
                os.path.join(args.DLL_DIR, dep),
                os.path.join(new_wheel_dir, dll_dir, hashed_name),
            )

        if dll.endswith(".pyd"):
            old_name = dll
            new_name = os.path.join(new_wheel_dir, os.path.relpath(dll, old_wheel_dir))
        else:
            old_name = os.path.join(args.DLL_DIR, dll)
            hashed_name = hash_filename(os.path.join(args.DLL_DIR, dll))  # already basename
            new_name = os.path.join(new_wheel_dir, dll_dir, hashed_name)

        mangle_filename(old_name, new_name, mapping)


parser = argparse.ArgumentParser(
    description="Vendor in external shared library dependencies of a wheel."
)

parser.add_argument("WHEEL_FILE", type=str, help="Path to wheel file")
parser.add_argument(
    "-d", "--dll-dir", dest="DLL_DIR", type=str, help="Directory to find the DLLs"
)
parser.add_argument(
    "-w",
    "--wheel-dir",
    dest="WHEEL_DIR",
    type=str,
    help=('Directory to store delocated wheels (default: "wheelhouse/")'),
    default="wheelhouse/",
)

args = parser.parse_args()

wheel_name = os.path.basename(args.WHEEL_FILE)
package_name = wheel_name.split("-")[0]
repaired_wheel = os.path.join(args.WHEEL_DIR, wheel_name)
os.makedirs(args.WHEEL_DIR, exist_ok=True)

with TemporaryDirectory() as temp_dir:
    old_wheel_dir = os.path.join(temp_dir, 'old')
    new_wheel_dir = os.path.join(temp_dir, 'new')

    with zipfile.ZipFile(args.WHEEL_FILE, "r") as wheel:
        wheel.extractall(old_wheel_dir)
        wheel.extractall(new_wheel_dir)
        pyd_path_list = list(filter(lambda x: x.endswith(".pyd"), wheel.namelist()))

    for pyd_path in pyd_path_list:
        dll_dir = os.path.split(pyd_path)[0]
        tmp_pyd_path = os.path.join(old_wheel_dir, pyd_path)
        dll_dependencies = defaultdict(set)
        import_dll_dependencies(tmp_pyd_path, dll_dir, old_wheel_dir, new_wheel_dir)

    with zipfile.ZipFile(repaired_wheel, "w", zipfile.ZIP_DEFLATED) as new_wheel:
        for root, dirs, files in os.walk(new_wheel_dir):
            for file in files:
                new_wheel.write(
                    os.path.join(root, file), os.path.join(os.path.relpath(root, new_wheel_dir), file)
                )
print('Done! Repaired wheel saved to {}'.format(repaired_wheel))
