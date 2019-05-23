from __future__ import with_statement

import os
import sys
import errno
import time
from datetime import datetime
from vaultfs.vault_api import get_secrets, secrets_time
from vaultfs.logger import VaultfsLogger
#from logger import VaultfsLogger
#from vault_api import get_secrets, secrets_time


from fuse import FUSE, FuseOSError, Operations


class vault_fuse(Operations):
    def __init__(self, root, remote, payload, secrets_path, recheck_timestamp):#, data_key):
        self.root = root
        self.remote = remote
        self.payload = payload
        self.log = VaultfsLogger()
        self.secrets_path = secrets_path
        self.recheck_timestamp = recheck_timestamp
        #self.data_key = data_key

    # Helpers
    # =======

    def _full_path(self, partial):
        if partial.startswith("/"):
            partial = partial[1:]
        path = os.path.join(self.root, partial)
        return path

    # Filesystem methods
    # ==================

    def access(self, path, mode):
        full_path = self._full_path(path)
        if not os.access(full_path, mode):
            raise FuseOSError(errno.EACCES)

    def chmod(self, path, mode):
        full_path = self._full_path(path)
        return os.chmod(full_path, mode)

    def chown(self, path, uid, gid):
        full_path = self._full_path(path)
        return os.chown(full_path, uid, gid)

    def getattr(self, path, fh=None):
        full_path = self._full_path(path)
        secret_name = os.path.basename(full_path)
        #FIXME The fuck are those files
        if secret_name in ".xdg-volume-info" "autorun.inf" :
            pass
        else:
            if not os.path.exists(full_path):
                self.log.info("Looking for {} in {}".format(secret_name, self.remote))
                get_secrets(self.payload, self.remote, self.secrets_path, secret_name, full_path)
            if os.path.exists(full_path):
                last_modif = getattr(os.lstat(full_path), 'st_mtime')
                # if last modification was a week ago check for updates form vault
                # swithc to >
                time_now = time.mktime(time.strptime(str(datetime.utcnow()).split(".", 1)[0], '%Y-%m-%d %H:%M:%S'))
                # hack to convert st_mtime to UTC
                diff = time_now - time.time()
                last_modif = last_modif + diff
                if (time_now - last_modif) >= self.recheck_timestamp:
                    creation_time = secrets_time(self.payload, self.remote, self.secrets_path, secret_name)
                    if creation_time == None:
                        self.log.warning("secret `{}` not found in vault, ignoring...".format(secret_name))
                        return
                    else:
                        creation_time_epoch = time.mktime(time.strptime(creation_time, '%Y-%m-%dT%H:%M:%S'))
                        if creation_time_epoch < last_modif:
                            os.utime(full_path)
                        else:
                            self.log.info("updating `{}` from vault...".format(secret_name))
                            get_secrets(self.payload, self.remote, self.secrets_path, secret_name, full_path)

        st = os.lstat(full_path)
        return dict((key, getattr(st, key)) for key in ('st_atime', 'st_ctime',
                     'st_gid', 'st_mode', 'st_mtime', 'st_nlink', 'st_size', 'st_uid', 'st_blocks'))

    def readdir(self, path, fh):
        full_path = self._full_path(path)
        dirents = ['.', '..']
        if os.path.isdir(full_path):
            dirents.extend(os.listdir(full_path))
        for r in dirents:
            yield r

    def mknod(self, path, mode, dev):
        return os.mknod(self._full_path(path), mode, dev)

    def rmdir(self, path):
        full_path = self._full_path(path)
        return os.rmdir(full_path)

    def mkdir(self, path, mode):
        return os.mkdir(self._full_path(path), mode)

    def unlink(self, path):
        return os.unlink(self._full_path(path))

    def symlink(self, name, target):
        return os.symlink(name, self._full_path(target))

    def rename(self, old, new):
        return os.rename(self._full_path(old), self._full_path(new))

    def link(self, target, name):
        return os.link(self._full_path(target), self._full_path(name))

    def statfs(self, path):
        full_path = self._full_path(path)
        stv = os.statvfs(full_path)
        return dict((key, getattr(stv, key)) for key in ('f_bavail', 'f_bfree',
            'f_blocks', 'f_bsize', 'f_favail', 'f_ffree', 'f_files', 'f_flag',
            'f_frsize', 'f_namemax'))


    def utimens(self, path, times=None):
        return os.utime(self._full_path(path), times)

    # File methods
    # ============

    def open(self, path, flags):
        full_path = self._full_path(path)
        return os.open(full_path, flags)

    def create(self, path, mode, fi=None):
        full_path = self._full_path(path)
        return os.open(full_path, os.O_WRONLY | os.O_CREAT, mode)

    def read(self, path, length, offset, fh):
        os.lseek(fh, offset, os.SEEK_SET)
        return os.read(fh, length)

    def write(self, path, buf, offset, fh):
        os.lseek(fh, offset, os.SEEK_SET)
        return os.write(fh, buf)

    def truncate(self, path, length, fh=None):
        full_path = self._full_path(path)
        with open(full_path, 'r+') as f:
            f.truncate(length)

    def flush(self, path, fh):
        return os.fsync(fh)

    def release(self, path, fh):
        return os.close(fh)

    def fsync(self, path, fdatasync, fh):
        return self.flush(path, fh)

