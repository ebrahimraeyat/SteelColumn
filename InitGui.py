


class SteelColumnWorkbench(Workbench):

	def __init__(self):
		from pathlib import Path
		import section

		steel_column_path = Path(section.__file__).parent 
		path = steel_column_path / 'Resources' / 'icons' / 'column.png'
		self.__class__.Icon = str(path)
		self.__class__.MenuText = "SteelColumn"
		self.__class__.ToolTip = "SteelColumn Workbench"

	def Initialize(self):
		from PySide2 import QtCore
		import SteelColumnGui
		command_list = SteelColumnGui.steel_column_commands
				
		self.appendToolbar(str(QtCore.QT_TRANSLATE_NOOP(
			"SteelColumn",
			"SteelColumn tools")), command_list)
		self.appendMenu(str(QtCore.QT_TRANSLATE_NOOP(
			"SteelColumn",
			"SteelColumn")), command_list)

Gui.addWorkbench(SteelColumnWorkbench())