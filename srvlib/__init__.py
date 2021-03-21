#!/usr/bin/env python3

from . import pxe

__description__ = "Server management module"
__author__ = "Choops <choopsbd@gmail.com>"

c0 = "\33[0m"
ce = "\33[31m"
cok = "\33[32m"
cw = "\33[33m"
ci = "\33[36m"

error = f"{ce}E{c0}:"
done = f"{cok}OK{c0}:"
warning = f"{cw}W{c0}:"


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
        serverfct = choose_server()

    serverfct = ""
    if srvidx in range(len(servers)):
        serverfct = servers[srvidx]
    else:
        print(f"{error} Out of range choice '{srvidx}'")
        serverfct = choose_server()

    return serverfct


def install_server(srv):
    if srv == "pxe":
        pxe.config()
        pxe.install()
    else:
        print(f"{error} Unsupported (yet ?) server function '{srv}'")
        exit(1)
