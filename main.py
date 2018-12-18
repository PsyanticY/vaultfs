import argparse
from fuse import FUSE
from Vault_fuse import Vault_fuse

def vaultfs(mountpoint, local, remote, secrets_path, payload):
    FUSE(Vault_fuse(local, remote, secrets_path, payload), mountpoint, nothreads=True,
         foreground=True)


if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='Vault fuse file system')

    parser.add_argument( '-m', '--mountpoint', dest='mountpoint', metavar='',
        required=True, default='/run/keys', help='where the fuse filesystem will be mounted.')
    parser.add_argument( '-l', '--local', dest='local', metavar='', required=True,
        default='/run/imported-keys', help='credentials local path after being pulled from vault.')
    parser.add_argument( '-r', '--remote', dest='remote', metavar='', required=True,
        default='https://susanoo.vault.com:8200', help='Vault Server HTTPS address.')
    parser.add_argument( '-s', '--secrets-path', dest='secrets_path', metavar='', required=True,
        action='append', help='List of secrets path in the Vault server.')
    parser.add_argument( '-p', '--payload', dest='payload', metavar='', required=True,
        help='List of secrets path in the Vault server.')

    args = parser.parse_args()

    mountpoint = args.mountpoint
    local = args.local
    remote = args.remote
    secrets_path = args.secrets_path
    payload = args.payload

    vaultfs(mountpoint, local, remote, secrets_path, payload)
