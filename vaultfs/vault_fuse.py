from __future__ import with_statement

import os
import sys
import errno
from vault_api import get_secrets
from logger import VaultfsLogger

from fuse import FUSE, FuseOSError, Operations


class vault_fuse(Operations):
    def __init__(self, root, remote, payload, secrets_path):#, data_key):
        self.root = root
        self.remote = remote
        self.payload = payload
        self.log = VaultfsLogger()
        self.secrets_path = secrets_path
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

        if not os.path.exists(full_path):
            secret_name = os.path.basename(full_path)
            #FIXME The fuck are those files
            if secret_name in ".xdg-volume-info" "autorun.inf" :
                pass
            else:
                self.log.info("Looking for {} in {}".format(secret_name, self.remote))
                notFound = 0
                for i in range(0,len(self.secrets_path)):
                    (result, status) = get_secrets(self.payload, self.remote, self.secrets_path[i], secret_name)
                    if status == "Success":
                        with open(full_path, "w") as f:
                            f.write(result)
                        f.close()
                        break
                    elif status == "Forbidden":
                        self.log.error("{}: {}".format(status, result))
                        # quit the loop since we can't authenticate to the server
                        break
                    elif status == "NotFound":
                        notFound += 1
                    else : 
                        self.log.error("{}: {}".format(status, result))
                        break
                if (notFound == len(self.secrets_path)):
                    self.log.error("Can't find secret {} in provided secret engines: {} ".format(secret_name, ', '.join(self.secrets_path)))
        else:
            pass
            # check checksum and compare files
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

    def flush(self, path, fh):
        return os.fsync(fh)

    def release(self, path, fh):
        return os.close(fh)

    def fsync(self, path, fdatasync, fh):
        return self.flush(path, fh)

