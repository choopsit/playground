#!/usr/bin/env python3

import os
import shutil
import urllib.request
import mylib

__description__ = "Configuration management module"
__author__ = "Choops <choopsbd@gmail.com>"


def fix_hostname(hostname, domain):
    """Apply machine naming"""

    with open("/etc/hostname", "w") as f:
        f.write(f"{hostname}\n")

    hostline = f"127.0.1.1\t{hostname}"
    if domain != "":
        hostline += f".{domain}\t{hostname}"

    mylib.file.overwrite("/etc/hosts", "/tmp/hosts")
    with open("/tmp/hosts", "r") as oldf, open("/etc/hosts", "w") as newf:
        for line in oldf:
            if line.startswith("127.0.1.1"):
                newf.write(hostline)
            else:
                newf.write(line)

    os.system(f"hostname {hostname}")


def deploy_scripts(srcfolder):
    """Deploy scripts to '/usr/local/bin'"""

    src = f"{srcfolder}/bin"
    tgt = "/usr/local/bin"
    for script in os.listdir(src):
        if not os.path.exists(f"{tgt}/{script}"):
            shutil.copy(f"{src}/{script}", f"{tgt}/{script}")


def bash(home):
    """Apply bash configuration"""

    srcfolder = os.path.dirname(os.path.realpath(__file__))

    profilesrc = f"{srcfolder}/home/profile"
    profiletgt = f"{home}/.profile"
    mylib.file.overwrite(profilesrc, profiletgt)

    bashcfg = f"{home}/.config/bash"
    if not os.path.isdir(bashcfg):
        os.makedirs(bashcfg)

    if os.path.isfile(f"{home}/.bashrc"):
        os.remove(f"{home}/.bashrc")

    for bashfile in ["aliases", "history", "logout"]:
        bashfilesrc = f"{home}/.bash_{bashfile}"
        bashfiletgt = f"{bashcfg}/{bashfile}"
        if os.path.isfile(bashfilesrc):
            shutil.move(bashfilesrc, bashfiletgt)

    if home == "/root":
        bashrcsrc = f"{srcfolder}/home/config/bash/bashrc_root"
    else:
        bashrcsrc = f"{srcfolder}/home/config/bash/bashrc_user"
    bashrctgt = f"{bashcfg}/bashrc"
    mylib.file.overwrite(bashrcsrc, bashrctgt)


def vim(home):
    """Apply vim configuration"""

    srcfolder = os.path.dirname(os.path.realpath(__file__))

    for oldfile in [f"{home}/.vimrc", f"{home}/.viminfo"]:
        if os.path.isfile(oldfile):
            os.remove(oldfile)

    vimcfg = f"{home}/.vim"
    if not os.path.isdir(vimcfg):
        os.makedirs(vimcfg)

    mylib.file.overwrite(f"{srcfolder}/home/vim", vimcfg)

    plugfolder = f"{vimcfg}/autoload"
    if not os.path.isdir(plugfolder):
        os.makedirs(plugfolder)
    rawgiturl = "https://raw.githubusercontent.com/"
    plugurl = f"{rawgiturl}junegunn/vim-plug/master/plug.vim"
    urllib.request.urlretrieve(plugurl, f"{plugfolder}/plug.vim")

    if user == "root":
        os.system("vim +PlugInstall +qall")


def root():
    """Apply 'root' configuration"""

    bash("/root")
    vim("/root")
    os.system("update-alternatives --set editor /usr/bin/vim.basic")


def swap():
    """Apply swap configuration"""

    swapconf = "/etc/sysctl.d/99-swappiness.conf"
    swapconfok = False

    if os.path.isfile(swapconf):
        with open(swapconf, "r") as f:
            if "vm.swappiness=5" in f.read():
                swapconfok = True

    if not swapconfok:
        with open(swapconf, "w") as f:
            for newline in ["vm.swappiness=5\n", "vm.vfs_cache_pressure=50\n"]:
                f.write(newline)

    os.system(f"sysctl -p {swapconf}")
    os.system("swapoff -av")
    os.system("swapon -av")


def ssh():
    """Apply ssh configuration"""

    sshconf = "/etc/ssh/sshd_config"
    sshconfok = False

    with open(sshconf, "r") as f:
        for line in f:
            if re.match('^PermitRootLogin yes', line):
                sshconfok = True

    if not sshconfok:
        tmpfile = "/tmp/sshd_config"
        with open(sshconf, "r") as oldf, open(tmpfile, "w") as tmpf:
            for line in oldf:
                if "PermitRootLogin" in line:
                    tmpf.write("PermitRootLogin yes\n")
                else:
                    tmpf.write(line)
        shutil.copy(tmpfile, sshconf)

    os.system("systemctl restart ssh")
