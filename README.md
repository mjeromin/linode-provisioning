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
This is the common ansible playbook for all hosts that pull this repo via ansible-pull. At the very least, it will install a cronjob to ensure future ansible-pulls. For something more specific, ansible-pull allows yaml files named after the hostname (which will override local.yml).

### Trusted User CA Keys
Instead of installing public keys in each user's authorized_keys, Ansible will install a public CA key under `/etc/ssh/ca.pub`. Users can login using ssh keys signed by this. There is a great write-up on [this page](https://code.fb.com/security/scalable-and-secure-access-with-ssh/), but once you have created a CA key, add the public portion to **templates/ca.pub**. There are some trade-offs with manageability, ie.: securing the CA public key, expiration dates for key signatures and/or managing a revokation list, implementing secure signing workflows. But in return you will have a login management system that is easy to scale, easy to manage with a dynamic set of users that shrinks/grows unpredictably, and doesn't come with SPOF like LDAP and/or Kerberos.

#### Quick-Start: Creating a CA key
```
$ ssh-keygen -C CA -f ca
```
This sets up a certificate authority for signing certificates. You should have
two files, **ca** (the private key) and **ca.pub** (the public key). Make sure
to lock-down access to your **ca** file (ie. 0400 permissions, root ownership). 

#### Quick-Start: Signing a user key
```
$ ssh-keygen -s ca -I mjeromin -V +1w -z 1 id_rsa.pub
```
This command uses the private CA key stored in the **ca** file to sign the public portion of the user SSH keypair, **id_rsa.pub**. The certificate ID will be **mjeromin**. You can restrict the user accounts and machines this key is authorized to login to, take a look at [this page](https://code.fb.com/security/scalable-and-secure-access-with-ssh/). 

## provision_instances.py
Using Linode API v4, this script will provision VM instances based on YAML configuration found in a file named **config.yml** in the same directory. An example is included as filename **config.yml.example**.

## contrib/config-helper.sh
Using Linode API v4, this script will help list details of public images, instance types, and regions.
