import civilGui


class CivilWorkbench(Workbench):

	def __init__(self):
		self.__class__.Icon = FreeCAD.ConfigGet("AppHomePath") + "Mod/Civil/images/civil-engineering.png"
		self.__class__.MenuText = "Civil"
		self.__class__.ToolTip = "Civil Workbench"

	def Initialize(self):
		from PySide2 import QtCore, QtGui
		command_list = ["Section",
						"Punch"]
				
		self.appendToolbar(str(QtCore.QT_TRANSLATE_NOOP(
			"Civil",
			"Civil tools")), command_list)
		self.appendMenu(str(QtCore.QT_TRANSLATE_NOOP(
			"Civil",
			"Civil")), command_list)

Gui.addWorkbench(CivilWorkbench())