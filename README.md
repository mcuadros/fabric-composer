fabric-composer
===============

fabric-composer is a basic generic deploy system for all PHP projects ussing [Composer](https://getcomposer.org/) 
made with python library, [Fabric](http://docs.fabfile.org/).


Requirements
------------

* python >= 2.5 
* Unix system;
* fabric
* pyyaml


Installation and usage
--------------------

Download the code from github

```sh
wget https://github.com/mcuadros/fabric-composer/archive/master.zip
unzip master.zip
```

Setup the config.yaml file, you can just copy the example file or create a new one

```sh
cd fabric-composer-master
cp config.yaml.example config.yaml
```

Now you are read to made the deploy ussing fab bin
```sh
fab deploy:example
```

The list of command available is:
* ```fab deploy:<project_name> ```
This lauch the deploy and all hosts

* ```fab info:<project_name> ```
Prints the some PHP and Composer related info from each server 

Configuration
--------------

The config file, called config.yaml, contains all the configuration needed to make the deploy of a project, as much as you want 
you can define project configurations in the same config file

All the properties are mandatory

```yaml
example: # project name
    user: johndoe # username used by the SSH layer when connecting to remote hosts
    hosts: # host list where the deploy will be do it
        - www-1.example.com
        - www-2.example.com
    deploy_path: /var/www/sonata # path where all files will be copied
    remote_workspace_path: /home/johndoe/deploy/ # workspace in remote server
    local_workspace_path: /tmp/ # workspace in local server
    repository: git@github.com:sonata-project/sandbox.git # git repository
    composer_params: --no-dev --optimize-autoloader --no-interaction # optional composer commands
    post_install_commands: [] # commands to be executed at the end of composer install in local server
```

Deploy strategy
---------------

The deploy is made as follow:

1. [local] git clone from project repository
2. [local] composer install 
3. [local] execution of post_install_commands (optional)
4. [local] the code is compressed 
5. [remote] compressed code is delivered to every remote server
6. [remote] the code is compressed
7. [remote] composer update with --dry-run, this cmd validate the code 
8. [remote] a ln is made from the workspace path to the deploy path

License
-------

MIT, see [LICENSE](LICENSE)

