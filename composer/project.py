#(c) Máximo Cuadros <maximo@yunait.com>
#
# This source file is subject to the MIT license that is bundled
# with this source code in the file LICENSE.

from fabric.api import *
from fabric.contrib import files
from fabric.colors import red, green
import time

class Project:
    version = time.strftime('%Y-%m-%dT%H%M%S')
    config = None
    name = None

    def __init__(self, name, config):
        self.config = config
        self.name = name

    def prepare(self):
        with hide('output'):
            self.__create_local_paths()
            self.__install_composer_local()
            self.__fetch()

    def __create_local_paths(self):
        local('mkdir -p %s' % (self.config['local_workspace_path']))

    def __create_remote_paths(self):
        run('mkdir -p %s' % (self.config['remote_workspace_path']))

    def __install_composer_local(self):
        local(self.__get_composer_installer_command() % (self.config['local_workspace_path']))

    def __install_composer_remote(self):
        run(self.__get_composer_installer_command() % (self.config['remote_workspace_path']))

    def __get_composer_installer_command(self):
        return 'curl -sS https://getcomposer.org/installer | php -- --install-dir=%s' 

    def __fetch(self):
        self.__git_clone()
        self.__composer_install()
        self.__execute_post_install_commands()
        self.__tar_code()
                
    def __git_clone(self):
        local('git clone --depth 1 %s %s' % (self.config['repository'], self.__get_local_workspace_path()))

    def __composer_install(self):
        with lcd(self.__get_local_workspace_path()):
            local('%scomposer.phar install %s' % (self.config['local_workspace_path'], self.config['composer_params']))

    def __execute_post_install_commands(self):
        with lcd(self.__get_local_workspace_path()):
            for command in self.config['post_install_commands']:
                local(command)

    def __tar_code(self, version=None):
        with lcd(self.__get_local_workspace_path()):
            local('tar czf %s.tar.gz .' % self.__get_version(version))

    def deploy(self):
        version = self.__get_version()
        print(green('Deploying %s version to server' % (version)))
        
        with hide('output'):
            self.__create_remote_paths()
            self.__install_composer_remote()
            self.__upload_deploy_file(version)
            self.__untar_code(version)
            self.__validate_deploy()
            self.__link_code(version)

    def __upload_deploy_file(self, version):
        target = self.__get_remote_workspace_path(version)
       
        run('mkdir -p %s' % (target))
        put(self.__get_deploy_file(), target)

    def __untar_code(self, version=None):
        with cd(self.__get_remote_workspace_path(version)):
            run('tar xzf %s.tar.gz' % self.__get_version(version))

    def __validate_deploy(self, version=None):
        with cd(self.__get_remote_workspace_path(version)):
            run('%scomposer.phar update --dry-run %s' % (self.config['remote_workspace_path'], self.config['composer_params']))

    def __link_code(self, version):
        if files.exists(self.config['deploy_path']):
            run('unlink %s' % (self.config['deploy_path']))

        run('ln -s %s %s' % (self.__get_remote_workspace_path(version), self.config['deploy_path']))

    def __get_deploy_file(self, version=None):
        version = self.__get_version(version)
        return '%s%s/%s/%s.tar' % (self.config['local_workspace_path'], self.name, version, version)

    def __get_local_workspace_path(self, version=None):
        return '%s%s/%s' % (self.config['local_workspace_path'], self.name, self.__get_version(version))
    
    def __get_remote_workspace_path(self, version=None):
        return '%s%s/%s' % (self.config['remote_workspace_path'], self.name, self.__get_version(version))

    def __get_version(self, version=None):
        if version == None:
            version = self.version

        return version

    def info(self):
        self.prepare()

        with hide('output'):
            php_version = run('php -v | head -n 1')
            composer_version = run('%scomposer.phar --version | head -n 1' % (self.config['remote_workspace_path']))
            md5_composer_lock = run('md5sum ' + self.config['deploy_path'] + '/composer.lock').split(' ')[0]

        print('%s: %s' % (green('PHP Version'), php_version))
        print('%s: %s' % (green('Composer Version'), composer_version))
        print('%s: %s' % (green('Composer Lock'), md5_composer_lock))