import os

__version__ = '0.1.0'
__license__ = 'GPL2'
__author__ = 'Bernd Strebel'

PACKAGE_DIR = os.path.dirname(os.path.abspath(__file__))

from .session import OxHttpAPI
from .beans import OxBean
from .beans import OxBeans
from .folders import OxFolder
from .folders import OxFolders
from .tasks import OxTask
from .tasks import OxTasks
from .attachment import OxAttachment
from .attachment import OxAttachments
from .sync import OxTaskSync

__all__ = [

    'OxHttpAPI',
    'OxSync',
    'OxBean',
    'OxBeans',
    'OxFolder',
    'OxFolders',
    'OxTask',
    'OxTasks',
    'OxTaskSync',
    'OxAttachment',
    'OxAttachments'
]


