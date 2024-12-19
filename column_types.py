import FreeCAD
import FreeCADGui
import Arch
import Draft
import Part
import ArchComponent

from PySide.QtWidgets import *
from PySide.QtCore import *
from PySide.QtGui import *
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

		if not hasattr(obj, "sections_name"):
			obj.addProperty(
				"App::PropertyStringList",
				"sections_name",
				"column_types")

		if not hasattr(obj, "Base"):
			obj.addProperty(
				"App::PropertyLink",
				"Base",
				"column_types",
				)

		if not hasattr(obj, "heights"):
			obj.addProperty(
				"App::PropertyFloatList",
				"heights",
				"Levels",
			)

		if not hasattr(obj, "levels"):
			obj.addProperty(
				"App::PropertyFloatList",
				"levels",
				"Levels",
				)
			obj.setEditorMode("levels", 1)

		if not hasattr(obj, "levels_name"):
			obj.addProperty(
				"App::PropertyStringList",
				"levels_name",
				"Levels",
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
			obj.setEditorMode("childrens_name", 1)


		if not hasattr(obj, "columns_names"):
			obj.addProperty(
				"App::PropertyStringList",
				"columns_names",
				"column_types",
				)
			obj.setEditorMode("columns_names", 1)

		if not hasattr(obj, "composite_deck"):
			obj.addProperty(
				"App::PropertyBool",
				"composite_deck",
				"Deck",
				).composite_deck = True


	def execute(self, obj):
		scale = 1000 * obj.v_scale
		shapes = []
		childrens_name = []
		levels = [obj.base_level * scale]
		real_level = [obj.base_level]
		lev = self.get_level_text(real_level[-1])
		f = Arch.makeFloor(name=f"{obj.levels_name[0]}  {lev}")
		f.ViewObject.FontSize = 200
		f.ViewObject.ShowLevel = False
		f.Placement.Base = FreeCAD.Vector(-2000, -2000, levels[-1])
		plane = Part.makePlane(20000, 20000)
		plane.Placement.Base.z = levels[-1]
		shapes.append(plane)
		childrens_name.append(f.Name)
		for i, height in enumerate(obj.heights):
			levels.append(levels[-1] + height * scale)
			real_level.append(real_level[-1] + height)
			lev = self.get_level_text(real_level[-1])
			f = Arch.makeFloor(name=f"{obj.levels_name[i + 1]}  {lev}")
			f.ViewObject.FontSize = 200
			f.ViewObject.ShowLevel = False
			pl = FreeCAD.Vector(-2000, -2000, levels[-1])
			f.Placement.Base = pl
			f.Height = height * scale
			childrens_name.append(f.Name)
			plane = Part.makePlane(20000, 20000)
			plane.Placement.Base.z = levels[-1]
			shapes.append(plane)
		com = Part.makeCompound(shapes)
		obj.Shape = com
		obj.ViewObject.Transparency = 90
		obj.ViewObject.LineColor = (1.00,1.00,1.00)
		obj.ViewObject.PointColor = (1.00,1.00,1.00)
		obj.ViewObject.ShapeColor = (0.68,0.95,0.95)

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
		ui = Ui()
		ui.setupUi()
		FreeCADGui.Control.showDialog(ui)
		return True

	def unsetEdit(self, vobj, mode):
		FreeCADGui.Control.closeDialog()
		return

	def doubleClicked(self,vobj):
		self.setEdit(vobj)

	def __getstate__(self):
		return None

	def __setstate__(self, state):
		return None
		



def make_columns_types(
		heights=[3.5],
		base_level=-1.2,
		levels_name=["Base", "Story 1"],
		):
	FreeCADGui.activateWorkbench("ArchWorkbench")
	obj = FreeCAD.ActiveDocument.addObject("Part::FeaturePython","Levels")
	ColumnTypes(obj)
	ViewProviderColumnTypes(obj.ViewObject)
	obj.heights = heights
	obj.base_level = base_level
	obj.levels_name = levels_name
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
		if orientation == Qt.Vertical:
			return str(section + 1)

	def flags(self, index):
		if not index.isValid():
			return Qt.ItemIsEnabled
		col = index.column()
		i = index.row()
		if i != 0 and col == LEVEL:
			return Qt.ItemIsEnabled

		if i == 0 and col == HEIGHT:
			return Qt.ItemIsEnabled

		if col == STORY:
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
				return str(self.cts.levels_name[i])
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
			elif column == STORY:
				if str(value) in self.cts.levels_name:
					return False
				if i < len(self.cts.levels_name):
					self.cts.levels_name = self.cts.levels_name[:i] + [str(value)] + self.cts.levels_name[i + 1:]
				else:
					self.cts.levels_name = self.cts.levels_name[:i] + [str(value)]
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
		icon_path = os.path.join(
			os.path.dirname(__file__), 'Resources/icons/')
		self.form.addButton.setIcon(QPixmap(icon_path + "add.svg"))
		self.form.removeButton.setIcon(QPixmap(icon_path + "remove.svg"))
		self.model = LevelTableModel()
		try:
			self.model.cts = FreeCAD.ActiveDocument.Levels
		except:
			self.model.cts = make_columns_types(heights=[3.5,], base_level=-1.2,
			levels_name=["Base", "Story 1"])
		self.form.story_name.setText(f"Story {len(self.model.cts.heights) + 1}")
		self.form.tableView.setModel(self.model)


	def add_connections(self):
		self.form.addButton.clicked.connect(self.add_story)
		self.form.removeButton.clicked.connect(self.remove_story)


	def add_story(self):
		self.model.beginResetModel()
		self.model.cts.heights += [self.form.height_spinbox.value()]
		self.model.cts.levels_name += [self.form.story_name.text()]
		self.model.cts.v_scale = self.form.v_scale.value()
		self.model.cts.composite_deck = self.form.composite_deck.isChecked()
		self.model.cts.Proxy.execute(self.model.cts)
		self.model.endResetModel()
		FreeCAD.ActiveDocument.recompute()
		FreeCAD.ActiveDocument.recompute()
		self.form.story_name.setText(f"Story {len(self.model.cts.levels_name)}")
		FreeCADGui.SendMsgToActiveView("ViewFit")

	def remove_story(self):
		indexes = self.form.tableView.selectionModel().selectedRows()

		for index in indexes:
			i = index.row()
			col = index.column()
			if i == 0 and col == LEVEL:
				return
			self.model.beginResetModel()
			self.model.cts.heights = self.model.cts.heights[:i-1] + self.model.cts.heights[i:]
			if i < len(self.model.cts.levels_name):
				self.model.cts.levels_name = self.model.cts.levels_name[:i] + self.model.cts.levels_name[i + 1:]
			else:
				self.model.cts.levels_name = self.model.cts.levels_name[:i]
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


