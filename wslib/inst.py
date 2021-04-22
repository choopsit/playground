#!/usr/bin/env python3

import os
import mylib

__description__ = "Workstation installation management module"
__author__ = "Choops <choopsbd@gmail.com>"

c0 = "\33[0m"
ce = "\33[31m"
cok = "\33[32m"
cw = "\33[33m"
ci = "\33[36m"

error = f"{ce}E{c0}:"
done = f"{cok}OK{c0}:"
warning = f"{cw}W{c0}:"


def awesome(basepkgs):
    """Append packagelists for AwesomeWM"""

    awesomepkgs = ["xorg", "mesa-utils", "awesome", "awesome-extra", "psmisc",
                   "lightdm", "slick-greeter", "compton", "terminator"]
    appspkgs = ["gimp", "imagemagick", "mpv"]
    stylepkgs = ["arc-theme", "papirus-icon-theme"]

    pkgs = basepkgs + awesomepkgs + appspkgs + stylepkgs

    return pkgs


def xfce(basepkgs):
    """Append packagelists for XFCE"""

    xfcepkgs = ["task-xfce-desktop", "task-desktop", "slick-greeter",
                "gvfs-backends", "synaptic", "xfce4-appfinder",
                "xfce4-appmenu-plugin", "xfce4-clipman-plugin",
                "xfce4-power-manager", "xfce4-pulseaudio-plugin",
                "xfce4-weather-plugin", "xfce4-whiskermenu-plugin",
                "xfce4-xkb-plugin", "xfce4-screenshooter",
                "catfish", "plank"]
    syspkgs = ["cups", "printer-driver-escpr", "system-config-printer",
               "network-manager-gnome", "gparted"]
    appspkgs = ["terminator", "redshift-gtk", "gnome-system-monitor", "gedit",
                "gedit-plugins", "galculator", "gthumb", "simple-scan",
                "remmina", "blender", "gimp"]
    stylepkgs = ["arc-theme", "papirus-icon-theme", "libreoffice-gtk3",
                 "libreoffice-style-sifr"]

    pkgs = basepkgs + xfcepkgs + syspkgs + appspkgs + stylepkgs

    uselesspkgs = ["xfce4-taskmanager", "xfce4-terminal", "xfburn", "xsane",
                   "exfalso", "quodlibet", "hv3", "parole", "ristretto",
                   "mousepad", "xterm", "libreoffice-base"]

    return pkgs, uselesspkgs


def de(de, codename, hostname):
    """Install Dexktop Environment"""

    mylib.pkg.upgrade()

    if codename == "sid":
        firefox = ["firefox"]
        compositor = ["picom"]
    else:
        firefox = ["firefox-esr"]
        compositor = ["compton"]
    if codename == "buster":
        mediaplayers = ["gnome-mpv", "rhythmbox",
                        "rhythmbox-plugin-alternative-toolbar"]
    else:
        mediaplayers = ["celluloid", "lollypop", "kid3-cli"]

    syspkgs = ["firmware-linux", "build-essential", "nfs-common", "deborphan",
               "sudo", "vim", "curl", "git", "ssh", "tree", "htop", "rsync",
               "p7zip-full", "unrar", "imagemagick"]

    nvidiadrv = []
    if os.system("lspci | grep -qi nvidia") == 0:
        os.system("dpkg --add-architecture i386")
        nvidiadrv = ["nvidia-driver", "nvidia-settings", "nvidia-xconfig"]

    stdpkgs = syspkgs + nvidiadrv + firefox

    pkgs = []
    uselesspkgs = []
    if de == "xfce":
        stdpkgs += mediaplayers
        pkgs, uselesspkgs = xfce(stdpkgs)
    elif de == "awesomewm":
        stdpkgs += compositor
        pkgs = awesome(stdpkgs)

    if "nvidia-driver" in pkgs:
        os.system("dpkg --add-architecture i386")
        os.system("apt update")

    mylib.pkg.install(pkgs)

    if uselesspkgs != []:
        mylib.pkg.remove(uselesspkgs)

    mylib.pkg.clean()


def themes():
    """Install managed htemes from git by 'bin/themesupdate'"""

    origfolder = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))

    install_themes = f"{origfolder}/bin/themesupdate"
    os.system(install_themes)
