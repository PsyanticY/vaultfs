import argparse
from fuse import FUSE
from vault_fuse import vault_fuse

def vaultfs(mountpoint, local, remote, payload, secrets_path):
    FUSE(vault_fuse(local, remote, payload, secrets_path), mountpoint, nothreads=True,
         foreground=True)


if __name__ == '__main__':

    # FIXME implement the possibility to get parameters via a config file
    parser = argparse.ArgumentParser(description='Vault fuse file system')

    parser.add_argument( '-c', '--config', dest='config', metavar='', required=False, help='Config file.')
    parser.add_argument( '-m', '--mountpoint', dest='mountpoint', metavar='',
        required=True, help='where the fuse filesystem will be mounted.')
    parser.add_argument( '-l', '--local', dest='local', metavar='', required=True,
                        help='credentials local path after being pulled from vault.')
    parser.add_argument( '-r', '--remote', dest='remote', metavar='', required=True, help='Vault Server HTTPS address.')
    parser.add_argument( '-s', '--secrets-path', dest='secrets_path', metavar='', required=True,
        action='append', help='List of secrets path in the Vault server.')
    parser.add_argument( '-p', '--payload', dest='payload', metavar='', required=True,
        help='List of secrets path in the Vault server.')

    args = parser.parse_args()

    # FIXME: Add some controls over mountpoint/local (should be a folder), remote should be reachable payload should exist
    mountpoint = args.mountpoint
    local = args.local
    remote = args.remote.rstrip('/')
    secrets_path = args.secrets_path
    payload = args.payload
    vaultfs(mountpoint, local, remote,  payload, secrets_path)
