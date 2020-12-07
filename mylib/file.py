#!/usr/bin/env python3

import os
import shutil

__description__ = "File management module"
__author__ = "Choops <choopsbd@gmail.com>"

c0 = "\33[0m"
ce = "\33[31m"
cok = "\33[32m"
cw = "\33[33m"
ci = "\33[36m"

error = f"{ce}E{c0}:"
done = f"{cok}OK{c0}:"
warning = f"{cw}W{c0}:"


def overwrite(src, tgt):
    """Overwrite file or folder"""

    if os.path.isdir(src):
        if os.path.isdir(tgt):
            shutil.rmtree(tgt)
        shutil.copytree(src, tgt, symlinks=True)
    else:
        if os.path.exists(tgt):
            os.remove(tgt)
        shutil.copy(src, tgt, follow_symlinks=False)


def rcopy(src, tgt):
    """Recursive copy"""

    for root, dirs, files in os.walk(src):
        for item in files:
            src_path = os.path.join(root, item)
            dst_path = os.path.join(tgt, src_path.replace(f"{src}/", ""))
            if os.path.exists(dst_path):
                if os.stat(src_path).st_mtime > os.stat(dst_path).st_mtime:
                    shutil.copy(src_path, dst_path)
            else:
                shutil.copy(src_path, dst_path)
        for item in dirs:
            src_path = os.path.join(root, item)
            dst_path = os.path.join(tgt, src_path.replace(f"{src}/", ""))
            if not os.path.exists(dst_path):
                os.mkdir(dst_path)


def rchown(path, newowner=None, newgroup=None):
    """Recursive chown"""

    shutil.chown(path, newowner, newgroup)
    for dirpath, dirs, files in os.walk(path):
        for mydir in dirs:
            shutil.chown(os.path.join(dirpath, mydir), newowner, newgroup)
        for myfile in files:
            shutil.chown(os.path.join(dirpath, myfile), newowner, newgroup)


def rchmod(path, perm):
    """Recursive chmod"""

    os.chmod(path, perm)
    for root, dirs, files in os.walk(path):
        for mydir in dirs:
            os.chmod(os.path.join(root, mydir), perm)
        for myfile in files:
            os.chmod(os.path.join(root, myfile), perm)
