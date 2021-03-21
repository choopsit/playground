#!/usr/bin/env python3

import sys
import os
import re
import mylib
import wslib


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


def usage(errcode):
    myscript = os.path.basename(__file__)
    print(f"{ci}{__description__}\nUsage{c0}:")
    print(f"  './{myscript} [OPTION]' as root or using 'sudo'")
    print(f"{ci}Options{c0}:")
    print(f"  -h,--help: Print this help")
    print()
    exit(errcode)


if __name__ == "__main__":
    if len(sys.argv) > 1:
        if re.match('^-(h|-help)$', sys.argv[1]):
            usage(0)
        else:
            print(f"{error} Bad argument")
            usage(1)

    mydistro = mylib.get_distro()
    mycodename = mylib.get_codename()

    mylib.prereq(mydistro, mycodename)

    myhostname, mydomain = mylib.set_hostname()

    myde = wslib.choose_de()

    myusers = mylib.list_users()
    mydeusers = wslib.deusers_add(myde, myusers)

    additions = wslib.choose_additions()

    newgroups = ["sudo"]
    moreinst = []
    moreprecmds = []
    morepkgs = []

    if re.match('^(y|yes)$', additions["nfssrv"]):
        moreinst += ["NFS server"]
        morepkgs += ["nfs-kernel-server"]

    if re.match('^(y|yes)$', additions["docker"]):
        newgroups.append("docker")
        moreinst += ["Docker"]
        morepkgs += ["docker-compose"]

    if re.match('^(y|yes)$', additions["vbox"]):
        newgroups.append("vboxusers")
        moreinst += ["VirtualBox"]
        morepkgs += ["virtualbox", "virtualbox-ext-pack",
                     "Virtualbox-guest-additions-iso"]

    if re.match('^(y|yes)$', additions["tsmd"]):
        moreinst += ["Transmission-daemon"]
        morepkgs += ["transmission-daemon"]
        tsmduser = ""
        for (home, user, grp) in mydeusers:
            oktsm = mylib.yesno(f"Make '{user}' transmision-daemon user",
                                    "n")
            if re.match('^(y|yes)$', oktsm):
                tsmduser = user
                break
        if tsmduser == "":
            tsmduser = mydeusers[0][1]

    if re.match('^(y|yes)$', additions["mediatools"]):
        moreinst += ["Multimedia utilities"]
        morepkgs += ["easytag", "audacity"]

    if re.match('^(y|yes)$', additions["kodi"]):
        moreinst += ["Kodi MediaCenter"]
        morepkgs += ["kodi"]

    if re.match('^(y|yes)$', additions["steam"]):
        moreinst += ["Steam"]
        steamagree = "echo steam steam/question select 'I AGREE'"
        steamagree += " | debconf-set-selections"
        steamlicnote = "echo steam steam/license note ''"
        steamlicnote += " | debconf-set-selections"
        moreprecmds += [steamagree, steamlicnote]
        morepkgs += ["steam"]

    if myhostname == "mrchat":
        moreinst += ["Conky", "Games"]
        morepkgs += ["conky-all", "gnome-2048", "quadrapassel", "supertuxkart"]

    newingroups = {}
    for user in myusers:
        for grp in newgroups:
            newingroups[grp] = []
            if mylib.is_user_to_add_to_group(user, grp):
                newingroups[grp].append(user)

    print(f"\n{ci}Workstation settings{c0}:")
    print(f"  - {ci}Hostname{c0}:            {myhostname}")
    if mydomain != "":
        print(f"  - {ci}Domain{c0}:              {mydomain}")
    print(f"  - {ci}Desktop Environment{c0}: {myde}")
    if  newingroups["sudo"]!= []:
        print(f"  - {ci}Give 'sudo' privileges to{c0}:")
        for user in newingroups["sudo"]:
            print(f"    - {user}")
    if moreinst != []:
        print(f"  - {ci}Additional installations{c0}:")
        for inst in moreinst:
            print(f"    - {inst}")
    confconf = mylib.yesno("Confirm configuration", "y")
    if re.match('^(n|no)$', confconf):
        exit(0)

    mylib.conf.fix_hostname(myhostname, mydomain)
    mylib.pkg.update_sourceslist(mydistro)
    wslib.inst.de(myde, mycodename, myhostname)

    if moreprecmds != []:
        for cmd in moreprecmds:
            os.system(cmd)
    if morepkgs != []:
        if "steam" in morepkgs:
            os.system("dpkg --add-architecture i386")
            os.system("apt update")

        mylib.pkg.install(morepkgs)

    for grp, users in newingroups.items():
        mylib.add_user_to_group(user, grp)

    mylib.conf.swap()
    mylib.conf.ssh()

    if mylib.pkg.is_installed("lightdm"):
        wslib.conf.lightdm()
    if mylib.pkg.is_installed("network-manager"):
        wslib.conf.networkmanager()
    if mylib.pkg.is_installed("pulseaudio-utils"):
        wslib.conf.pulseaudio()
    if mylib.pkg.is_installed("redshift"):
        wslib.conf.redshift()
    if mylib.pkg.is_installed("transmission-daemon"):
        wslib.conf.transmissiond(tsmduser)

    mylib.conf.deploy_scripts()

    mylib.conf.root()

    wslib.conf.user(myde, "/etc/skel", "root", "root")
    for deuser in mydeusers:
        wslib.conf.user(myde, *deuser)

    wslib.inst.themes()

    wslib.conf.specials(myhostname)

    print(f"{done} '{myde}' installed")
    mylib.reboot()
