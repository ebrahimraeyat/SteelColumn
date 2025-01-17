from os.path import join, dirname, abspath
import copy
import string
import random

# import TechDraw
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

def add_section_edges_to_dxf(ct, dxfattribs, block, z, scale):
	dxfattribs_text = copy.deepcopy(dxfattribs)
	dxfattribs_text['height'] = 30 * scale
	dxfattribs_text['style'] = 'ROMANT'
	for i, name in enumerate(ct.sections_obj_name):
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
		x = (bb.XMax + bb.XMin) / 2 * scale
		y = bb.ZMin  * scale + z - 30 * scale
		block.add_text(f"{o.name[:6]}0",
						dxfattribs=dxfattribs_text).set_pos(
						(x, y),
						align="TOP_CENTER"
						)
		o_zmin = bb.ZMin
		if o.flang_plate_size:
			for flang_plate_name in ct.flang_plates_name:
				flang_plate = FreeCAD.ActiveDocument.getObject(flang_plate_name)
				flang_plate_bb = flang_plate.Shape.BoundBox
				zmax, zmin = flang_plate_bb.ZMax, flang_plate_bb.ZMin
				flang_plate_height = flang_plate.Height
				if zmin < o_zmin < zmax:
					h = round(int(flang_plate_height.Value / ct.v_scale), -1)
					break
			bf, tf = o.flang_plate_size
			y = bb.ZMax * scale + z + 20 * scale
			block.add_text(f"2PL{h}*{bf}*{tf}",
						dxfattribs=dxfattribs_text).set_pos(
						(x, y),
						align="BOTTOM_CENTER"
						)
			x = flang_plate_bb.Center.x * scale
			block.add_blockref("nardebani", (x, y), dxfattribs={
		        'xscale': scale,
		        'yscale': scale},
		        )
			x -= 600 * scale
			block.add_text(f"2PL{h}*{bf}*{tf}",
						dxfattribs=dxfattribs_text).set_pos(
						(x, y),
						align="BOTTOM_LEFT"
						)

		if o.web_plate_size:
			for web_plate_name in ct.web_plates_name:
				web_plate = FreeCAD.ActiveDocument.getObject(web_plate_name)
				web_plate_bb = web_plate.Shape.BoundBox
				zmax, zmin = web_plate_bb.ZMax, web_plate_bb.ZMin
				web_plate_height = web_plate.Height
				if zmin < o_zmin < zmax:
					h = round(int(web_plate_height.Value / ct.v_scale), -1)
					break
			bf, tf = o.web_plate_size
			y = (bb.ZMax + bb.ZMin) / 2 * scale + z
			x = bb.XMax * scale
			block.add_text(f"2PL{h}*{bf}*{tf}",
				dxfattribs=dxfattribs_text).set_pos(
				(x, y),
				align="MIDDLE_LEFT")
		
		if o.side_plate_size:
			for side_plate_name in ct.side_plates_name:
				side_plate = FreeCAD.ActiveDocument.getObject(side_plate_name)
				side_plate_bb = side_plate.Shape.BoundBox
				zmax, zmin = side_plate_bb.ZMax, side_plate_bb.ZMin
				side_plate_height = side_plate.Height
				if zmin < o_zmin < zmax:
					h = round(int(side_plate_height.Value / ct.v_scale), -1)
					break
			bf, tf = o.side_plate_size
			y = (bb.ZMax + bb.ZMin) / 2 * scale + z
			x = bb.XMax * scale
			block.add_text(f"2PL{h}*{bf}*{tf}",
				dxfattribs=dxfattribs_text).set_pos(
				(x, y),
				align="MIDDLE_LEFT")

		if all((o.pa_baz, not o.flang_plate_size, o.n==2)):
			bw, bh, bt, bdist = ct.nardebani_plate_size
			x = bb.Center.x * scale
			y = bb.ZMax * scale + z

			block.add_text(f"2PL{bw:.0f}*{bh:.0f}*{bt:.0f}@{bdist/10:.0f} Cm",
						dxfattribs=dxfattribs_text).set_pos(
						(x, y + 2 * bt * scale),
						align="BOTTOM_CENTER"
						)
			bw *= scale
			bt *= scale
			dxfattribs['xscale'] = bw
			dxfattribs['yscale'] = bt
			dxfattribs['ltscale'] = 0.3
			block.add_blockref("plate", (x, y), dxfattribs=dxfattribs)
			block.add_blockref("plate", (x, y - bb.ZLength * scale - bt), dxfattribs=dxfattribs)
			del(dxfattribs['xscale'])
			del(dxfattribs['yscale'])
			del(dxfattribs['ltscale'])

def add_connection_ipe_under_plate(ct, dxfattribs, block, x, y, scale, View, page):
	view = FreeCAD.ActiveDocument.addObject('TechDraw::DrawViewPart','View')
	view.HardHidden = True
	view.Direction = get_view_direction(View)
	view.Scale = scale
	names = ct.front_draw_sources_name
	view.Source = [FreeCAD.ActiveDocument.getObject(name) for name in names]
	page.addView(view)
	FreeCAD.ActiveDocument.recompute()
	hidden_edges = view.getHiddenEdges()
	add_edges_to_dxf(hidden_edges, dxfattribs, block, x, y)

def add_leader_for_connection_ipe(name, dxfattribs, block, view_scale, obj_scale):
	o = FreeCAD.ActiveDocument.getObject(name)
	center_of_mass = o.Shape.CenterOfMass
	y =  (o.Shape.BoundBox.ZMin + 20) * view_scale
	x1 = center_of_mass.x * view_scale
	x2 = x1 + 450 * view_scale
	block.add_blockref("connectionipe", (x1, y), dxfattribs={
        'xscale': view_scale,
        'yscale': view_scale},
        )
	size = int(o.Base.Shape.BoundBox.YLength)
	block.add_text(f"IPE{size}",
					dxfattribs=dxfattribs).set_pos(
					(x2, y),
					align="BOTTOM_RIGHT"
					)
	y =  (o.Shape.BoundBox.ZMin + 10) * view_scale
	h = int(o.Height.Value / 10 / obj_scale)
	block.add_text(f"L={h} cm",
					dxfattribs=dxfattribs).set_pos(
					(x2, y),
					align="TOP_RIGHT"
					)

def add_level_to_dxf(text, x1, x2, y1, y2, dxfattribs, block, scale):
	block.add_blockref("levelblock", (x2, y1), dxfattribs={
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
	t = "T.O.B" if ct.composite_deck else "B.O.B"
	for i, name in enumerate(ct.neshimans_name):
		o = FreeCAD.ActiveDocument.getObject(name)
		y1 = o.Shape.BoundBox.ZMax * scale
		if not ct.composite_deck:
			y1 -= 300 * ct.v_scale * scale
		y2 = y1 + 30 * scale
		level = f"{ct.levels[i + 1] / ct.v_scale / 1000:+06.2f}"
		text = f"{t} = {level}"
		add_level_to_dxf(text, x1, x2, y1, y2, dxfattribs, block, scale)
	# add base level
	level = f"{ct.levels[0] / ct.v_scale / 1000:+06.2f}"
	text = f"Base = {level}"
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
		bw, bh, bt, bdist = ct.nardebani_plate_size
		block.add_text(
        	f"PL{int(bw)}*{int(bh)}*{int(bt)}",
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

def get_save_filename(ext):
    try:
        from PySide.QtWidgets import QFileDialog
    except ImportError:
        from PySide2.QtWidgets import QFileDialog
    filters = f"{ext[1:]} (*{ext})"
    filename, _ = QFileDialog.getSaveFileName(None, 'select file',
                                              None, filters)
    if not filename:
        return
    if not ext in filename:
        filename += ext
    return filename

def get_view_direction(View):
	if View == "Flange":
		return (0, -1, 0)
	if View == "Web":
		return (1, 0, 0)
	if View == "3D":
		return (1, -1 , 0.2)

def export_to_dxf(filename, show_hidden_edges=False, View="Flange"):
	'''
	View can be "Flange", "Web" or "3D"
	'''

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
	sc = 200 * view_scale

	cts = []
	for o in FreeCAD.ActiveDocument.Objects:
		if hasattr(o, "base_plate_name"):
			cts.append(o)


	for i, ct in enumerate(cts, start=1):
		block_name = ''.join(random.choices(string.ascii_letters + string.digits, k=50))
		block = doc.blocks.new(name=block_name)
		view = FreeCAD.ActiveDocument.addObject('TechDraw::DrawViewPart','View')
		view.HardHidden = show_hidden_edges
		view.Direction = get_view_direction(View)

		names = [ct.ipe_name] + \
				ct.flang_plates_name + \
				(ct.web_plates_name if View != "Flange" else []) + \
				ct.side_plates_name + \
				ct.base_plate_name + \
				ct.nardebani_names + \
				ct.connection_ipes_name + \
				ct.souble_ipes_name + \
				ct.neshimans_name

		view.Source = [FreeCAD.ActiveDocument.getObject(name) for name in names]
		page.addView(view)
		view.Scale = view_scale
		FreeCAD.ActiveDocument.recompute()
		visible_edges = view.getVisibleEdges()
		h = FreeCAD.ActiveDocument.getObject(ct.ipe_name).Height.Value * view.Scale
		e = visible_edges[0]
		comp = e.generalFuse(visible_edges[1:])
		visible_edges = comp[0].Edges
		hidden_edges = []
		if show_hidden_edges:
			hidden_edges = view.getHiddenEdges()
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
		number = ct.N
		block.add_text(f"C{i}",
			dxfattribs = {'color': 6, "height": 2 * text_height, 'style': 'ROMANT'}).set_pos(
				(x, (zmin_ct - 150) * view.Scale),
				align="BOTTOM_CENTER",
				)
		block.add_text(f"N={number}",
			dxfattribs = {'color': 6, "height": 2 * text_height, 'style': 'ROMANT'}).set_pos(
				(x, (zmin_ct - 150) * view.Scale),
				align="TOP_CENTER",
				)
		dx = 150 * view.Scale
		y2 = (zmin_ct - 140) * view.Scale
		block.add_line((x - dx, y2), (x + dx, y2), dxfattribs = {'color': 6,})

		add_section_edges_to_dxf(ct, {'layer':"Section", 'color': 2}, block, 0, view.Scale)

		# write connection ipe leader
		for name in ct.connection_ipes_name:
			add_leader_for_connection_ipe(
				name,
				{"layer": "connection_ipe", "color": 6, "height": text_height, 'style': 'ROMANT'},
				block,
				view.Scale,
				ct.v_scale,
				)
		# adding ipe connection when show_hidden_edges is False
		if not show_hidden_edges:
			add_connection_ipe_under_plate(
				ct,
				{'layer':"COL", "linetype":"DASHED2", "lineweight": 13, "ltscale": .3},
				block,
				x,
				y,
				view.Scale,
				View,
				page
			)

		add_levels_to_dxf(
			ct,
			{"layer": "levels", "color": 6, "height": text_height, 'style': 'ROMANT'},
			block,
			view.Scale,
			)
		add_nardebani_text_to_dxf(
			ct,
			{"layer": "nardebani_text", "color": 6, "height": text_height, 'style': 'ROMANT'},
			block,
			view.Scale
			)

		add_edges_to_dxf(visible_edges, {'layer':"COL"}, block, x, y)
		add_edges_to_dxf(hidden_edges, {'layer':"COL", "linetype":"DASHED2", "lineweight": 13}, block, x, y)

		FreeCAD.ActiveDocument.removeObject(view.Name)
		msp.add_blockref(block_name, (0 , 0)).set_scale(.001 / ct.v_scale)
	height = int(len(cts) * view_scale)
	doc.set_modelspace_vport(height=height, center=(height, int(height/2)))
	doc.saveas(filename)
	FreeCAD.ActiveDocument.removeObject(page.Name)

if __name__ == '__main__':
	import tempfile
	from pathlib import Path
	temp_dir = tempfile.gettempdir()
	# export_to_dxf(str(Path(temp_dir) / 'ezdxf.dxf'))
	# export_to_dxf(str(Path(temp_dir) / 'ezdxf_web.dxf'), View='Web')
	export_to_dxf(str(Path(temp_dir) / 'ezdxf_web_show_hidden.dxf'), show_hidden_edges=True, View='Web')


