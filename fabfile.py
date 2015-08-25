from fabric.api import *
from fabric.contrib.project import rsync_project
from fabric.contrib.files import exists as path_exists
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
    dest_env = 'test'
    source_env = 'local'
    backup(source_env)
    backup(dest_env)
    sync_temp(dest_env, source_env)
    sync_from_temp(dest_env)


def deploy():
    """
        push everything into repository from production machine,
        copy everything to production machine from test machine,
        pull everything from repository to production machine.
        import database.
    """
    dest_env = 'deploy'
    source_env = 'test'
    backup(source_env)
    backup(dest_env)
    sync_temp(dest_env, source_env)
    sync_from_temp(dest_env)
    db_import(dest_env)


def get_files(env_name):
    localpath = os.path.join(ENVS['local']['workspace'])
    remotepath = os.path.join(ENVS[env_name]['workspace'],'wp-content')
    set_env(env_name)
    get(remotepath,localpath)


def sync_temp(env_name, from_branch):
    """
        synchronize from given repository.
    """
    assert 'tempspace' in ENVS[env_name], "tempspace does not exist."
    assert 'git_branch' in ENVS[env_name], "git_branch does not exist."
    set_env(env_name)
    cmd_mkdir = "mkdir -p %s" % ENVS[env_name]['tempspace']
    cmd_clone = "git clone %s . -b %s" % (ENVS['project'][
        'repository'], from_branch)
    commands = []
    commands.append('git checkout %s' % from_branch)
    commands.append('git reset --hard HEAD')
    commands.append('git clean -dfx')
    commands.append('git pull origin %s' % from_branch)
    if env_name == 'local':
        if not os.direxists(ENVS[env_name]['tempspace']):
            local(cmd_mkdir)
            with lcd(ENVS[env_name]['tempspace']):
                local(cmd_clone)
        with lcd(ENVS[env_name]['tempspace']):
            for cmd in commands:
                local(cmd)
    else:
        if not path_exists(ENVS[env_name]['tempspace']):
            run(cmd_mkdir)
            with cd(ENVS[env_name]['tempspace']):
                run(cmd_clone)
        with cd(ENVS[env_name]['tempspace']):
            for cmd in commands:
                run(cmd)


def sync_from_temp(env_name):
    """
        synchronize to server from tempory directory.
    """
    assert 'tempspace' in ENVS[env_name], "tempspace does not exist."
    assert 'workspace' in ENVS[env_name], "workspace does not exist."
    set_env(env_name)
    source_path = os.path.join(
        ENVS[env_name]['tempspace'], ENVS[env_name]['sync_dir'])+'/'
    destin_path = os.path.join(
        ENVS[env_name]['workspace'], ENVS[env_name]['sync_dir'])+'/'
    cache_path = os.path.join(
        ENVS[env_name]['workspace'], ENVS[env_name]['sync_dir'],'cache')
    commands = []
    commands.append('rsync -avzrtW --delete --exclude "cache" %s %s' %
                    (source_path, destin_path))
    commands.append('chmod 777 %s -R' % cache_path)

    if env_name == 'local':
        for cmd in commands:
            local(cmd)
    else:
        for cmd in commands:
            run(cmd)


def db_import(env_name):
    """
        database import from file
    """
    set_env(env_name)
    commands = []
    commands.append('wp db import %s' % ENVS[env_name]['dump_file'])
    for pattern in ENVS[env_name]['replace_pattern']:
        commands.append('wp search-replace %s %s' %
                        (pattern, ENVS[env_name]['replace']))
    if env_name == 'local':
        with lcd(ENVS[env_name]['workspace']):
            for cmd in commands:
                local(cmd)
    else:
        with cd(ENVS[env_name]['workspace']):
            for cmd in commands:
                run(cmd)


def db_export(env_name):
    """
        database export to file
    """
    set_env(env_name)
    commands = []
    commands.append('wp db export %s' % ENVS[env_name]['dump_file'])
    if env_name == 'local':
        with lcd(ENVS[env_name]['workspace']):
            for cmd in commands:
                local(cmd)
    else:
        with cd(ENVS[env_name]['workspace']):
            for cmd in commands:
                run(cmd)


def pull(env_name):
    """
        pull from last check point.
    """
    set_env(env_name)
    assert 'workspace' in ENVS[env_name], "workspace does not exist."
    assert 'git_branch' in ENVS[env_name], "git_branch does not exist."
    assert 'dump_file' in ENVS[env_name], "dump_file does not exist."
    commands = []

    commands.append('git checkout %s' % ENVS[env_name]['git_branch'])
    commands.append('git reset --hard HEAD')
    commands.append('git clean -dfx')
    commands.append('git pull origin %s' % ENVS[env_name]['git_branch'])
    if env_name == 'local':
        with lcd(ENVS[env_name]['workspace']):
            for cmd in commands:
                local(cmd)
    else:
        with cd(ENVS[env_name]['workspace']):
            for cmd in commands:
                run(cmd)


def push(env_name):
    """
        push everything to repository.
    """
    set_env(env_name)
    assert 'workspace' in ENVS[env_name], "workspace does not exist."
    assert 'git_branch' in ENVS[env_name], "git_branch does not exist."
    assert 'dump_file' in ENVS[env_name], "dump_file does not exist."
    commands = []
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


def backup(env_name):
    """
        backup everything to repository.
    """
    db_export(env_name)
    push(env_name)


def rollback(env_name):
    """
        rollback to last check point.
    """
    pull(env_name)
    db_import(env_name)


def update():
    """
        Update the default OS installation's
        basic default tools.
    """
    sudo("aptitude    update")
    sudo("aptitude -y upgrade")


def get_current_datetime():
    return datetime.datetime.now().strftime("%I:%M%p on %B %d, %Y")
