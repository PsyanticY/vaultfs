from __future__ import with_statement

import os
import sys
import errno
from vault_api import get_secrets
from logger import VaultfsLogger

from fuse import FUSE, FuseOSError, Operations


class Passthrough(Operations):
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
        print('fullpath here1')
        return path

    # Filesystem methods
    # ==================

    def access(self, path, mode):
        print('fullpath here2')
        full_path = self._full_path(path)
        if not os.access(full_path, mode):
            raise FuseOSError(errno.EACCES)

    def chmod(self, path, mode):
        print('fullpath here3')
        full_path = self._full_path(path)
        return os.chmod(full_path, mode)

    def chown(self, path, uid, gid):
        print('fullpath here4')
        full_path = self._full_path(path)
        return os.chown(full_path, uid, gid)

    def getattr(self, path, fh=None):
        print('fullpath here5')
        full_path = self._full_path(path)

        if not os.path.exists(full_path):
            print(full_path)
            secret_name = os.path.basename(full_path)
            print('getting stuff from vault')
            for i in range(0,len(self.secrets_path)):
                print (i)
                (secret_file, status) = get_secrets(self.payload, self.remote, self.secrets_path[i], secret_name)
                if status == "Success":
                    with open(full_path, "w") as f:
                         f.write(secret_file)
                    f.close()
                    break
        else:
            pass
            # check checksum and compare files
        st = os.lstat(full_path)
        print("hhhhhhh")
        return dict((key, getattr(st, key)) for key in ('st_atime', 'st_ctime',
                     'st_gid', 'st_mode', 'st_mtime', 'st_nlink', 'st_size', 'st_uid', 'st_blocks'))


    def readdir(self, path, fh):
        print('fullpath here6')
        full_path = self._full_path(path)
        print('readdir here')
        dirents = ['.', '..']
        if os.path.isdir(full_path):
            dirents.extend(os.listdir(full_path))
        for r in dirents:
            yield r


    def statfs(self, path):
        print('fullpath here7')
        full_path = self._full_path(path)
        stv = os.statvfs(full_path)
        return dict((key, getattr(stv, key)) for key in ('f_bavail', 'f_bfree',
            'f_blocks', 'f_bsize', 'f_favail', 'f_ffree', 'f_files', 'f_flag',
            'f_frsize', 'f_namemax'))


    def utimens(self, path, times=None):
        print('fullpath here8')
        return os.utime(self._full_path(path), times)

    # File methods
    # ============

    def open(self, path, flags):
        print('fullpath here9')
        full_path = self._full_path(path)
        return os.open(full_path, flags)

    def create(self, path, mode, fi=None):
        print('fullpath here10')
        full_path = self._full_path(path)
        return os.open(full_path, os.O_WRONLY | os.O_CREAT, mode)

    def read(self, path, length, offset, fh):
        print('fullpath here11')
        os.lseek(fh, offset, os.SEEK_SET)
        return os.read(fh, length)

    def write(self, path, buf, offset, fh):
        print('fullpath here12')
        os.lseek(fh, offset, os.SEEK_SET)
        return os.write(fh, buf)

    def flush(self, path, fh):
        print('fullpath here13')
        return os.fsync(fh)

    def release(self, path, fh):
        print('fullpath here14')
        return os.close(fh)

    def fsync(self, path, fdatasync, fh):
        print('fullpath here15')
        return self.flush(path, fh)


def main(mountpoint, root):
    FUSE(Passthrough(root, "https://blabla.com:8200", "test.json", ["sharedProd", "mvdDev"]), mountpoint, nothreads=True, foreground=True)

if __name__ == '__main__':
    main(sys.argv[2], sys.argv[1])



## non existing file:
# cat : 5 1
# rm: 5 1 5 1
# ll: 5 1
#chmod 5 1 3 1 5 1

## existing file:
# rm : 5 1 2 1
# ll : 5 1
# cat: 5 1 9 1 11 5 1 13 14

# eixting folder
#chown : 5 1 4 1 5 1
