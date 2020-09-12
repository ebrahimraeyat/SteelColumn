import TechDraw
import FreeCADGui as Gui
import FreeCAD
import ezdxf


def add_edges_to_dxf(edges, dxfattribs, block):
	for e in edges:
		p1 = e.Vertexes[0]
		p2 = e.Vertexes[1]
		block.add_line((p1.X , -p1.Y), (p2.X , -p2.Y), dxfattribs=dxfattribs)

def get_unique_edges(edges, ct, scale, ignore_len=False):
	unique_edges = edges[:]
	
	for e in edges:
		if ignore_len:
			if e.Length >= ignore_len:
				unique_edges.remove(e)

	edges = unique_edges[:]

	if ct.connection_ipes_name and ignore_len:
		print("yes")
		connection_ipe_name = ct.connection_ipes_name[0]
		connection_ipe = FreeCAD.ActiveDocument.getObject(connection_ipe_name)
		bb = connection_ipe.Shape.BoundBox
		xmin, xmax = bb.XMin - ct.Placement.Base.x, bb.XMax - ct.Placement.Base.x

		for e in edges:
			# print(f"xmin = {xmin}, xmax = {xmax}, exmin = {e.BoundBox.XMin}")
			# break
			if xmin < e.BoundBox.XMin  / scale < xmax:
				unique_edges.remove(e)

	return unique_edges

		
# def get_unique_edges(edges, current_edges=[]):
# 	unique_edges = current_edges[:]
# 	for e in edges:
# 		if unique_edges:FreeCAD.ActiveDocument.getObject(ct.connection_ipes_name[0]).Height.Value
# 			p1 = e.firstVertex()
# 			p2 = e.lastVertex()
# 			equal = False
# 			for ce in unique_edges:
# 				p3 = ce.firstVertex()
# 				p4 = ce.lastVertex()
# 				if ((p1.Point == p3.Point) and (p2.Point == p4.Point)):
# 					equal = True
# 					break
# 			if not equal:
# 				unique_edges.append(e)
# 		else:
# 			unique_edges.append(e)
# 	return unique_edges



page = FreeCAD.ActiveDocument.addObject('TechDraw::DrawPage', 'Page')
FreeCAD.ActiveDocument.addObject('TechDraw::DrawSVGTemplate', 'Template')
templateFileSpec = '/usr/share/freecad-daily/Mod/TechDraw/Templates/A0_Landscape_blank.svg'
FreeCAD.ActiveDocument.Template.Template = templateFileSpec
FreeCAD.ActiveDocument.Page.Template = FreeCAD.ActiveDocument.Template
page.ViewObject.show()

new_dwg = ezdxf.readfile("/home/ebi/ali_momen/TEMPLATE.DXF")
msp = new_dwg.modelspace()

cts = []
for o in FreeCAD.ActiveDocument.Objects:
	if hasattr(o, "childrens_name"):
		cts.append(o)


for ct in cts:
	view = FreeCAD.ActiveDocument.addObject('TechDraw::DrawViewPart','View')
	view.HardHidden = True
	view.ViewObject.LineWidth = .05
	view.ViewObject.HiddenWidth = .005
	view.Direction = (1, 0, 0)
	# view.XDirection = (0, 0, 1)
	view.SmoothVisible = False
	# view.Perspective = True

	names = [ct.ipe_name] + ct.flang_plates_name + ct.base_plate_name + ct.nardebani_names + \
		ct.connection_ipes_name + ct.neshimans_name + ct.souble_ipes_name

	view.Source = [FreeCAD.ActiveDocument.getObject(name) for name in names]
	page.addView(view)
	view.Scale = .005
	FreeCAD.ActiveDocument.recompute()
	Gui.runCommand('TechDraw_ToggleFrame',0)
	visible_edges = view.getVisibleEdges()
	visible_edges = get_unique_edges(visible_edges, ct, view.Scale, False)
	hidden_edges = view.getHiddenEdges()
	h = FreeCAD.ActiveDocument.getObject(ct.ipe_name).Height.Value * view.Scale
	hidden_edges = get_unique_edges(hidden_edges, ct, view.Scale, h)



	block = new_dwg.blocks.new(name = ct.Name)
	IPE = FreeCAD.ActiveDocument.getObject(ct.ipe_name)
	h = IPE.Height.Value * view.Scale
	add_edges_to_dxf(visible_edges, {'layer':"COL"}, block)
	add_edges_to_dxf(hidden_edges, {'layer':"COL", "linetype":"DASHED2", "lineweight": 13}, block)
	x = ct.Placement.Base.x
	msp.add_blockref(ct.Name, (x * view.Scale, 0))
new_dwg.saveas("/home/ebi/ali_momen/ezdxf.dxf")


