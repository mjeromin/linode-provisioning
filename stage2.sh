#!/usr/bin/env bash

for i in "$@"
do
case $i in
    id=*)
    LINODE_ID="${i#*=}"
    ;;
    git_repo=*)
    GIT_REPO="${i#*=}"
    ;;
    git_branch=*)
    GIT_BRANCH="${i#*=}"
    ;;
    *)
    :       # unknown option
    ;;
esac
done

if [[ -z "$GIT_REPO" ]] || [[ -z "$GIT_BRANCH" ]]; then
    echo "USAGE: $0 git_repo=<git_repo_url> git_branch=<branch_name> [id=<linode_id>]"
    exit 1
fi

# stash parameters as Ansible facts
mkdir -p /etc/ansible/facts.d
cat > /etc/ansible/facts.d/bootstrap.fact << EOF
{
    "LINODE_ID": "$LINODE_ID",
    "ANSIBLE_GIT_REPO" : "$GIT_REPO",
    "ANSIBLE_GIT_BRANCH" : "$GIT_BRANCH"
}
EOF

# install ansible (note: ansible 2.5+ supports python 3.5+)
yum install -y libselinux-python
pip3 install --upgrade pip
/usr/local/bin/pip3 install ansible==2.5.10  # full pip3 path needed after upgrade

# run ansible bootstrap playbook
mkdir /var/lib/ansible/local
if [ -r /root/.vault_pass ]; then
    ansible-pull --vault-password-file=/root/.vault_pass \
                 --checkout=${GIT_BRANCH} \
                 -d /var/lib/ansible/local \
                 -i localhost, \
                 -U $GIT_REPO
else
    ansible-pull --checkout=${GIT_BRANCH} \
                 -d /var/lib/ansible/local \
                 -i localhost, \
                 -U $GIT_REPO
fi

exit 0
