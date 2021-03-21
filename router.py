#!/usr/bin/env python3

import os
import sys
import re
import mylib
import srvlib

__description__ = "Install configured Desktop Environment on Debian"
__author__ = "Choops <choopsbd@gmail.com>"

c0 = "\33[0m"
ce = "\33[31m"
cok = "\33[32m"
cw = "\33[33m"
ci = "\33[36m"

error = f"{ce}E{c0}:"
done = f"{cok}OK{c0}:"
warning = f"{cw}W{c0}:"


def usage():
    myscript = f"{os.path.basename(sys.argv[0])}"
    print(f"{ci}{__description__}\nUsage{c0}:")
    print(f"  './{myscript} [OPTION]' as root or using 'sudo'")
    print(f"{ci}Options{c0}:")
    print(f"  -h,--help: Print this help")
    print()


def choose_server():
    servers = ["pxe", "dchp", "saltmaster"]
    
    print("Available servers:")
    for i in range(len(servers)):
        print(f"  {i}) {myservers[i]}")
    srv = input("Your choice ? ")
    
    try:
        srvidx = int(srv)
    except ValueError:
        print(f"{error} Invalid choice '{srv}'")
        exit(1)
    
    serverfct = ""
    if srvidx in range(len(servers)):
        serverfct = servers[srvidx]
    else:
        print(f"{error} Out of range choice '{srvidx}'")
        serverfct = choose_server()

    return serverfct


if __name__ == "__main__":
    if len(sys.argv) > 1:
        if re.match('^-(h|-help)$', sys.argv[1]):
            usage()
            exit(0)
        else:
            print(f"{error} Bad argument")
            usage()
            exit(1)

    distro = mylib.com.get_distro()
    if distro != "debian":
        print(f"{error} OS is not Debian")
        exit(1)

    if os.getuid() != 0:
        print(f"{error} Need higher privileges")
        exit(1)

    scriptfolder = os.path.dirname(os.path.realpath(__file__))

    mycodename = mylib.com.get_codename()

    olddebian = ["stretch", "jessie", "wheezy", "squeeze", "lenny"]
    if mycodename in olddebian:
        print(f"{error} '{codename}' is a too old Debian version")
        exit(1)

    myhostname, mydomain = mylib.com.set_hostname()


    myserver = choose_server()

    srvlib.installsrv(myserver)

    print(f"{done} '{myserver}' server installed")
    mylib.com.reboot()
