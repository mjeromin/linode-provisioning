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
This is the second stage bootstrap script, intended to setup configuration management. It will accept three parameters (`GIT_REPO`, `GIT_BRANCH`, `LINODE_ID`), install ansible, and kick off ansible-pull. 

## local.yml
This is the common ansible playbook for all hosts that pull this repo via ansible-pull. At the very least, it will configure SSH and install a cronjob to ensure future ansible-pulls. For something more specific, ansible-pull allows yaml files named after the hostname (which will override local.yml).

### Trusted User CA Keys
Instead of installing public keys in each user's authorized_keys, local.yml will install a public CA key under `/etc/ssh/ca.pub`. Users can login using ssh keys that are signed by this CA. There are great write-ups on [this page](https://code.fb.com/security/scalable-and-secure-access-with-ssh/) and [this page](https://medium.com/uber-security-privacy/introducing-the-uber-ssh-certificate-authority-4f840839c5cc), but once you have created a CA key, add the public portion to your **templates/ca.pub**.

#### Quick-Start: Creating a CA key
```
$ ssh-keygen -C CA -f ca
```
This sets up a certificate authority for signing certificates. You should have
two files, **ca** (the private key) and **ca.pub** (the public key). Make sure
to lock-down access to your **ca** file (ie. 0400 permissions, root ownership). 

#### Quick-Start: Signing a user key
```
$ ssh-keygen -s ca -I mjeromin -V +1w -z 1 -n root,mjeromin id_rsa.pub
```
This command uses the private CA key stored in the **ca** file to sign the public portion of the user SSH keypair, **id_rsa.pub**. The certificate ID will be **mjeromin** (named after the user ID), the signature is valid for 1 week, the signature serial number is "1", and the certificate is valid for login to usernames (aka. principals): root and mjeromin -- assuming principals have been enabled in **sshd_config**. There are other ways we can apply restrictions on the usage of signed keys, take a look at [this page](https://code.fb.com/security/scalable-and-secure-access-with-ssh/) or the [man page](https://www.freebsd.org/cgi/man.cgi?query=ssh-keygen&sektion=1&manpath=OpenBSD). 

## provision_instances.py
Using Linode API v4, this script will provision VM instances based on YAML configuration found in a file named **config.yml** in the same directory. An example is included as filename **config.yml.example**. However, you can use a different filename for your configuration. For example:
```
./provision_instances.py --config dev.yml
ssh root@xx.xxx.xx.xx [id: linodexxxxxxxx]
Current instances: 1
- linodexxxxxxxx
```

## contrib/config-helper.sh
Using Linode API v4, this script will help list details of public images, instance types, and regions.
```
contrib/config-helper.sh [images|sizes|regions]

images: prints a list of public images.
sizes: prints a collection of Linode Types, including pricing and specifications.
regions: prints the regions available for Linode services.
```
