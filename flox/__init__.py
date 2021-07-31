import sys
import os

from .flox import Flox
from .launcher import Launcher

PLUGIN_MANIFEST = 'plugin.json'

potential_paths = [
    os.path.abspath(os.getcwd()),
    os.path.dirname(os.path.abspath(os.path.dirname(__file__)))
]

for path in potential_paths:

    while True:
        if os.path.exists(os.path.join(path, PLUGIN_MANIFEST)):
            plugindir = path
            break
        elif path == '/':
            break

        path = os.path.dirname(path)

    if plugindir:
        break

lib_path = os.path.join(plugindir, 'lib')
if os.path.exists(lib_path):
    sys.path.append(lib_path)


from .flox import (
    ICON_APP,
    ICON_APP_ERROR,
    ICON_BROWSER,
    ICON_CALCULATOR,
    ICON_CANCEL,
    ICON_CLOSE,
    ICON_CMD,
    ICON_COLOR,
    ICON_CONTROL_PANEL,
    ICON_COPY,
    ICON_DELETE_FILE_FOLDER,
    ICON_DISABLE,
    ICON_DOWN,
    ICON_EXE,
    ICON_FILE,
    ICON_FIND,
    ICON_FOLDER,
    ICON_HISTORY,
    ICON_IMAGE,
    ICON_LOCK,
    ICON_LOGOFF,
    ICON_OK,
    ICON_OPEN,
    ICON_PICTURES,
    ICON_PLUGIN,
    ICON_PROGRAM,
    ICON_RECYCLEBIN,
    ICON_RESTART,
    ICON_SEARCH,
    ICON_SETTINGS,
    ICON_SHELL,
    ICON_SHUTDOWN,
    ICON_SLEEP,
    ICON_UP,
    ICON_UPDATE,
    ICON_URL,
    ICON_USER,
    ICON_WARNING,
    ICON_WEB_SEARCH,
    ICON_WORK
)