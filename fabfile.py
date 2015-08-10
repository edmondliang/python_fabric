from fabric.api import *
import json
import sys
import os


current_path = os.path.dirname(os.path.realpath(__file__))
setting_file = os.path.join(current_path, "setting.json")
ENVS = None
if os.path.isfile(setting_file):
    ENVS = json.loads(open(setting_file).read())
else:
    print """
            Setting file does not exist!
            Please configure one according readme.me then to continue!
        """
    sys.exit(0)


def _set_env(env_name):
    """
        Set enviroment
    """
    assert env_name in ENVS, "Environment does not exist."
    for k, v in ENVS[env_name]["env"].iteritems():
        setattr(env, k, v)


def test():
    """
        push everything into repository from test machine,
        copy everything to test machine from local machine,
        pull everything from repository to test server.
    """
    pass


def deploy():
    """
        push everything into repository from production machine,
        copy everything to production machine from test machine,
        pull everything from repository to production machine.
    """
    pass


def copy():
    """
        copy everything from a machine to b machine.
    """
    pass


def rollback():
    """
        rollback to last check point.
    """
    pass


def pull():
    """
        pull everything from repository.
    """
    pass


def push():
    """
        push everything to repository.
    """
    pass


def update():
    """
        Update the default OS installation's
        basic default tools.
    """
    run("aptitude    update")
    run("aptitude -y upgrade")
