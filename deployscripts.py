#!/usr/bin/env python3

import sys
import os
import re
import mylib

myrepo = "choopsit/playground"
__description__ = f"Link scripts from '{myrepo}' repo to '/usr/local/bin'"
__author__ = "Choops <choopsbd@gmail.com>"


def usage():
    myscript = f"{os.path.basename(__file__)}"
    print(f"{ci}{__description__}\nUsage{c0}:")
    print(f"  './{myscript} [OPTION]' as root or using 'sudo'")
    print(f"{ci}Options{c0}:")
    print(f"  -h,--help: Print this help")
    print()


def create_links():
    target = "/usr/local/bin"
    ignoredlist = []

    print(f"{ci}Linking scripts...{c0}")
    for script in os.listdir(f"{scriptpath}/bin"):
        mysrc = f"{scriptpath}/bin/{script}"
        mylink = f"{target}/{script}"

        if os.path.islink(mylink):
            os.remove(mylink)

        if os.path.isfile(mylink):
            force = "n"
            print(f"{warning} '{mylink}' is a file.", end=" ")
            print("It could be an important script")
            force = input(f"Overwrite it with link to '{mysrc}' [y/N] ? ")
            if re.match('^(y|yes)$', force.lower()):
                os.remove(mylink)
            else:
                ignoredlist.append(script)

        if os.path.isdir(mylink):
            print(f"{warning} '{mylink}' is a folder.", end=" ")
            print("It will not be overwritten")
            ignoredlist.append(script)

        if not mylib.pkg.is_installed("virtualbox"):
            if script == "vbox":
                continue

        if not os.path.exists(mylink):
            os.chdir(target)
            os.symlink(mysrc, mylink)

    return ignoredlist


c0 = "\33[0m"
ce = "\33[31m"
cok = "\33[32m"
cw = "\33[33m"
ci = "\33[36m"

error = f"{ce}E{c0}:"
done = f"{cok}OK{c0}:"
warning = f"{cw}W{c0}:"

if __name__ == "__main__":
    scriptpath = os.path.dirname(os.path.abspath(__file__))

    if len(sys.argv) > 1:
        if re.match('^-(h|-help)$', sys.argv[1]):
            usage()
            exit(0)
        else:
            print(f"{error} Too many arguments")
            exit(1)

    if os.getuid() != 0:
        print(f"{error} Need higher privileges")
        exit(1)

    ignored = create_links()

    ignoredscripts = ""
    if len(ignored) > 0:
        ignoredscripts = f" [{cw}Ignored scripts{c0}: {', '.join(ignored)}]"

    print(f"{done} Links created{ignoredscripts}")
