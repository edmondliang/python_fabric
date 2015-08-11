from fabric.api import *
import json
import sys
import os
import datetime


current_path = os.path.dirname(os.path.realpath(__file__))
setting_file = os.path.join(current_path, "setting.json")
ENVS = None
if os.path.isfile(setting_file):
    ENVS = json.loads(open(setting_file).read())
else:
    print """
            Setting file does not exist!
            Please create setting.json according readme.me then to continue!
        """
    sys.exit(0)


def set_env(env_name):
    """
        Set enviroment
    """

    assert env_name in ENVS, "Environment does not exist."
    # for k, v in ENVS[env_name]["env"].iteritems():
    #     setattr(env, k, v)
    env.host = ENVS[env_name]["env"]["host"]
    env.host_string = ENVS[env_name]["env"]["host"]
    env.user = ENVS[env_name]["env"]["user"]
    env.password = ENVS[env_name]["env"]["password"]


def test():
    """
        push everything into repository from test machine,
        copy everything to test machine from local machine,
        pull everything from repository to test server.
    """
    env_name = 'deploy'
    backup(env_name)
    # pull('test')


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


def rollback(env_name):
    """
        rollback to last check point.
    """
    set_env(env_name)
    assert 'workspace' in ENVS[env_name], "workspace does not exist."
    assert 'git_branch' in ENVS[env_name], "git_branch does not exist."
    commands = []
    commands.append('git checkout .')
    commands.append('wp db import dump.sql')
    if env_name == 'local':
        with lcd(ENVS[env_name]['workspace']):
            for cmd in commands:
                local(cmd)
    else:
        with cd(ENVS[env_name]['workspace']):
            for cmd in commands:
                run(cmd)


def backup(env_name):
    """
        push everything to repository.
    """
    set_env(env_name)
    assert 'workspace' in ENVS[env_name], "workspace does not exist."
    assert 'git_branch' in ENVS[env_name], "git_branch does not exist."
    commands = []
    commands.append('wp db export dump.sql')
    commands.append('git add -A')
    commands.append('git commit -m "backup at %s"' % get_current_datetime())
    commands.append('git push origin %s' % ENVS[env_name]['git_branch'])
    if env_name == 'local':
        with lcd(ENVS[env_name]['workspace']):
            for cmd in commands:
                local(cmd)
    else:
        with cd(ENVS[env_name]['workspace']):
            for cmd in commands:
                run(cmd)


def update():
    """
        Update the default OS installation's
        basic default tools.
    """
    sudo("aptitude    update")
    sudo("aptitude -y upgrade")


def get_current_datetime():
    return datetime.datetime.now().strftime("%I:%M%p on %B %d, %Y")
