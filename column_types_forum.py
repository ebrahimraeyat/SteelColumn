import FreeCAD
import Arch
import Draft

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
		if not hasattr(obj, "v_scale"):
			obj.addProperty(
				"App::PropertyFloat",
                "v_scale",
                "column_type",
                ).v_scale = 1

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
		old_childrens_name = obj.childrens_name
		obj.childrens_name = childrens_name
		for name in old_childrens_name:
			children = FreeCAD.ActiveDocument.getObject(name)
			if hasattr(children, "Base") and children.Base:
				FreeCAD.ActiveDocument.removeObject(children.Base.Name)
			FreeCAD.ActiveDocument.removeObject(name)

	def get_level_text(self, level):
		if level == 0:
			text = f"{level:.2f}"
		elif level > 0:
			text = f"+ {level:.2f}"
		else:
			text =  f"- {abs(level):.2f}"
		print(text)
		return text


class ViewProviderColumnTypes:

	def __init__(self, obj):
		obj.Proxy = self

	def attach(self, vobj):
		self.ViewObject = vobj
		self.Object = vobj.Object

	def claimChildren(self):
		children=[FreeCAD.ActiveDocument.getObject(name) for name in self.Object.childrens_name]
		return children
    	

def make_columns_types(prop=[], heights=None, base_level=None):
	
	obj = FreeCAD.ActiveDocument.addObject("App::DocumentObjectGroupPython","Columns")
	ColumnTypes(obj)
	ViewProviderColumnTypes(obj.ViewObject)
	obj.heights = heights
	obj.base_level = base_level
	FreeCAD.ActiveDocument.recompute()
	FreeCAD.ActiveDocument.recompute()
	

make_columns_types(heights=[4, 3.2, 3.2, 3.2, 3.3, 5], base_level=-1.2)


