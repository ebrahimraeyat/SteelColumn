from pathlib import Path

import FreeCAD
import FreeCADGui

import column_type
import column_types
import section
import update

steel_column_path = Path(__file__).parent

QT_TRANSLATE_NOOP = FreeCAD.Qt.QT_TRANSLATE_NOOP


class Dxf:
    def Activated(self):
        filename = get_save_filename(".dxf")
        if not filename:
            return
        import techdraw

        techdraw.export_to_dxf(filename)

    def IsActive(self):
        return True if FreeCADGui.ActiveDocument else False

    def GetResources(self):
        MenuText = QT_TRANSLATE_NOOP("SteelColumn_ExportDxf", "Export to DXF")
        ToolTip = QT_TRANSLATE_NOOP("SteelColumn_ExportDxf", "Export to DXF")

        path = steel_column_path / "Resources" / "icons" / "Dxf.svg"
        return {"Pixmap": str(path), "MenuText": MenuText, "ToolTip": ToolTip}


class Levels:
    def GetResources(self):
        MenuText = QT_TRANSLATE_NOOP("SteelColumn_CreateLevels", "Creates Levels")
        ToolTip = QT_TRANSLATE_NOOP("SteelColumn_CreateLevels", "Creates Levels")

        path = steel_column_path / "Resources" / "icons" / "Levels.svg"
        return {"Pixmap": str(path), "MenuText": MenuText, "ToolTip": ToolTip}

    def Activated(self):
        column_types.create_levels()

    def IsActive(self):
        return True if FreeCADGui.ActiveDocument else False


class Columns:
    def GetResources(self):
        MenuText = QT_TRANSLATE_NOOP("SteelColumn_CreateColumns", "Creates Columns")
        ToolTip = QT_TRANSLATE_NOOP("SteelColumn_CreateColumns", "Creates Columns")

        path = steel_column_path / "Resources" / "icons" / "add.svg"
        return {"Pixmap": str(path), "MenuText": MenuText, "ToolTip": ToolTip}

    def Activated(self):
        column_type.create_columns()

    def IsActive(self):
        return True if FreeCADGui.ActiveDocument.Levels else False


class RemoveColumn:
    def GetResources(self):
        MenuText = QT_TRANSLATE_NOOP("SteelColumn_RemoveColumns", "Remove Columns")
        ToolTip = QT_TRANSLATE_NOOP("SteelColumn_RemoveColumns", "Remove Columns")

        path = steel_column_path / "Resources" / "icons" / "remove.svg"
        return {"Pixmap": str(path), "MenuText": MenuText, "ToolTip": ToolTip}

    def Activated(self):
        column_type.remove_column()

    def IsActive(self):
        return True if FreeCADGui.ActiveDocument.Levels else False


class Sections:
    def GetResources(self):
        MenuText = QT_TRANSLATE_NOOP("SteelColumn_CreateSections", "Creates Sections")
        ToolTip = QT_TRANSLATE_NOOP("SteelColumn_CreateSections", "Creates Sections")

        path = steel_column_path / "Resources" / "icons" / "section.svg"
        return {"Pixmap": str(path), "MenuText": MenuText, "ToolTip": ToolTip}

    def Activated(self):
        section.create_sections()

    def IsActive(self):
        return True if FreeCADGui.ActiveDocument.Levels else False


class Update:
    def GetResources(self):
        MenuText = QT_TRANSLATE_NOOP("SteelColumn_UpdateWorkbench", "Update")
        ToolTip = QT_TRANSLATE_NOOP("SteelColumn_UpdateWorkbench", "Update Steel Column WorkBench")

        path = steel_column_path / "Resources" / "icons" / "update.png"
        return {"Pixmap": str(path), "MenuText": MenuText, "ToolTip": ToolTip}

    def Activated(self):
        update.update()

    def IsActive(self):
        return True


def get_save_filename(ext):
    from PySide.QtWidgets import QFileDialog

    filters = f"{ext[1:]} (*{ext})"
    filename, _ = QFileDialog.getSaveFileName(None, "select file", None, filters)
    if not filename:
        return
    if ext not in filename:
        filename += ext
    return filename


FreeCADGui.addCommand("SteelColumn_CreateLevels", Levels())
FreeCADGui.addCommand("SteelColumn_CreateSections", Sections())
FreeCADGui.addCommand("SteelColumn_CreateColumns", Columns())
FreeCADGui.addCommand("SteelColumn_RemoveColumns", RemoveColumn())
FreeCADGui.addCommand("SteelColumn_ExportDxf", Dxf())
FreeCADGui.addCommand("SteelColumn_UpdateWorkbench", Update())

steel_column_commands = [
    "SteelColumn_CreateLevels",
    "SteelColumn_CreateSections",
    "SteelColumn_CreateColumns",
    "SteelColumn_RemoveColumns",
    "SteelColumn_ExportDxf",
    "SteelColumn_UpdateWorkbench",
]
