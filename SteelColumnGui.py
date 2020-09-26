import PySide2
from PySide2 import QtCore, QtGui
import FreeCAD
import FreeCADGui as Gui
import DraftTools
import os
import techdraw

# from safe.punch import punchPanel


def QT_TRANSLATE_NOOP(ctx, txt): return txt


class Dxf:
    def Activated(self):
        filename = get_save_filename('.dxf')
        if not filename:
            return
        techdraw.export_to_dxf(filename)

    def GetResources(self):
        MenuText = QtCore.QT_TRANSLATE_NOOP(
            "Dxf",
            "Export to Dxf")
        ToolTip = QtCore.QT_TRANSLATE_NOOP(
            "Dxf",
            "Export to Dxf")
        rel_path = "Mod/SteelColumn/icons/Dxf.svg"
        path = FreeCAD.ConfigGet("AppHomePath") + rel_path
        import os
        if not os.path.exists(path):
            path = FreeCAD.ConfigGet("UserAppData") + rel_path
        return {'Pixmap': path,
                'MenuText': MenuText,
                'ToolTip': ToolTip}


# class Copy(DraftTools.Move):

#     def __init__(self):
#         DraftTools.Move.__init__(self)

#     def GetResources(self):

#         return {'Pixmap': os.path.join(os.path.dirname(__file__), "images", "copy.svg"),
#                 'MenuText': QtCore.QT_TRANSLATE_NOOP("Copy", "Copy"),
#                 'ToolTip': QtCore.QT_TRANSLATE_NOOP("TogglePanels", "Copies selected objects to another location"),
#                 'Accel': 'C,P'}


# class CivilPdf:
#     def Activated(self):
#         from safe.punch import pdf
#         doc = FreeCAD.ActiveDocument
#         filename = get_save_filename('.pdf')
#         pdf.createPdf(doc, filename)

#     def GetResources(self):
#         MenuText = QtCore.QT_TRANSLATE_NOOP(
#             "Civil_pdf",
#             "Export to pdf")
#         ToolTip = QtCore.QT_TRANSLATE_NOOP(
#             "Civil_pdf",
#             "export to pdf")
#         rel_path = "Mod/Civil/safe/punch/icon/pdf.svg"
#         path = FreeCAD.ConfigGet("AppHomePath") + rel_path
#         import os
#         if not os.path.exists(path):
#             path = FreeCAD.ConfigGet("UserAppData") + rel_path
#         return {'Pixmap': path,
#                 'MenuText': MenuText,
#                 'ToolTip': ToolTip}

#     def IsActive(self):
#         return not FreeCAD.ActiveDocument is None


def get_save_filename(ext):
    from PySide2.QtWidgets import QFileDialog
    filters = f"{ext[1:]} (*{ext})"
    filename, _ = QFileDialog.getSaveFileName(None, 'select file',
                                              None, filters)
    if not filename:
        return
    if not ext in filename:
        filename += ext
    return filename


Gui.addCommand('Dxf', Dxf())
# Gui.addCommand('Copy', Copy())
# Gui.addCommand('Civil_pdf', CivilPdf())
