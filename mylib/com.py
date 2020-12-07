#!/usr/bin/env python3

import os
import re
import socket

__description__ = "Common functions module"
__author__ = "Choops <choopsbd@gmail.com>"

c0 = "\33[0m"
ce = "\33[31m"
cok = "\33[32m"
cw = "\33[33m"
ci = "\33[36m"

error = f"{ce}E{c0}:"
done = f"{cok}OK{c0}:"
warning = f"{cw}W{c0}:"


def yesno(question, default):
    """Ask a question awaiting a yes or no answer with a default choice"""

    answer = ""

    if default == "y":
        defindic = "[Y/n]"
    else:
        defindic = "[y/N]"

    answer = input(f"{question} {defindic} ? ")
    if answer == "":
        answer = default
    elif not re.match('^(y|yes|n|no)$', answer):
        print(f"{error} Invalid answer '{answer}'")
        answer = yesno(question, default)

    return answer


def reboot():
    """Ask for reboot"""

    rebootnow = yesno("Reboot now", "y")
    if not re.match('^(n|no)$', rebootnow):
        os.system("reboot")


def get_distro():
    """Return distro name based on '/etc/os-release' content"""

    distro = ""

    with open("/etc/os-release", "r") as f:
        for line in f:
            if line.startswith("ID="):
                distro = line.split("=")[1].rstrip()

    return distro


def get_codename():
    """Return codename based on '/etc/os-release' content"""

    codename = ""

    with open("/etc/os-release", "r") as f:
        for line in f:
            if line.startswith("VERSION_CODENAME="):
                codename = line.split("=")[1].rstrip()

    if get_distro() == "debian":
        stable = "buster"
        testing = "bullseye"

        if codename != stable:
            testsid = "apt search firefox 2>/dev/null | grep ^firefox/"

            if os.popen(testsid).read() != "":
                codename = "sid"
            else:
                codename = testing

    return codename


def is_valid_hostname(hostname):
    """Check validity of a string to be used as hostname"""

    if len(hostname) > 255:
        return False

    if hostname[-1] == ".":
        hostname = hostname[:-1]
    allowed = re.compile("(?!-)[A-Z\d-]{1,63}(?<!-)$", re.IGNORECASE)

    return all(allowed.match(x) for x in hostname.split("."))


def decompose_fqdn(fqdn):
    """Split FQDN in hostname and domain"""

    hostname = fqdn.split(".")[0]
    domain = ".".join(fqdn.split(".")[1:])

    return hostname, domain


def set_hostname():
    """Define a machine hostname"""

    current = socket.getfqdn()
    keepcurrent = input(f"Keep current hostname: '{current}' [Y/n] ? ")
    if re.match("^(n|no)$", keepcurrent.lower()):
        newhostname = input("New hostname (or FQDN) ? ")
        if newhostname == "":
            print(f"{error} No hostname given")
            hostname, domain = set_hostname()
        elif is_valid_hostname(newhostname):
            hostname, domain = decompose_fqdn(newhostname)
        else:
            print(f"{error} Invalid hostname '{newhostname}'")
            hostname, domain = set_hostname()
    else:
        hostname, domain = decompose_fqdn(current)

    return hostname, domain


def list_users():
    """List users having their home directory at '/home/{user}'"""

    userslist = []
    potentialusers = os.listdir("/home")
    for user in potentialusers:
        with open("/etc/passwd") as f:
            for line in f:
                if line.startswith(f"{user}:"):
                    userslist.append(user)

    return userslist


def is_user_to_add_to_group(user, grp):
    """Check if user '{user}' is in group '{grp}'"""

    ret = False
    
    grplist = os.popen(f"groups {user}").read()

    if grp in grplist:
        print(f"{done} '{user}' already in '{grp}'")
    else:
        adduser = yesno(f"Add '{user}' to '{grp}'", "y")
        if not re.match('^(n|no)', adduser):
            ret = True

    return ret


def add_user_to_group(user, grp):
    """Add '{user}' to group '{grp}'"""

    os.system(f"adduser {user} {grp}")


def is_vm():
    """Check if machine is virtual"""

    testkvm = "lspci | grep -q paravirtual"
    testvbox = "lspci | grep -iq virtualbox"
    if os.system(testkvm) == 0 or os.system(testvbox) == 0:
        return True
    else:
        return False
