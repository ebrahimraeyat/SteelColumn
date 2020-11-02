import FreeCAD
import FreeCADGui
import Arch
import Draft
import ArchComponent

from PySide2.QtWidgets import *
from PySide2.QtCore import *
from PySide2.QtGui import *
import sys, os
from os.path import join, dirname, abspath
from column_type import make_column_type

column_count = 3
STORY, HEIGHT, LEVEL = range(column_count)

class ColumnTypes:

	def __init__(self, obj):
		obj.Proxy = self
		self.set_properties(obj)

	def set_properties(self, obj):
		self.Type = "ColumnTypes"

		if not hasattr(obj, "base_level"):
			obj.addProperty(
				"App::PropertyFloat",
				"base_level",
				"column_types",
				)

		if not hasattr(obj, "heights"):
			obj.addProperty(
				"App::PropertyFloatList",
				"heights",
				"column_types",
			)

		if not hasattr(obj, "levels"):
			obj.addProperty(
				"App::PropertyFloatList",
				"levels",
				"column_types",
				)

		if not hasattr(obj, "v_scale"):
			obj.addProperty(
				"App::PropertyFloat",
				"v_scale",
				"column_types",
				).v_scale = .25

		if not hasattr(obj, "childrens_name"):
			obj.addProperty(
				"App::PropertyStringList",
				"childrens_name",
				"column_types",
				)


		if not hasattr(obj, "columns_names"):
			obj.addProperty(
				"App::PropertyStringList",
				"columns_names",
				"column_types",
				)

		if not hasattr(obj, "composite_deck"):
			obj.addProperty(
				"App::PropertyBool",
				"composite_deck",
				"Deck",
				).composite_deck = True


	def execute(self, obj):
		scale = 1000 * obj.v_scale
			# shapes = []
		childrens_name = []
		levels = [obj.base_level * scale]
		real_level = [obj.base_level]
		lev = self.get_level_text(real_level[-1])
		f = Arch.makeFloor(name=f"Base  {lev}")
		f.ViewObject.FontSize = 200
		f.ViewObject.ShowLevel = False
		f.Placement.Base = FreeCAD.Vector(-2000, -2000, levels[-1])
		childrens_name.append(f.Name)
		for i, height in enumerate(obj.heights):
			levels.append(levels[-1] + height * scale)
			real_level.append(real_level[-1] + height)
			lev = self.get_level_text(real_level[-1])
			f = Arch.makeFloor(name=f"Story {i + 1}  {lev}")
			f.ViewObject.FontSize = 200
			f.ViewObject.ShowLevel = False
			pl = FreeCAD.Vector(-2000, -2000, levels[-1])
			f.Placement.Base = pl
			f.Height = height * scale
			childrens_name.append(f.Name)
			rec = Draft.makeRectangle(length=20000, height=20000, face=True, support=None)
			rec.Placement.Base = pl
			rec.ViewObject.Transparency = 90
			rec.ViewObject.LineColor = (1.00,1.00,1.00)
			rec.ViewObject.PointColor = (1.00,1.00,1.00)
			rec.ViewObject.ShapeColor = (0.68,0.95,0.95)
			f.Group.append(rec.Name)
			childrens_name.append(rec.Name)

		obj.levels = real_level

		old_childrens_name = obj.childrens_name
		obj.childrens_name = childrens_name
		for name in old_childrens_name:
			children = FreeCAD.ActiveDocument.getObject(name)
			if hasattr(children, "Base") and children.Base:
				FreeCAD.ActiveDocument.removeObject(children.Base.Name)
			FreeCAD.ActiveDocument.removeObject(name)
		for o in FreeCAD.ActiveDocument.Objects:
			if hasattr(o, "Proxy"):
				if hasattr(o.Proxy, "Type") and o.Proxy.Type == "ColumnTypes":
					continue
			if hasattr(o, "v_scale") and o.v_scale != obj.v_scale:
				o.v_scale = obj.v_scale
			if hasattr(o, "base_level") and o.base_level != obj.base_level:
				o.base_level = obj.base_level
			if hasattr(o, "composite_deck") and o.composite_deck != obj.composite_deck:
				o.composite_deck = obj.composite_deck
			if hasattr(o, "heights") and o.heights == obj.heights:
				o.heights = obj.heights


	def get_level_text(self, level):
		if level == 0:
			text = f"{level:.2f}"
		elif level > 0:
			text = f"+ {level:.2f}"
		else:
			text =  f"- {abs(level):.2f}"
		return text


			


class ViewProviderColumnTypes(ArchComponent.ViewProviderComponent):

	def __init__(self, vobj):
		super().__init__(vobj)
		vobj.Proxy = self

	def attach(self, vobj):
		self.ViewObject = vobj
		self.Object = vobj.Object

	def claimChildren(self):
		children=[FreeCAD.ActiveDocument.getObject(name) for name in self.Object.childrens_name]
		return children

	def getIcon(self):
		return join(dirname(abspath(__file__)),"Resources", "icons","Levels.svg")

	def setEdit(self, vobj, mode=0):
		create_levels()
		return True

	def unsetEdit(self, vobj, mode):
		FreeCADGui.Control.closeDialog()
		return
		



def make_columns_types(prop=[], heights=None, base_level=None):
	FreeCADGui.activateWorkbench("ArchWorkbench")
	obj = FreeCAD.ActiveDocument.addObject("App::DocumentObjectGroupPython","Levels")
	ColumnTypes(obj)
	ViewProviderColumnTypes(obj.ViewObject)
	obj.heights = heights
	obj.base_level = base_level
	obj.Proxy.column_types_prop = prop
	FreeCAD.ActiveDocument.recompute()
	FreeCAD.ActiveDocument.recompute()
	FreeCADGui.activeDocument().activeView().viewFront()
	FreeCADGui.SendMsgToActiveView("ViewFit")
	FreeCADGui.activateWorkbench("SteelColumnWorkbench")
	return obj


class LevelTableModel(QAbstractTableModel):

	def __init__(self):
		super(LevelTableModel, self).__init__()
		self.cts = None

	def headerData(self, section, orientation, role=Qt.DisplayRole):
		if role == Qt.TextAlignmentRole:
			if orientation == Qt.Horizontal:
				return int(Qt.AlignLeft | Qt.AlignVCenter)
			return int(Qt.AlignRight | Qt.AlignVCenter)
		if role != Qt.DisplayRole:
			return

		if orientation == Qt.Horizontal:
			if section == STORY:
				return "Story"
			elif section == HEIGHT:
				return "Height"
			elif section == LEVEL:
				return "Level"

	def flags(self, index):
		if not index.isValid():
			return Qt.ItemIsEnabled
		col = index.column()
		i = index.row()
		if col == STORY:
			return Qt.ItemIsEnabled
		if i != 0 and col == LEVEL:
			return Qt.ItemIsEnabled

		if i == 0 and col == HEIGHT:
			return Qt.ItemIsEnabled

		return Qt.ItemFlags(
			QAbstractTableModel.flags(self, index) |
			Qt.ItemIsEditable)

	def data(self, index, role=Qt.DisplayRole):
		if (not index.isValid() or
				not (0 <= index.row() < len(self.cts.heights) + 1)):
			return
		i = index.row()
		column = index.column()

		if role == Qt.DisplayRole:
			if column == STORY:
				if i == 0:
					return "Base"
				return f"Story {i}"
			elif column == HEIGHT:
				if i == 0:
					return ""
				return str(self.cts.heights[i - 1])

			elif column == LEVEL:
				return str(self.cts.levels[i])



	def rowCount(self, index=QModelIndex()):
		if self.cts:
			return len(self.cts.heights) + 1
		return 0

	def columnCount(self, index=QModelIndex()):
		return column_count

	def setData(self, index, value, role=Qt.EditRole):
		if index.isValid() and 0 <= index.row() < len(self.cts.heights) + 1:
			column = index.column()
			i = index.row()
			if column == HEIGHT:
				self.cts.heights = self.cts.heights[:i - 1] + [float(value)] + self.cts.heights[i:]
				self.cts.Proxy.execute(self.cts)
			elif i == 0 and column == LEVEL:
				self.cts.base_level = float(value)
				self.cts.Proxy.execute(self.cts)
			self.dataChanged.emit(index, index)
			FreeCAD.ActiveDocument.recompute()
			FreeCAD.ActiveDocument.recompute()
			return True
		return False


	def insertRows(self, position, index=QModelIndex()):
		self.beginInsertRows(QModelIndex(), position, position)
		self.cts.heights.insert(position + 1, 3)



class Ui:

	def __init__(self):
		self.form = FreeCADGui.PySideUic.loadUi(os.path.join(
				os.path.dirname(__file__), 'Resources/ui/story.ui')
			)

	def setupUi(self):
		self.add_connections()
		self.model = LevelTableModel()
		try:
			self.model.cts = FreeCAD.ActiveDocument.Levels
		except:
			self.model.cts = make_columns_types(heights=[], base_level=-1.2)
		self.form.tableView.setModel(self.model)


	def add_connections(self):
		self.form.addButton.clicked.connect(self.add_story)
		self.form.removeButton.clicked.connect(self.remove_story)


	def add_story(self):
		self.model.beginResetModel()
		self.model.cts.heights += [4]
		self.model.cts.v_scale = self.form.v_scale.value()
		self.model.cts.composite_deck = self.form.composite_deck.isChecked()
		self.model.cts.Proxy.execute(self.model.cts)
		self.model.endResetModel()
		FreeCAD.ActiveDocument.recompute()
		FreeCAD.ActiveDocument.recompute()
		FreeCADGui.SendMsgToActiveView("ViewFit")

	def remove_story(self):
		indexes = self.form.tableView.selectionModel().selectedRows()

		for index in indexes:
			i = index.row()
			if i == 0:
				return
			self.model.beginResetModel()
			self.model.cts.heights = self.model.cts.heights[:i-1] + self.model.cts.heights[i:]
			self.model.cts.Proxy.execute(self.model.cts)
			self.model.endResetModel()
			FreeCAD.ActiveDocument.recompute()
			FreeCAD.ActiveDocument.recompute()

	def getStandardButtons(self):
		return int(QDialogButtonBox.Close)

def create_levels():
	ui = Ui()
	FreeCADGui.Control.showDialog(ui)
	if ui.setupUi():
		FreeCADGui.Control.closeDialog(ui)
	FreeCAD.ActiveDocument.recompute()


if __name__ == '__main__':
	create_levels()


