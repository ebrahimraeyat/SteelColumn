try:
    from PySide.QtWidgets import *
    from PySide.QtCore import *
    from PySide.QtGui import *
except ImportError:
    from PySide2.QtWidgets import *
    from PySide2.QtCore import *
    from PySide2.QtGui import *
import os
import FreeCAD

def update():
    if (QMessageBox.question(None, "update", "update to latest version?!",
                             QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes) == QMessageBox.No):
        return
    if not internet():
        msg = "You are not connected to the Internet, please check your internet connection."
        QMessageBox.warning(None, 'update', str(msg))
        return

    steel_column_path = os.path.abspath(os.path.join(os.path.dirname(__file__)))
    user_data_dir = FreeCAD.getUserAppDataDir()
    if not user_data_dir in steel_column_path:
        mod_path = os.path.join(user_data_dir, 'Mod')
        if not os.path.exists(mod_path):
            os.mkdir(mod_path)
        steel_column_path = os.path.join(mod_path, 'SteelColumn')
    import git
    g = git.cmd.Git(steel_column_path)
    msg = ''
    try:
        msg = g.pull(env={'GIT_SSL_NO_VERIFY': '1'})
    except:
        QMessageBox.information(None, "update", "update takes some minutes, please be patient.")
        import shutil
        import tempfile
        default_tmp_dir = tempfile._get_default_tempdir()
        name = next(tempfile._get_candidate_names())
        steel_column_temp_dir = os.path.join(default_tmp_dir, 'steel_column' + name)
        os.mkdir(steel_column_temp_dir)
        os.chdir(steel_column_temp_dir)
        git.Git('.').clone("https://github.com/ebrahimraeyat/momen.git", env={'GIT_SSL_NO_VERIFY': '1'})
        src_folder = os.path.join(steel_column_temp_dir, 'momen')

        shutil.copytree(src_folder, steel_column_path)
        msg = 'update done successfully, please remove steel_column folder from FreeCAD installation folder!,  then restart FreeCAD.'

    else:
        if not msg:
            msg = 'error occurred during update\nplease contact with @roknabadi'
    # msg += '\n please restart the program.'
    QMessageBox.information(None, 'update', msg)


def onerror(func, path, exc_info):
    """
    Error handler for ``shutil.rmtree``.

    If the error is due to an access error (read only file)
    it attempts to add write permission and then retries.

    If the error is for another reason it re-raises the error.

    Usage : ``shutil.rmtree(path, onerror=onerror)``
    """
    import stat
    if not os.access(path, os.W_OK):
        # Is the error an access error ?
        os.chmod(path, stat.S_IWUSR)
        func(path)
    else:
        print('another error')
        raise


def internet(host="8.8.8.8", port=53, timeout=3):
    import socket
    try:
        socket.setdefaulttimeout(timeout)
        socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect((host, port))
        return True
    except Exception as ex:
        return False
