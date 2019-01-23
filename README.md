# vaultfs
Hashicorp Vault fuse filesystem

*This is a WIP*

*THis is what we want to implement*

This module requires a mountpoint,a local path and a remote url of the vault

It will also requires a:
* Token (`payload`) that will allow `vaultfs` to authenticate requests made to the vault 
* List of secret engines from where secrets will be fetched ( this requires that the token has enought permissions to access those ).
* data_key: Given that the vault will store secrets in KV2 (currently kv will not be supported) backend, we need to specify the key where the secrets are stored.

The intent for this package is to get secrets from the vault server if the secret is not found in the local path.

Programms or human will expect files to be in the mountpoint, `vaultfs` will first fetch them from the vault and copy them to the local path, hitherto the system/programs/human can find the file in the expected destination.

TODO:
MAke sure the program checks vault for existing file for new version.
Hardin the logging
Implement rotating token and generating them from a role id. (maybe ?)
