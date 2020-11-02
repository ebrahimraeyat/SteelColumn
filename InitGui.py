


class SteelColumnWorkbench(Workbench):

	def __init__(self):
		rel_path = "Mod/SteelColumn/Resources/icons/column.png"
		path = FreeCAD.ConfigGet("AppHomePath") + rel_path
		import os
		if not os.path.exists(path):
		    path = FreeCAD.ConfigGet("UserAppData") + rel_path
		self.__class__.Icon = path
		self.__class__.MenuText = "SteelColumn"
		self.__class__.ToolTip = "SteelColumn Workbench"

	def Initialize(self):
		from PySide2 import QtCore, QtGui
		import SteelColumnGui
		command_list = SteelColumnGui.steel_column_commands
				
		self.appendToolbar(str(QtCore.QT_TRANSLATE_NOOP(
			"SteelColumn",
			"SteelColumn tools")), command_list)
		self.appendMenu(str(QtCore.QT_TRANSLATE_NOOP(
			"SteelColumn",
			"SteelColumn")), command_list)

Gui.addWorkbench(SteelColumnWorkbench())