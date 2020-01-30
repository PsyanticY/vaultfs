# vaultfs
Hashicorp Vault fuse filesystem

The intent for this package is to get secrets from the vault server if the secret is not found in the local path.

## Setup

```bash
git clone 
cd vaultfs
sudo python3.6 setup.py install
```

## Usage

```bash
usage: vaultfs.py [-h] [-c] [-m] [-l] [-r] [-s] [-p]

Vault fuse file system

optional arguments:
  -h, --help            show this help message and exit
  -c , --config         Configuration file.
  -m , --mountpoint     where the fuse filesystem will be mounted.
  -l , --local          credentials local path after being pulled from vault.
  -r , --remote         Vault Server HTTPS address.
  -s , --secrets-path   List of secrets path in the Vault server.
  -p , --payload        .Vault authentication token

Note: arguments: "--mountpoint", "--local", "--remote", "--secetes-path" and "--payload" are required when "--config" is missing
```

*This is a WIP*

*THis is what we want to implement*

- This module requires a mountpoint,a local path and the remote url of the hashicorp vault

- It will also requires a:
  * Token (`payload`) that will allow `vaultfs` to authenticate requests made to the vault 
  * List of secret engines from where secrets will be fetched ( this requires that the token has enought permissions to access those ).
  * data_key: Given that the vault will store secrets in KV2 (currently kv will not be supported) backend, we need to specify the key where the secrets are stored.
  

the system/human will expect files to be in the mountpoint, `vaultfs` will first fetch them from the vault and copy them to the local path, hitherto the system/programs/human can find the file in the expected destination.

TODO:
- Make sure the mount point is empty before mounting the system/move file to th cache if possible. (this can currently be done by a prescript in the systemd unit)
- Make sure the program checks vault for existing file for new version. (use hashlib) (no we are using timestamps for that)
- Hardin the logging. \[done\]
- Implement rotating token and generating them from a role id. (No for the moment at least) (this wil ladd complexity beyond the scope of the package)
- Implement getting configs from a file (that we may put in /etc/) \[done\]
- Change the look with list call and search
- Explore how to remove the cache entirely (nah, let's just implement a correct caching mecanism)
### Notes

Using a non Empty folder as the mountpoint fail with this error: 
```bash
fuse: mountpoint is not empty
fuse: if you are sure this is safe, use the 'nonempty' mount option
```
As mentioned in the error message to work aroud this we need to add `nonempty=True` as a FUSE function parameter.==> Mounting to a nomempty folder cause the files in there to desappear so it makes sense to copy them somewhere else (best is in local cache)

## testing
 use python3.6 for no since some issues happen with 3.7.
```bash
python3.6 vaultfs/vaultfs.py --config config/vaultfs.cfg
```

## Docker

The Dockerfile facilitates mounting of remote vaults into the local filesystem
or other Docker containers. The image implements a Docker volume on the cheap:
Used with proper  creation options (see below) , you should be able to
bind-mount back the vault onto a host directory. This directory will
make the content of the vault available to processes, but also all other
containers on the host.

Provided the existence of a directory called `/mnt/vault` on the host, a file
called `auth.tkn` in the current directory and that you have built the image
`vaultfs`, the following command would mount a remote vault, and bind-mount the
remote vault onto the host's `/mnt/vault` in a way that makes the remote secrets
accessible to processes and/or other containers running on the same host.

```shell
docker run -it --rm \
    --device /dev/fuse \
    --cap-add SYS_ADMIN \
    --security-opt "apparmor=unconfined" \
    -v $(pwd)/auth.tkn:/data/auth.tkn:ro \
    -v /mnt/vault:/vault:rshared \
    vaultfs \
    -r https://your.remote.vault/ \
    -s secrets \
    -p /data/auth.tkn
```

The `--device`, `--cap-add` and `--security-opt` options and their values are to
make sure that the container will be able to make available the vault using
FUSE. `rshared` is what ensures that bind mounting makes the files and
directories available back to the host and recursively to other containers.
