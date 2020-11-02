import PySide2
from PySide2 import QtCore, QtGui
import FreeCAD
import FreeCADGui
import DraftTools
import os
import techdraw
import column_types
import column_type


# from safe.punch import punchPanel


def QT_TRANSLATE_NOOP(ctx, txt): return txt


class Dxf:
    def Activated(self):
        filename = get_save_filename('.dxf')
        if not filename:
            return
        techdraw.export_to_dxf(filename)

    def IsActive(self):
        return True if FreeCADGui.ActiveDocument else False

    def GetResources(self):
        MenuText = QtCore.QT_TRANSLATE_NOOP(
            "Dxf",
            "Export to Dxf")
        ToolTip = QtCore.QT_TRANSLATE_NOOP(
            "Dxf",
            "Export to Dxf")
        rel_path = "Mod/SteelColumn/Resources/icons/Dxf.svg"
        path = FreeCAD.ConfigGet("AppHomePath") + rel_path
        import os
        if not os.path.exists(path):
            path = FreeCAD.ConfigGet("UserAppData") + rel_path
        return {'Pixmap': path,
                'MenuText': MenuText,
                'ToolTip': ToolTip}

class Levels:

    def GetResources(self):
        MenuText = QtCore.QT_TRANSLATE_NOOP(
            "Levels",
            "Creates Levels")
        ToolTip = QtCore.QT_TRANSLATE_NOOP(
            "Levels",
            "Creates Levels")
        rel_path = "Mod/SteelColumn/Resources/icons/Levels.svg"
        path = FreeCAD.getHomePath() + rel_path
        import os
        if not os.path.exists(path):
            path =  FreeCAD.getUserAppDataDir() + rel_path
        return {'Pixmap': path,
                'MenuText': MenuText,
                'ToolTip': ToolTip}


    def  Activated(self):
        column_types.create_levels()

    def IsActive(self):
        return True if FreeCADGui.ActiveDocument else False


class Columns:

    def GetResources(self):
        MenuText = QtCore.QT_TRANSLATE_NOOP(
            "Levels",
            "Creates Levels")
        ToolTip = QtCore.QT_TRANSLATE_NOOP(
            "Levels",
            "Creates Levels")
        rel_path = "Mod/SteelColumn/Resources/icons/column"
        path = FreeCAD.getHomePath() + rel_path
        import os
        if not os.path.exists(path):
            path =  FreeCAD.getUserAppDataDir() + rel_path
        return {'Pixmap': path,
                'MenuText': MenuText,
                'ToolTip': ToolTip}


    def  Activated(self):
        column_type.create_columns()

    def IsActive(self):
        return True if FreeCADGui.ActiveDocument.Levels else False



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


FreeCADGui.addCommand('Dxf', Dxf())
FreeCADGui.addCommand("steel_column_levels", Levels())
FreeCADGui.addCommand("steel_column_columns", Columns())

steel_column_commands = [
    "steel_column_levels",
    "steel_column_columns",
    "Dxf",
    ]
