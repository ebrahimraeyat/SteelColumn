import TechDraw
import FreeCADGui as Gui
import FreeCAD
import ezdxf
from ezdxf.tools.standards import linetypes


def add_edges_to_dxf(edges, dxfattribs, block, x):
	for e in edges:
		if e.Length == 0:
			continue

		if e.BoundBox.XLength and e.BoundBox.YLength:
			continue
		if len(e.Vertexes) == 2:
			p1 = e.Vertexes[0]
			p2 = e.Vertexes[1]
			block.add_line((p1.X + x, -p1.Y), (p2.X + x, -p2.Y), dxfattribs=dxfattribs)

def add_section_edges_to_dxf(name, dxfattribs, block, z, scale):
	edges = []
	o = FreeCAD.ActiveDocument.getObject(name)
	for e in o.Shape.Edges:
		edges.append(e)
	for e in edges:
		if len(e.Vertexes) == 2:
			p1 = e.Vertexes[0]
			p2 = e.Vertexes[1]
			block.add_line((p1.X * scale, p1.Z * scale + z),
							(p2.X * scale, p2.Z * scale + z),
							dxfattribs=dxfattribs)
	bb = o.Shape.BoundBox
	dxfattribs['height'] = 30 * scale
	x = (bb.XMax + bb.XMin) / 2 * scale
	y = bb.ZMin  * scale + z - 20 * scale
	block.add_text(o.name[:6],
					dxfattribs=dxfattribs).set_pos(
					(x, y),
					align="TOP_CENTER"
					)
	if o.flange_plate_size:
		bf, tf = o.flange_plate_size
		y = bb.ZMax * scale + z + 20 * scale
		block.add_text(f"2PL{bf}*{tf}",
					dxfattribs=dxfattribs).set_pos(
					(x, y),
					align="BOTTOM_CENTER"
					)

	if o.web_plate_size:
		bf, tf = o.web_plate_size
		y = (bb.ZMax + bb.ZMin) / 2 * scale + z
		x = bb.XMax * scale
		block.add_text(f"2PL{bf}*{tf}",
			dxfattribs=dxfattribs).set_pos(
			(x, y),
			align="MIDDLE_LEFT")


def get_unique_edges(edges, ct, scale, ignore_len=False):
	unique_edges = edges[:]
	
	for e in edges:
		if ignore_len:
			if e.Length >= ignore_len:
				unique_edges.remove(e)

	edges = unique_edges[:]

	if ct.connection_ipes_name and ignore_len:
		connection_ipe_name = ct.connection_ipes_name[0]
		connection_ipe = FreeCAD.ActiveDocument.getObject(connection_ipe_name)
		bb = connection_ipe.Shape.BoundBox
		xmin, xmax = bb.XMin - ct.Placement.Base.x, bb.XMax - ct.Placement.Base.x

		for e in edges:
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

new_dwg = ezdxf.new()
msp = new_dwg.modelspace()
new_dwg.layers.new(name='COL')
new_dwg.layers.new(name="Section")
line_types = [('DASHEDX2', 'Dashed (2x) ____  ____  ____  ____  ____  ____', [1.2, 1.0, -0.2]), ('DASHED2', 'Dashed (.5x) _ _ _ _ _ _ _ _ _ _ _ _ _ _', [0.1, 0.1, -0.05])]
for name, desc, pattern in line_types:
    if name not in new_dwg.linetypes:
        new_dwg.linetypes.new(name=name, dxfattribs={'description': desc, 'pattern': pattern})


cts = []
for o in FreeCAD.ActiveDocument.Objects:
	if hasattr(o, "base_plate_name"):
		cts.append(o)


for ct in cts:
	view = FreeCAD.ActiveDocument.addObject('TechDraw::DrawViewPart','View')
	view.HardHidden = True
	view.ViewObject.LineWidth = .005
	view.ViewObject.HiddenWidth = .001
	# view.Direction = (1, 0, 0)
	view.Direction = (0, -1, 0)
	# view.XDirection = (0, 0, 1)
	# view.SmoothVisible = True
	# view.Perspective = True
	# names = ct.front_draw_sources_name + ct.sections_obj_name
	names = [ct.ipe_name] + ct.flang_plates_name + ct.base_plate_name + ct.nardebani_names + \
		ct.connection_ipes_name + ct.souble_ipes_name + ct.neshimans_name

	view.Source = [FreeCAD.ActiveDocument.getObject(name) for name in names]
	page.addView(view)
	view.Scale = 1
	FreeCAD.ActiveDocument.recompute()
	Gui.runCommand('TechDraw_ToggleFrame',0)
	visible_edges = view.getVisibleEdges()
	h = FreeCAD.ActiveDocument.getObject(ct.ipe_name).Height.Value * view.Scale
	first_height = ct.heights[0] * ct.v_scale * 1000 * view.Scale
	z = - h / 2 + first_height / 2
	for i, name in enumerate(ct.sections_obj_name):
		# story_mid_level = (ct.levels[i + 1] - ct.levels[i]) / 2 * view.Scale
		add_section_edges_to_dxf(name, {'layer':"Section", 'color': 2}, msp, z, view.Scale)
	e = visible_edges[0]
	comp = e.generalFuse(visible_edges[1:])
	visible_edges = comp[0].Edges
	hidden_edges = view.getHiddenEdges()
	hidden_edges = get_unique_edges(hidden_edges, ct, view.Scale, h)
	e = hidden_edges[0]
	comp = e.generalFuse(hidden_edges[1:])
	hidden_edges = comp[0].Edges




	# block = new_dwg.blocks.new(name = ct.Name)
	# IPE = FreeCAD.ActiveDocument.getObject(ct.ipe_name)
	# h = IPE.Height.Value * view.Scale
	x = (ct.Placement.Base.x) * view.Scale
	add_edges_to_dxf(visible_edges, {'layer':"COL"}, msp, x)
	add_edges_to_dxf(hidden_edges, {'layer':"COL", "linetype":"DASHED2", "lineweight": 13}, msp, x)

	# msp.add_blockref(ct.Name, (x * view.Scale, 0))
new_dwg.set_modelspace_vport(height=1000, center=(0, 0))
new_dwg.saveas("/home/ebi/alaki/ezdxf.dxf")

FreeCAD.ActiveDocument.removeObject(page.Name)


