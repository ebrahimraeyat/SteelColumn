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
        MenuText = QT_TRANSLATE_NOOP("Dxf", "Export to DXF")
        ToolTip = QT_TRANSLATE_NOOP("Dxf", "Export to DXF")

        path = steel_column_path / "Resources" / "icons" / "Dxf.svg"
        return {"Pixmap": str(path), "MenuText": MenuText, "ToolTip": ToolTip}


class Levels:
    def GetResources(self):
        MenuText = QT_TRANSLATE_NOOP("Levels", "Creates Levels")
        ToolTip = QT_TRANSLATE_NOOP("Levels", "Creates Levels")

        path = steel_column_path / "Resources" / "icons" / "Levels.svg"
        return {"Pixmap": str(path), "MenuText": MenuText, "ToolTip": ToolTip}

    def Activated(self):
        column_types.create_levels()

    def IsActive(self):
        return True if FreeCADGui.ActiveDocument else False


class Columns:
    def GetResources(self):
        MenuText = QT_TRANSLATE_NOOP("Levels", "Creates Columns")
        ToolTip = QT_TRANSLATE_NOOP("Levels", "Creates Columns")

        path = steel_column_path / "Resources" / "icons" / "add.svg"
        return {"Pixmap": str(path), "MenuText": MenuText, "ToolTip": ToolTip}

    def Activated(self):
        column_type.create_columns()

    def IsActive(self):
        return True if FreeCADGui.ActiveDocument.Levels else False


class RemoveColumn:
    def GetResources(self):
        MenuText = QT_TRANSLATE_NOOP("Levels", "Remove Columns")
        ToolTip = QT_TRANSLATE_NOOP("Levels", "Remove Columns")

        path = steel_column_path / "Resources" / "icons" / "remove.svg"
        return {"Pixmap": str(path), "MenuText": MenuText, "ToolTip": ToolTip}

    def Activated(self):
        column_type.remove_column()

    def IsActive(self):
        return True if FreeCADGui.ActiveDocument.Levels else False


class Sections:
    def GetResources(self):
        MenuText = QT_TRANSLATE_NOOP("Sections", "Creates Sections")
        ToolTip = QT_TRANSLATE_NOOP("Sections", "Creates Sections")

        path = steel_column_path / "Resources" / "icons" / "section.svg"
        return {"Pixmap": str(path), "MenuText": MenuText, "ToolTip": ToolTip}

    def Activated(self):
        section.create_sections()

    def IsActive(self):
        return True if FreeCADGui.ActiveDocument.Levels else False


class Update:
    def GetResources(self):
        MenuText = QT_TRANSLATE_NOOP("Update", "Update")
        ToolTip = QT_TRANSLATE_NOOP("Update", "Update Steel Column WorkBench")

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


FreeCADGui.addCommand("steel_column_levels", Levels())
FreeCADGui.addCommand("steel_column_section", Sections())
FreeCADGui.addCommand("steel_column_columns", Columns())
FreeCADGui.addCommand("steel_column_remove", RemoveColumn())
FreeCADGui.addCommand("steel_column_dxf", Dxf())
FreeCADGui.addCommand("steel_column_update", Update())

steel_column_commands = [
    "steel_column_levels",
    "steel_column_section",
    "steel_column_columns",
    "steel_column_remove",
    "steel_column_dxf",
    "steel_column_update",
]
