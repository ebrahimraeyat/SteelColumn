import FreeCAD
import FreeCADGui as Gui
from FreeCADGui import Workbench


class SteelColumnWorkbench(Workbench):
    def __init__(self):
        from pathlib import Path
        import section

        steel_column_path = Path(section.__file__).parent
        translations_path = steel_column_path / "Resources" / "translations"
        icon_path = steel_column_path / "Resources" / "icons" / "column.png"

        # Add translations path
        Gui.addLanguagePath(str(translations_path))
        Gui.updateLocale()

        self.__class__.Icon = str(icon_path)
        self.__class__.MenuText = FreeCAD.Qt.translate("Workbench", "SteelColumn")
        self.__class__.ToolTip = FreeCAD.Qt.translate("Workbench", "SteelColumn Workbench")

    def Initialize(self):
        import SteelColumnGui

        QT_TRANSLATE_NOOP = FreeCAD.Qt.QT_TRANSLATE_NOOP

        command_list = SteelColumnGui.steel_column_commands

        self.appendToolbar(QT_TRANSLATE_NOOP("Workbench", "SteelColumn tools"), command_list)
        self.appendMenu(QT_TRANSLATE_NOOP("Workbench", "SteelColumn"), command_list)


Gui.addWorkbench(SteelColumnWorkbench())
