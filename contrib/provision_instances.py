#!/usr/bin/env python

DEBUG = 0
DEFAULT_CONFIG_FILE = 'config.yml'

import sys

try:
    from argparse import ArgumentParser
except ImportError:
    print("Please install argparse.")
    exit(1)

try:
    from yaml import load, dump, YAMLError
except ImportError:
    print("Please install PyYAML.")
    exit(1)

try:
    from linode_api4 import LinodeClient
    from linode_api4.objects.filtering import Filter
    from linode_api4.errors import ApiError, UnexpectedResponseError
except ImportError:
    print("Please install linode-api4.")
    exit(1)

def parse_args(args):
    """Parse a list of command-line args via argparse and return them in dict format."""

    parser = ArgumentParser(description='Provision VM instances based on YAML configuration.')
    parser.add_argument('--config',
                        dest='config_file',
                        default=DEFAULT_CONFIG_FILE,
                        help='specify YAML configuration filename. DEFAULT=config.yml'
                       )
    return vars(parser.parse_args(args))

def load_config(config_file):
    """Readin config_file, load YAML into dictionary, then return config dict. """

    try:
        with open(config_file, 'r') as f:
            try:
                config = load(f)
            except YAMLError as exc:
                print("{}".format(exc))
                exit(1)
    except IOError:
        print("Could not read configuration file: {}", format(config_file))
        exit(1)

    # Configuration requirements
    required_config_keys = ['virtual_machines',
                            'stackscript_label',
                            'api_token',
                            'git_repo',
                            'git_branch',
                            'git_access_key64',
                            'vault_password'
                            ]
    for key in required_config_keys:
        if key not in list(config.keys()):
            print("ERROR: Missing config key: {}".format(key))
            exit(1)

    return config

def get_stackscript(label, client):
    """Check that stackscript exists in Linode, then return stackscript object."""

    username = label.split('/')[0]
    basename = label.split('/')[1]
    username_filter = Filter({'username': username})
    stackscript = None
    stackscripts = client.linode.stackscripts(username_filter)
    if len(stackscripts) == 0:
        print("ERROR: no filtered stackscripts found")
        exit(1)
    
    for ss in stackscripts:
        if ss.label == basename:
            stackscript = ss
            break
    
    if not stackscript:
        print("ERROR: no appropriate stackscript found")
        exit(1)

    return(stackscript)

#  we don't care about sysargv[0], the invoked command name
args = parse_args(sys.argv[1:])
config = load_config(args['config_file'])
client = LinodeClient(config['api_token'])
stackscript = get_stackscript(config['stackscript_label'], client)

for vm in config['virtual_machines']:
    # Instance_create() returns the newly-created Instance object and the root
    # password that was generated for it. This Instance will boot automatically,
    # and should be available shortly.
    try:
        new_linode, password = client.linode.instance_create(
                                    vm['size'],
                                    vm['region'],
                                    vm['image'],
                                    stackscript=stackscript,
                                    stackscript_data={
                                        "GIT_REPO": config['git_repo'],
                                        "GIT_BRANCH": config['git_branch'],
                                        "GIT_ACCESS_KEY64": config['git_access_key64'],
                                        "VAULT_PASSWORD": config['vault_password']
                                    }
                                )
    except (ApiError, UnexpectedResponseError) as exc: 
        print("{}".format(exc))
    else:
        if DEBUG == 1:
            print("ssh root@{} - {} [id: {}]".format(new_linode.ipv4[0], password, new_linode.label))
        else:
            print("ssh root@{} [id: {}]".format(new_linode.ipv4[0], new_linode.label))

my_linodes = client.linode.instances()
print("Current instances: {}".format(len(my_linodes)))
for my_linode in my_linodes:
    print("- {}".format(my_linode.label))

exit(0)
