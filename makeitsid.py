#!/usr/bin/env python3

import sys
import re
import os
import mylib

__description__ = "Make a Debian stable or testing switch to sid (unstable)"
__author__ = "Choops <choopsbd@gmail.com>"


def usage():
    myscript = f"{os.path.basename(__file__)}"
    print(f"{ci}{__description__}\nUsage{c0}:")
    print(f"  './{myscript} [OPTION]' as root or using 'sudo'")
    print(f"{ci}Options{c0}:")
    print(f"  -h,--help: Print this help")
    print()


def sid_sourceslist(codename, stable):
    newsl = True
    sourceslist = "/etc/apt/sources.list"
    srcurl = "http://deb.debian.org/debian"
    branch = "main contrib non-free"

    sl = ["# sid\n",
          f"deb {srcurl}/ sid {branch}\n",
          f"#deb-src {srcurl}/ sid {branch}\n\n",
          "# testing\n",
          f"#deb {srcurl}/ testing {branch}\n",
          f"#deb-src {srcurl}/ testing {branch}\n",
          "# testing security\n",
          f"#deb {srcurl}-security/ testing-security/updates {branch}\n",
          f"#deb-src {srcurl}-security/ testing-security/updates {branch}\n\n",
          f"# {stable}\n",
          f"#deb {srcurl}/ {stable} {branch}\n",
          f"#deb-src {srcurl}/ {stable} {branch}\n",
          f"# {stable} security\n",
          f"#deb {srcurl}-security/ {stable}/updates {branch}\n",
          f"#deb-src {srcurl}-security/ {stable}/updates {branch}\n",
          f"# {stable} volatiles\n",
          f"#deb {srcurl}/ {stable}-updates {branch}\n",
          f"#deb-src {srcurl}/ {stable}-updates {branch}\n"]

    if codename == "sid":
        print(f"{warning} Already sid")
        renewsl = mylib.yesno(f"Renew '{sourceslist}'", "n")
        if not re.match('^(y|yes)$', renewsl.lower()):
            newsl = False
    else:
        herewego = mylib.yesno(f"Upgrade {codename} to sid", "y")
        if re.match('^(n|no)$', herewego.lower()):
            exit(0)

    if newsl:
        with open(sourceslist, "w") as f:
            for line in sl:
                f.write(line)


def switch_firefox():
    swok = True
    swfirefox_cmds = ["apt install firefox 2>/dev/null",
                      "apt purge firefox-esr 2>/dev/null",
                      "apt autoremove --purge -yy 2>/dev/null"]

    swfirefox = mylib.yesno("\nSwitch firefox-esr to firefox", "y")
    if not re.match('^(n|no)', swfirefox.lower()):
        for cmd in swfirefox_cmds:
            if os.system(cmd) != 0:
                swok = False

    if swok:
        print(f"{done} firefox-esr switched to firefox")
    else:
        print(f"{error} Failed to switch firefox-esr to firefox")
        exit(1)


c0 = "\33[0m"
ce = "\33[31m"
cok = "\33[32m"
cw = "\33[33m"
ci = "\33[36m"

error = f"{ce}E{c0}:"
done = f"{cok}OK{c0}:"
warning = f"{cw}W{c0}:"

if __name__ == "__main__":
    if len(sys.argv) > 1:
        if re.match('^-(h|-help)$', sys.argv[1]):
            usage()
            exit(0)
        else:
            print(f"{error} Bad argument")
            usage()
            exit(1)

    distro = mylib.get_distro()
    if distro != "debian":
        print(f"{error} OS is not Debian")
        exit(1)

    if os.getuid() != 0:
        print(f"{error} Need higher privileges")
        exit(1)

    stable = "buster"
    olddebian = ["stretch", "jessie", "wheezy", "squeeze", "lenny"]

    codename = mylib.get_codename()
    if codename in olddebian:
        print(f"{error} '{codename}' is a too old Debian version")
        exit(1)

    sid_sourceslist(codename, stable)

    mylib.pkg.upgrade()
    mylib.pkg.clean()
    
    if os.system("dpkg -l | grep -q 'firefox-esr'") == 0:
        switch_firefox()

    if codename == "sid":
        print(f"{done} Renewed '/etc/sources.list'")
    else:
        print(f"{done} Upgraded from {codename} to sid")
    mylib.reboot()
