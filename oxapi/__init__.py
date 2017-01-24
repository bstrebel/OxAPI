import os

__version__ = '0.5.8'
__license__ = 'GPL2'
__author__ = 'Bernd Strebel'

PACKAGE_DIR = os.path.dirname(os.path.abspath(__file__))

from .session import OxHttpAPI
from .beans import OxBean, OxBeans
from .folders import OxFolder, OxFolders
from .tasks import OxTask, OxTasks
from .attachment import OxAttachment, OxAttachments
from .export import OxExport
from .config import OxConfig

__all__ = [

    'OxHttpAPI',
    'OxBean',
    'OxBeans',
    'OxFolder',
    'OxFolders',
    'OxTask',
    'OxTasks',
    'OxAttachment',
    'OxExport',
    'OxConfig',
    'OxAttachments'
]


