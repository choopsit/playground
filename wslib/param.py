#!/usr/bin/nv python3

import re
import socket
import pathlib
import mylib

__description__ = "Workstation settings management module"
__author__ = "Choops <choopsbd@gmail.com>"

c0 = "\33[0m"
ce = "\33[31m"
cok = "\33[32m"
cw = "\33[33m"
ci = "\33[36m"

error = f"{ce}E{c0}:"
done = f"{cok}OK{c0}:"
warning = f"{cw}W{c0}:"


def choose_additions():
    """Choose specific applications to install"""

    inst = {}

    if socket.gethostname() == "mrchat":
        inst["nfssrv"] = "yes"
        inst["docker"] = "no"
        inst["vbox"] = "yes"
        inst["tsmd"] = "yes"
        inst["mediatools"] = "yes"
        inst["kodi"] = "yes"
        inst["steam"] = "yes"
    else:
        inst["nfssrv"] = mylib.com.yesno("Install NFS server", "n")
        inst["docker"] = mylib.com.yesno("Install docker", "n")
        if not mylib.com.is_vm():
            inst["vbox"] = mylib.com.yesno("Install VirtualBox", "n")
        else:
            inst["vbox"] = "no"
        inst["tsmd"] = mylib.com.yesno("Install Transmission-daemon", "n")
        inst["mediatools"] = mylib.com.yesno("Install multimedia tools", "n")
        inst["kodi"] = mylib.com.yesno("Install Kodi MediaCenter", "n")
        inst["steam"] = mylib.com.yesno("Install Steam", "n")

    return inst


def choose_de():
    """Choose specific desktop environment or window manager to install"""

    okde = ["xfce", "awesomewm"]

    print(f"{ci}Available Desktop Environments or Window Managers{c0}:")
    for i in range(len(okde)):
        print(f"  {i}) {ci}{okde[i]}{c0}")
    dechoicestr = input("Your choice ? ")

    try:
        dechoice = int(dechoicestr)
    except ValueError:
        print(f"{ce}E{c0}: Invalid choice '{dechoicestr}'")
        de = choose_de()

    if dechoice in range(len(okde)):
        de = okde[dechoice]
    else:
        print(f"{ce}E{c0}: Out of range choice '{dechoice}'")
        de = choose_de()

    return de


def deusers_add(de, userlist):
    """Determine users to apply Desktop Environment configuration"""

    deusers = []
    for user in userlist:
        home = f"/home/{user}"
        grp = pathlib.Path(home).group()

        wmcfg = mylib.com.yesno(f"Deploy '{de}' config for '{user}'", "y")
        if not re.match('^(n|no)$', wmcfg.lower()):
            deusers.append((home, user, grp))

    return deusers
