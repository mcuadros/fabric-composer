#(c) Maximo Cuadros <maximo@yunait.com>
#
# This source file is subject to the MIT license that is bundled
# with this source code in the file LICENSE.
 
from fabric.colors import red, green
from project import *
import sys
import yaml


class Manager:
    config = {}
    instances = {}

    cmd_needs_prepare = ['deploy']

    def load_project_config(self, filename):
        config_file = open(filename)

        self.config = yaml.safe_load(config_file)
        config_file.close()

    def add_project_config(self, role, config):
        self.config[role] = config

    def prepare_all(self):
        if self.__needs_be_prepared() == False:
            return

        for role in self.__get_roles_from_tasks():
            self.prepare(role)

    def prepare(self, role):
        print(green('Creating deploy files for %s' % (role)))

        self.__get_project(role).prepare()

        self.__set_env_hosts(self.config[role]['hosts'])
        self.__set_env_user(self.config[role]['user'])

    def deploy(self, role):
        print(green('Deploying %s' % (role)))
        self.__get_project(role).deploy()

    def info(self, role):
        self.__get_project(role).info()


    def __set_env_user(self, user):
        env.user = user

    def __set_env_hosts(self, hosts):
        env.hosts = hosts

    def __has_project(self, role):
        return self.config.has_key(role)

    def __get_project(self, role):
        if self.__has_project(role) == False:
            sys.stderr.write(red('Unable to find a project called "%s" \n' % (role)))
            sys.exit()

        if self.instances.has_key(role) == False:
            self.instances[role] = Project(role, self.config[role])

        return self.instances[role]

    def __get_roles_from_tasks(self):
        roles = []
        for task in env.tasks:
            roles.append(task.split(':')[1]) 

        return roles

    def __needs_be_prepared(self):
        roles = []
        for task in env.tasks:
            if task.split(':')[0] in self.cmd_needs_prepare:
                return True
            

        return False

manager = Manager()