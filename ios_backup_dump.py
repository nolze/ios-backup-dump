__doc__ = """Usage:
    {f} list_backups
    {f} list_domains <backupname>
    {f} domain_info <backupname> (all | <fulldomainname>)
    {f} dump_files <backupname> (all | <fulldomainname>) <dstdir>
    {f} -h | --help

Options:
    -c --cat <ANOTHER_FILE>  concatnate target file name.
""".format(
    f=__file__
)

from docopt import docopt

import sqlite3
import tempfile
import shutil
from pathlib import Path
import logging
import plistlib
import pprint
from collections import namedtuple

pp = pprint.PrettyPrinter(indent=4)

OSX_DEFAULT_LOCATION = Path(
    "~/Library/Application Support/MobileSync/Backup/"
).expanduser()


def _copy_temporary_db(src):
    with open(src, "rb") as db_file:
        temp_fp = tempfile.NamedTemporaryFile(mode="wb")
        shutil.copyfileobj(db_file, temp_fp)
        temp_fp.seek(0)
    logging.debug(temp_fp.name)
    return temp_fp


class BackupInfo:
    def __init__(self, backupname, status):
        self.backupname = backupname
        self.status = status
        self.fullpath = Path(OSX_DEFAULT_LOCATION, backupname)
        self.manifest_path = self.fullpath.joinpath(Path("Manifest.db"))

    def pprint(self):
        pp.pprint(
            {
                "backupname": self.backupname,
                "fullpath": self.fullpath,
                "status": self.status,
            }
        )


class DomainInfo:
    def __init__(self, fulldomainname, path_mapping):
        self.fulldomainname = fulldomainname
        self.domaintype = fulldomainname.split("-", 1)[0]
        self.domainname = (
            fulldomainname.split("-", 1)[1]
            if len(fulldomainname.split("-", 1)) > 1
            else ""
        )
        self.path_mapping = path_mapping

    def dump_files(self, backup_fullpath, dstdir):
        dstdir = dstdir.joinpath(Path(self.domaintype, self.domainname))
        for internal_path, rel_path in self.path_mapping.items():
            logging.debug(internal_path, rel_path)
            src = backup_fullpath.joinpath(internal_path)
            logging.debug(src)
            dst = dstdir.joinpath(Path(rel_path))
            logging.debug(dst)
            if not src.exists():
                dst.mkdir(parents=True, exist_ok=True)
            else:
                dst.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(src, dst)

    def pprint(self):
        pp.pprint(
            {"fulldomainname": self.fulldomainname, "path_mapping": self.path_mapping}
        )


def list_backups(basedir):
    if not basedir.is_dir():
        return
    res = []
    for d in basedir.iterdir():
        if not d.is_dir():
            continue
        status = Path(d, "Status.plist")
        if status.exists():
            with open(status, "rb") as f:
                pl = plistlib.load(f)
                backupinfo = BackupInfo(d.name, pl)
                res.append(backupinfo)
    return res


def print_domains(res, only_include=["AppDomain"]):
    for item in res:
        if only_include and item[0] not in only_include:
            continue
        else:
            dt, dn = item
            print("-".join(item))


def get_domaininfo_by_domain(manifest, fulldomainname):
    logging.debug(manifest)
    conn = sqlite3.connect(manifest)
    cur = conn.cursor()
    cur.execute(
        "SELECT DISTINCT FileId, relativePath FROM Files WHERE domain=?",
        (fulldomainname,),
    )
    res = cur.fetchall()
    logging.debug(res)

    path_mapping = {}

    for item in res:
        fileid, rel_path = item
        head = fileid[:2]
        internal_path = "{}/{}".format(head, fileid)
        path_mapping[internal_path] = rel_path
    domaininfo = DomainInfo(fulldomainname, path_mapping)

    conn.close()
    return domaininfo


def list_domains(manifest):
    conn = sqlite3.connect(manifest)
    cur = conn.cursor()
    cur.execute("SELECT DISTINCT domain FROM Files")
    res = cur.fetchall()
    res = map(lambda x: x[0].split("-", 1), res)

    conn.close()
    return res


if __name__ == "__main__":
    args = docopt(__doc__, options_first=True)
    logging.debug(args)
    if args["list_backups"]:
        backups = list_backups(OSX_DEFAULT_LOCATION)
        for backup in backups:
            backup.pprint()

    if args["list_domains"]:
        p = Path(args["<backupname>"])
        if p.is_file():
            manifest_temp = _copy_temporary_db(p)
        else:
            backup = BackupInfo(p, {})
            manifest_temp = _copy_temporary_db(backup.manifest_path)
        domains = list_domains(Path(manifest_temp.name))
        print_domains(domains)

        manifest_temp.close()

    if args["domain_info"]:
        p = Path(args["<backupname>"])
        if p.is_file():
            manifest_temp = _copy_temporary_db(p)
        else:
            backup = BackupInfo(p, {})
            manifest_temp = _copy_temporary_db(backup.manifest_path)
        if args["<fulldomainname>"]:
            domaininfo = get_domaininfo_by_domain(
                Path(manifest_temp.name), args["<fulldomainname>"]
            )
            domaininfo.pprint()
        elif args["all"]:
            domains = list_domains(Path(manifest_temp.name))
            for domain in domains:
                domaininfo = get_domaininfo_by_domain(
                    Path(manifest_temp.name), "-".join(domain)
                )
                domaininfo.pprint()
        manifest_temp.close()

    if args["dump_files"] and args["<dstdir>"]:
        p = Path(args["<backupname>"])
        backup = BackupInfo(p, {})
        manifest_temp = _copy_temporary_db(backup.manifest_path)
        if args["<fulldomainname>"]:
            domaininfo = get_domaininfo_by_domain(
                Path(manifest_temp.name), args["<fulldomainname>"]
            )
            domaininfo.dump_files(backup.fullpath, Path(args["<dstdir>"]))
        elif args["all"]:
            domains = list_domains(Path(manifest_temp.name))
            for domain in domains:
                domaininfo = get_domaininfo_by_domain(
                    Path(manifest_temp.name), "-".join(domain)
                )
                domaininfo.dump_files(backup.fullpath, Path(args["<dstdir>"]))
        manifest_temp.close()
