#!/usr/bin/env python3

import os
import re
import shutil
import mylib

__description__ = "Workstation configuration management module"
__author__ = "Choops <choopsbd@gmail.com>"

c0 = "\33[0m"
ce = "\33[31m"
cok = "\33[32m"
cw = "\33[33m"
ci = "\33[36m"

error = f"{ce}E{c0}:"
done = f"{cok}OK{c0}:"
warning = f"{cw}W{c0}:"


def deploy_dotconfig(home, confcontent, srcfolder):
    for conf in confcontent:
        src = f"{srcfolder}/home/config/{conf}"
        tgt = f"{home}/.config/{conf}"
        if os.path.isdir(tgt):
            if home == "/etc/skel":
                mylib.file.overwrite(src, tgt)
            else:
                print(f"{warning} '{tgt}' already exists")
                resetconf = mylib.com.yesno("Overwrite it", "y")
                if not re.match('^(n|no)', resetconf.lower()):
                    mylib.file.overwrite(src, tgt)
        else:
            shutil.copytree(src, tgt, symlinks=True)


def deploy_dotlocal(home, srcfolder):
    for loc in os.listdir(f"{srcfolder}/home/local"):
        mylib.file.overwrite(f"{srcfolder}/home/local/{loc}",
                             f"{home}/.local/{loc}")


def awesomewm(home):
    """Deploy AwesomeWM configuration"""

    srcfolder = os.path.dirname(os.path.realpath(__file__))

    awesomesrc = "/etc/xdg/awesome/rc.lua"
    cfgfolder = f"{home}/.config/awesome"
    awesomeconf = f"{cfgfolder}/rc.lua"

    if not os.path.isdir(cfgfolder):
        os.makedirs(cfgfolder)

    with open(awesomesrc, "r") as src, open(awesomeconf, "w") as tgt:
        for line in src:
            # TODO: define default awesomewm configuration
            if line.startswith("something"):
                tgt.write("something configured\n")
            else:
                tgt.write(line)

    confcontent = ["terminator"]
    deploy_dotconfig(home, confcontent, srcfolder)


def xfce(home):
    """Deploy XFCE configuration"""

    srcfolder = os.path.dirname(os.path.realpath(__file__))

    if not os.path.isdir(f"{home}/.config"):
        os.makedirs(f"{home}/.config")

    confcontent = ["autostart", "conky", "dconf", "plank", "pluma",
                   "terminator", "Thunar", "tumbler", "xfce4"]
    deploy_dotconfig(home, confcontent, srcfolder)

    deploy_dotlocal(home, srcfolder)


def user(de, home, user, grp):
    """Deploy user configuration based on Desktop Environment"""

    mylib.conf.bash(home)
    mylib.conf.vim(home)

    if de == "xfce":
        xfce(home)
    elif de == "awesomewm":
        awesomewm(home)

    mylib.file.rchown(home, user, grp)


def lightdm():
    """Make username choosable in a list"""

    lightdmconf = "/usr/share/lightdm/lightdm.conf.d/10_my.conf"
    tmpfile = "/tmp/lightdm_perso.conf"
    newlines = ["[Seat:*]\n", "greeter-hide-users=false\n", "[Greeter]\n",
                "draw-user-backgrounds=true\n"]

    if os.path.isfile(lightdmconf):
        mylib.file.overwrite(lightdmconf, tmpfile)
        with open(tmpfile, "r") as oldf, open(lightdmconf, "a") as newf:
            for line in newlines:
                if line not in oldf:
                    newf.write(line)
    else:
        with open(lightdmconf, "w") as f:
            for line in newlines:
                f.write(line)


def redshift():
    """Link redshift to geoclue to follow local time"""

    redshiftconf = "/etc/geoclue/geoclue.conf"
    redshiftconfok = False

    with open(redshiftconf, "r") as f:
        for line in f:
            if "redshift" in line:
                redshiftconfok = True

    if not redshiftconfok:
        with open(redshiftconf, "a") as f:
            f.write("\n[redshift]\nallowed=true\nsystem=false\nusers=\n")


def pulseaudio():
    """Fix stupid default pulseaudio max volume on new application launch"""

    pulseconf = "/etc/pulse/daemon.conf"
    pulseconfok = False
    with open(pulseconf, "r") as f:
        for line in f:
            if re.match('^flat-volumes = no', line):
                pulseconfok = True
    if not pulseconfok:
        tmpfile = "/tmp/pulse_daemon.conf"
        mylib.file.overwrite(pulseconf, tmpfile)
        with open(tmpfile, "r") as oldf, open(pulseconf, "w") as newf:
            for line in oldf:
                if "flat-volumes" in line:
                    newf.write("flat-volumes = no\n")
                else:
                    newf.write(line)


def networkmanager():
    """Make network-manager manage already configured interfaces without it"""

    nwconf = "/etc/network/interfaces"
    iface = os.popen("ip r | grep default").read().split()[4]
    tmpfile = "/tmp/interfaces"
    mylib.file.overwrite(nwconf, tmpfile)
    with open(tmpfile, "r") as oldf, open(nwconf, "w") as newf:
        for line in oldf:
            if iface in line:
                newf.write(f"#{line}")
            else:
                newf.write(line)


def transmissiond(user):
    """Deploy transmission-deamon configuration with {user} as daemon user"""

    userhome = f"/home/{user}"
    os.system("systemctl stop transmission-daemon")
    tsmdconfdir = "/etc/systemd/system/transmission-daemon.service.d/"
    tsmdconf = f"{tsmdconfdir}/override.conf"

    if not os.path.isdir(tsmdconfdir):
        os.makedirs(tsmdconfdir)

    os.system("systemctl stop transmission-daemon")

    with open(tsmdconf, "w") as f:
        f.write(f"[Service]\nUser={user}\n")

    os.system("systemctl start transmission-daemon")
    os.system("systemctl stop transmission-daemon")

    tsmduserconf = f"{userhome}/.config/transmission-daemon/settings.json"
    if os.path.isfile(tsmduserconf):
        tmpfile = "/tmp/tsmdsettings.json"
        mylib.file.overwrite(tsmduserconf, tmpfile)
        with open(tmpfile, "r") as oldf, open(tsmduser, "w") as newf:
            for line in oldf:
                if '"peer-port"' in line:
                    newf.write('    "peer-port": 57413,\n')
                else:
                    newf.write(line)

    os.system("systemctl start transmission-daemon")


def specials(hostname):
    """Apply special configuration for special hosts"""

    if hostname == "mrchat":
        disks = {"grodix": "d498cab6-0d80-4b11-9c78-c422cc8ef983",
                 "speedix": "40b3c512-b22e-4842-b9e1-aa3262c4d1d8",
                 "backup": "67893919-07f9-48bf-83a2-48936aa1057c"}

        for label, partuuid in disks.items():
            mntpoint = f"/volumes/{label}"

            if not os.path.isdir(mntpoint):
                os.makedirs(mntpoint)
                shutil.chown(mntpoint, "choops", "choops")

            mntline = f"\n#{label}\nUUID={partuuid}\t{mntpoint}\tbtrfs\t"
            mntline += "defaults\t0\t0\n"
            with open("/etc/fstab", "a") as f:
                if label not in f.read():
                    f.write(mntline)

        nfsshare = "/volumes/grodix"
        subnet = "192.168.42.0/24"
        nfsopt = "rw,all_squash,anonuid=1000,anongid=1000,sync"
        nfsline = f"{nfsshare}\t{subnet}({nfsopt})"
        with open("/etc/exports", "a") as f:
            if label not in f.read():
                f.write(nfsline)
        os.system("systemctl restart nfs-kernel-server")
    else:
        pass
