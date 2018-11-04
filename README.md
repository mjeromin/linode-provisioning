# linode-provisioning
A collection of scripts for standing up [Linode](https://www.linode.com/) infra.

## stage1.stackscript
This script is meant to be submitted as a [StackScript](https://www.linode.com/stackscripts) on the Linode platform. It takes the following parameters:
* `GIT_REPO`: The git repository where second stage scripts can be pulled.
* `GIT_BRANCH`: The git repository branch where second stage scripts can be pulled.
* `GIT_ACCESS_KEY64`: A base64 encoded RSA private key to download the git repo.
* `VAULT_PASSWORD` : The password that can be used to decrypt vault files (ie. ansible-vault)

It will download the private git repo and then execute a second stage script within the repo named "stage2.sh".  It is assumed that subsequent changes will be delegated to configuration management (ie. ansible, puppet, chef, etc.).

## stage2.sh
This is the second stage bootstrap script, intended to setup configuration management.
