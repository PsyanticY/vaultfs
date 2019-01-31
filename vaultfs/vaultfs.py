import argparse
import sys
from fuse import FUSE
from logger import VaultfsLogger
# import vaultfs
# from vaultfs.vault_fuse import vault_fuse
# from vaultfs.vault_api import check_remote, check_local
from configparser import ConfigParser, NoOptionError
from vault_fuse import vault_fuse
from vault_api import check_remote, check_folder, check_file

# setting logger.
log = VaultfsLogger()

def vaultfs(mountpoint, local, remote, payload, secrets_path):
    FUSE(vault_fuse(local, remote, payload, secrets_path), mountpoint, nothreads=True,
         foreground=True)

def main():
    # FIXME: add a timeout parameter
    # FIXME: add a data_content parameter 
    
    parser = argparse.ArgumentParser(
        description='Vault fuse file system',
        epilog='Note: arguments: "--mountpoint", "--local", "--remote", "--secetes-path" and "--payload" are required when "--config" is missing')

    parser.add_argument( '-c', '--config', dest='config', metavar='', required=False, help='Configuration file.')
    parser.add_argument( '-m', '--mountpoint', dest='mountpoint', metavar='',
        required=False, help='where the fuse filesystem will be mounted.')
    parser.add_argument( '-l', '--local', dest='local', metavar='', required=False,
                        help='credentials local path after being pulled from vault.')
    parser.add_argument( '-r', '--remote', dest='remote', metavar='', required=False, help='Vault Server HTTPS address.')
    parser.add_argument( '-s', '--secrets-path', dest='secrets_path', metavar='', required=False,
        action='append', help='List of secrets path in the Vault server.')
    parser.add_argument( '-p', '--payload', dest='payload', metavar='', required=False,
        help='.Vault authentication token')

    args = parser.parse_args()
    if not args.config and (args.mountpoint is None or args.local is None or args.payload is None or args.remote is None or args.secrets_path is None):
        parser.error('arguments: "--mountpoint", "--local", "--remote", "--secetes-path" and "--payload" are required when "--config" is missing')
    
    config_file = ConfigParser()
    if args.config:
        check_file(args.config)
        try:
            config_file.read(args.config)
        except Exception as e:
            log.error(e)

        if not config_file.has_section("main"):
            log.error("Section 'main' was not found in the config file")
            sys.exit(1)

        if args.local:
            local = args.local
        else:
            local = config_file.get("main", 'local', fallback="/run/vault-keys")

        if args.mountpoint:
            mountpoint = args.mountpoint
        else:
            mountpoint = config_file.get("main", 'mountpoint', fallback="/run/keys")

        if args.remote:
            remote = args.remote.rstrip('/')
        else:
            try:
                remote = config_file.get("main", "remote").rstrip('/')
            except NoOptionError as e:
                log.error(e)
                sys.exit(1)

        if args.payload:
            payload = args.payload
        else:
            try:
                payload = config_file.get("main", "payload")
            except NoOptionError as e:
                log.error(e)
                sys.exit(1)

        if args.secrets_path:
            secrets_path = args.secrets_path
        else:
            try:
                secrets_path = config_file.get("main", "secrets_path")
            except NoOptionError as e:
                log.error(e)
                sys.exit(1)

    else:
        mountpoint = args.mountpoint
        local = args.local
        remote = args.remote.rstrip('/')
        secrets_path = args.secrets_path
        payload = args.payload

    # initial checks
    check_remote(remote)
    check_folder(local)
    check_folder(mountpoint)
    check_file(payload)
    print("success")
    
    vaultfs(mountpoint, local, remote,  payload, secrets_path)


if __name__ == '__main__':

    main()
