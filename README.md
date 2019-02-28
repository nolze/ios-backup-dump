# ios-backup-dump

> View and dump iOS backups. (experimental, no warranty)

## Examples

```bash
$ python ios_backup_dump.py list_backups
{   'backupname': '16cbfa4aa6182d5981149393b2d6fe77d4cfa180',
    'fullpath': PosixPath('/Users/john/Library/Application Support/MobileSync/Backup/16cbfa4aa6182d5981149393b2d6fe77d4cfa180'),
    'status': {   'BackupState': 'new',
                  'Date': datetime.datetime(2020, 12, 23, 6, 7, 8, 123456),
                  'IsFullBackup': False,
                  'SnapshotState': 'finished',
                  'UUID': 'AB56A5E7-575B-461E-BED1-08D83AC5A82A',
                  'Version': '4.8'}}
...
```

```bash
$ python ios_backup_dump.py list_domains 16cbfa4aa6182d5981149393b2d6fe77d4cfa180
AppDomain-com.apple.AccountAuthenticationDialog
AppDomain-com.apple.AppStore
AppDomain-com.apple.CloudKit.ShareBear
AppDomain-com.apple.DemoApp
AppDomain-com.apple.DiagnosticsService
AppDomain-com.apple.Fitness
AppDomain-com.applidium.Vim
...
```

```bash
$ python ios_backup_dump.py dump_files 16cbfa4aa6182d5981149393b2d6fe77d4cfa180 AppDomain-com.apple.DemoApp /tmp
# dumped to /tmp/AppDomain/com.apple.DemoApp/
```

## Usage

```
Usage:
    ios_backup_dump.py list_backups
    ios_backup_dump.py list_domains <backupname>
    ios_backup_dump.py domain_info <backupname> (all | <fulldomainname>)
    ios_backup_dump.py dump_files <backupname> (all | <fulldomainname>) <dstdir>
    ios_backup_dump.py -h | --help
```
