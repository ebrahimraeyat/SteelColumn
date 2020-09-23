from os.path import join, dirname, abspath
import TechDraw
import FreeCADGui as Gui
import FreeCAD
import Part
import ezdxf
from ezdxf.tools.standards import linetypes


def add_edges_to_dxf(edges, dxfattribs, block, x, y):
	for e in edges:
		if e.Length == 0:
			continue

		if len(e.Vertexes) == 2:
			p1 = e.Vertexes[0]
			p2 = e.Vertexes[1]
			block.add_line((p1.X + x, -p1.Y + y), (p2.X + x, -p2.Y + y), dxfattribs=dxfattribs)

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
	dxfattribs['style'] = 'ROMANT'
	x = (bb.XMax + bb.XMin) / 2 * scale
	y = bb.ZMin  * scale + z - 30 * scale
	block.add_text(f"{o.name[:6]}0",
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

	if all((o.dist > 0, not o.flange_plate_size, o.n==2)):
		x = bb.Center.x * scale
		y = bb.ZMax * scale + z
		bf = bb.XLength * scale * .8
		tf = bb.ZLength * scale * .05
		dxfattribs['xscale'] = bf
		dxfattribs['yscale'] = tf
		del(dxfattribs['height'])
		del(dxfattribs['style'])
		block.add_blockref("plate", (x, y), dxfattribs=dxfattribs)
		block.add_blockref("plate", (x, y - bb.ZLength * scale - tf), dxfattribs=dxfattribs)


def add_leader_for_connection_ipe(name, dxfattribs, block, scale):
	o = FreeCAD.ActiveDocument.getObject(name)
	center_of_mass = o.Shape.CenterOfMass
	y =  center_of_mass.z * scale + 50 * scale
	x1 = center_of_mass.x * scale
	x2 = x1 + 450 * scale
	block.add_blockref("juyuy", (x1, y), dxfattribs={
        'xscale': scale,
        'yscale': scale},
        )
	size = int(o.Base.Shape.BoundBox.YLength)
	block.add_text(f"IPE{size}",
					dxfattribs=dxfattribs).set_pos(
					(x2, y),
					align="BOTTOM_RIGHT"
					)
	y =  (center_of_mass.z + 40) * scale
	block.add_text("L=100 cm",
					dxfattribs=dxfattribs).set_pos(
					(x2, y),
					align="TOP_RIGHT"
					)

def add_level_to_dxf(text, x1, x2, y1, y2, dxfattribs, block, scale):
	block.add_blockref("kkkkk3", (x2, y1), dxfattribs={
        'xscale': scale,
        'yscale': scale},
        )
	block.add_text(
			text,
			dxfattribs = dxfattribs).set_pos(
			(x2, y2),
			align="BOTTOM_RIGHT",
			)

def add_levels_to_dxf(ct, dxfattribs, block, scale):
	o = FreeCAD.ActiveDocument.getObject(ct.ipe_name)
	x = o.Shape.BoundBox.XMin * scale
	x1 = x - 500 * scale
	x2 = x - 100 * scale
	for i, name in enumerate(ct.neshimans_name):
		o = FreeCAD.ActiveDocument.getObject(name)
		y1 = o.Shape.BoundBox.ZMax * scale
		y2 = y1 + 30 * scale
		if ct.levels[i + 1] > 0:
			text = f"T.O.B = +{ct.levels[i + 1] / ct.v_scale / 1000:.2f}"
		else:
			text = f"T.O.B = {ct.levels[i + 1] / ct.v_scale / 1000:.2f}"
		add_level_to_dxf(text, x1, x2, y1, y2, dxfattribs, block, scale)
	# add base level
	if ct.levels[0] > 0:
		text = f"Base = +{ct.levels[0] / ct.v_scale / 1000:.2f}"
	else:
		text = f"Base = {ct.levels[0] / ct.v_scale / 1000:.2f}"
	base_plate = FreeCAD.ActiveDocument.getObject(ct.base_plate_name[0])
	y1 = base_plate.Shape.BoundBox.ZMax * scale
	y2 = y1 + 30 * scale 
	add_level_to_dxf(text, x1, x2, y1, y2, dxfattribs, block, scale)

def add_nardebani_text_to_dxf(ct, dxfattribs, block, scale):
	for name in ct.nardebani_names:
		o = FreeCAD.ActiveDocument.getObject(name)
		x = o.Base.Shape.BoundBox.Center.x * scale
		y = (o.Base.Shape.BoundBox.Center.z + o.NumberZ // 2 * o.IntervalZ.z) * scale
		block.add_blockref("nardebani", (x, y), dxfattribs={
        'xscale': scale,
        'yscale': scale},
        )
		x2 = x - 600 * scale
		block.add_text(
        	f"PL200*150",
			dxfattribs = dxfattribs).set_pos(
			(x2, y),
			align="BOTTOM_LEFT",
			)
		block.add_text(
        	f"N={o.NumberZ}",
			dxfattribs = dxfattribs).set_pos(
			(x2, y - 10 * scale),
			align="TOP_LEFT",
			)

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

show_visible_edges = False		
view_scale = 1
page = FreeCAD.ActiveDocument.addObject('TechDraw::DrawPage', 'Page')
FreeCAD.ActiveDocument.addObject('TechDraw::DrawSVGTemplate', 'Template')
templateFileSpec = join(dirname(abspath(__file__)),"templates", "A0_Landscape_blank.svg")
FreeCAD.ActiveDocument.Template.Template = templateFileSpec
FreeCAD.ActiveDocument.Page.Template = FreeCAD.ActiveDocument.Template
page.ViewObject.show()

dxf_temp = join(dirname(abspath(__file__)), "templates", "TEMPLATE.DXF")
doc = ezdxf.readfile(dxf_temp)
msp = doc.modelspace()
# doc.layers.new(name='COL')
# doc.layers.new(name="Section")
# doc.layers.new(name="connection_ipe")
sc = 200 * view_scale
# line_types = [('DASHEDX2', 'Dashed (2x) ____  ____  ____  ____  ____  ____', [1.2, 1.0, -0.2]),
# 			('DASHED2', 'Dashed (.5x) _ _ _ _ _ _ _ _ _ _ _ _ _ _', [0.1 * sc, 0.1 * sc, -0.05 * sc])]
# for name, desc, pattern in line_types:
#     if name not in doc.linetypes:
#         doc.linetypes.new(name=name, dxfattribs={'description': desc, 'pattern': pattern})


cts = []
for o in FreeCAD.ActiveDocument.Objects:
	if hasattr(o, "base_plate_name"):
		cts.append(o)


for i, ct in enumerate(cts, start=1):
	view = FreeCAD.ActiveDocument.addObject('TechDraw::DrawViewPart','View')
	view.HardHidden = show_visible_edges
	view.ViewObject.LineWidth = .005
	view.ViewObject.HiddenWidth = .001
	# view.Direction = (1, 0, 0)
	# view.Direction = (1, -1 , .2)
	view.Direction = (0, -1, 0)
	# view.XDirection = (0, 0, 1)
	# view.SmoothVisible = True
	# view.Perspective = True
	# names = ct.front_draw_sources_name + ct.sections_obj_name
	names = [ct.ipe_name] + ct.flang_plates_name + ct.base_plate_name + ct.nardebani_names + \
		ct.connection_ipes_name + ct.souble_ipes_name + ct.neshimans_name

	view.Source = [FreeCAD.ActiveDocument.getObject(name) for name in names]
	page.addView(view)
	view.Scale = view_scale
	FreeCAD.ActiveDocument.recompute()
	# Gui.runCommand('TechDraw_ToggleFrame',0)
	visible_edges = view.getVisibleEdges()
	h = FreeCAD.ActiveDocument.getObject(ct.ipe_name).Height.Value * view.Scale
	e = visible_edges[0]
	comp = e.generalFuse(visible_edges[1:])
	visible_edges = comp[0].Edges
	hidden_edges = view.getHiddenEdges()
	if hidden_edges:
		hidden_edges = get_unique_edges(hidden_edges, ct, view.Scale, h)
		e = hidden_edges[0]
		comp = e.generalFuse(hidden_edges[1:])
		hidden_edges = comp[0].Edges

	es = Part.Compound(visible_edges + hidden_edges)
	ymin_view = es.BoundBox.YMin
	base_plate = FreeCAD.ActiveDocument.getObject(ct.base_plate_name[0])
	zmin_ct = base_plate.Shape.BoundBox.ZMin
	y = zmin_ct * view.Scale - ymin_view


	# add column type text
	text_height = 30 * view.Scale
	x = (ct.Placement.Base.x) * view.Scale
	msp.add_text(f"C{i}",
		dxfattribs = {'color': 6, "height": 2 * text_height, 'style': 'ROMANT'}).set_pos(
			(x, zmin_ct - 50 * view.Scale),
			align="TOP_CENTER",
			)

	for i, name in enumerate(ct.sections_obj_name):
		add_section_edges_to_dxf(name, {'layer':"Section", 'color': 2}, msp, 0, view.Scale)



	# write connection ipe leader
	for name in ct.connection_ipes_name:
		add_leader_for_connection_ipe(
			name,
			{"layer": "connection_ipe", "color": 6, "height": text_height, 'style': 'ROMANT'},
			msp,
			view.Scale,
			)

	add_levels_to_dxf(
		ct,
		{"layer": "levels", "color": 6, "height": text_height, 'style': 'ROMANT'},
		msp,
		view.Scale,
		)
	add_nardebani_text_to_dxf(
		ct,
		{"layer": "nardebani_text", "color": 6, "height": text_height, 'style': 'ROMANT'},
		msp,
		view.Scale
		)

	# block = doc.blocks.new(name = ct.Name)
	add_edges_to_dxf(visible_edges, {'layer':"COL"}, msp, x, y)
	add_edges_to_dxf(hidden_edges, {'layer':"COL", "linetype":"DASHED2", "lineweight": 13}, msp, x, y)

	# msp.add_blockref(ct.Name, (x * view.Scale, 0))
doc.set_modelspace_vport(height=1000, center=(0, 0))
doc.saveas("/home/ebi/alaki/ezdxf.dxf")

FreeCAD.ActiveDocument.removeObject(page.Name)


