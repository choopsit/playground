#!/usr/bin/env python3

import os
import sys
import re
import mylib
import srvlib

__description__ = "PXE server functions module"
__author__ = "Choops <choopsbd@gmail.com>"

c0 = "\33[0m"
ce = "\33[31m"
cok = "\33[32m"
cw = "\33[33m"
ci = "\33[36m"

error = f"{ce}E{c0}:"
done = f"{cok}OK{c0}:"
warning = f"{cw}W{c0}:"


def install():
    print(f"{ci}Installing 'pxe' server...")
    mylib.pkg.upgrade()


def config():
    print(f"{ci}Configuring 'pxe' server...")
