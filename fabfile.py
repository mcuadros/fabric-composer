#(c) Maximo Cuadros <maximo@yunait.com>
#
# This source file is subject to the MIT license that is bundled
# with this source code in the file LICENSE.

from fabric.api import *
from composer.manager import manager

manager.load_project_config('config.yaml')
manager.prepare_all()

def info(role):
    manager.info(role)

@parallel
def deploy(role):
    manager.deploy(role)