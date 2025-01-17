import csv
import FreeCAD, FreeCADGui
import Part
import Arch
import Draft

try:
    from PySide.QtWidgets import *
    from PySide.QtCore import *
    from PySide.QtGui import *
except ImportError:
    from PySide2.QtWidgets import *
    from PySide2.QtCore import *
    from PySide2.QtGui import *

from FreeCAD import Base
from section import make_section, create_ipe, create_plate, create_neshiman
from columnTypeFunctions import (decompose_section_name, remove_obj,
                                find_empty_levels, find_nardebani_plate_levels)
import os
from os.path import join, dirname, abspath

import config

extra_row = 10
SIZE, PABAZ, BASELEVEL, EXTENDLENGTH, EXTENDPLATEABOVE, EXTENDPLATEBELOW, \
CONNECTIONIPELENGTH, CONNECTIONIPEABOVE, XPOS, NUMBER = range(extra_row)


class ColumnType:
    def __init__(self, obj):
        obj.Proxy = self
        self.set_properties(obj)

    def set_properties(self, obj):
        self.Type = "ColumnType"


        if not hasattr(obj, "size"):
            obj.addProperty(
                "App::PropertyEnumeration",
                "size",
                "IPE",
                )
            obj.size = ["14", "16", "18", "20", "22", "24", "27", "30"]

        if not hasattr(obj, "N"):
            obj.addProperty(
                "App::PropertyInteger",
                "N",
                "column_type",
                ).N = 1

        if not hasattr(obj, "pa_baz"):
            obj.addProperty(
                "App::PropertyBool",
                "pa_baz",
                "IPE",
                )

        if not hasattr(obj, "Placement"):
            obj.addProperty(
                "App::PropertyPlacement",
                "Placement",
                "Base",
                )

        if not hasattr(obj, "level_obj"):
            obj.addProperty(
                "App::PropertyLink",
                "level_obj",
                "Levels",
                )
        obj.setEditorMode("level_obj", 1)
        
        if not hasattr(obj, "heights"):
            obj.addProperty(
                "App::PropertyFloatList",
                "heights",
                "column_type",
            )

        if not hasattr(obj, "levels_name"):
            obj.addProperty(
                "App::PropertyStringList",
                "levels_name",
                "Levels",
            )
        obj.setEditorMode("levels_name", 1)

        if not hasattr(obj, "levels"):
            obj.addProperty(
                "App::PropertyFloatList",
                "levels",
                "Levels",
            )
        obj.setEditorMode("levels_name", 1)

        if not hasattr(obj, "levels_state"):
            obj.addProperty(
                "App::PropertyIntegerList",
                "levels_state",
                "Levels",
                )
        # obj.setEditorMode("levels_index", 1)


        if not hasattr(obj, "base_level"):
            obj.addProperty(
                "App::PropertyFloat",
                "base_level",
                "Levels",
            )

        if not hasattr(obj, "childrens_name"):
            obj.addProperty(
                "App::PropertyStringList",
                "childrens_name",
                "column_type",
                )
        obj.setEditorMode("childrens_name", 1)

        if not hasattr(obj, "front_draw_sources_name"):
            obj.addProperty(
                "App::PropertyStringList",
                "front_draw_sources_name",
                "views",
                )
        obj.setEditorMode("front_draw_sources_name", 2)

        if not hasattr(obj, "sections_name"):
            obj.addProperty(
                "App::PropertyStringList",
                "sections_name",
                "column_type",
            )

        if not hasattr(obj, "extend_length"):
            obj.addProperty(
                "App::PropertyFloat",
                "extend_length",
                "extend_lengths",
                )

        if not hasattr(obj, "extend_3ipe_len_below"):
            obj.addProperty(
                "App::PropertyFloat",
                "extend_3ipe_len_below",
                "extend_lengths",
                )

        if not hasattr(obj, "extend_plate_len_above"):
            obj.addProperty(
                "App::PropertyFloat",
                "extend_plate_len_above",
                "extend_lengths",
                )

        if not hasattr(obj, "extend_plate_len_below"):
            obj.addProperty(
                "App::PropertyFloat",
                "extend_plate_len_below",
                "extend_lengths",
                )

        if not hasattr(obj, "profile"):
            obj.addProperty(
                "App::PropertyLink",
                "profile",
                "IPE",
                )

        if not hasattr(obj, "v_scale"):
            obj.addProperty(
                "App::PropertyFloat",
                "v_scale",
                "column_type",
                ).v_scale = .25

        if not hasattr(obj, "composite_deck"):
            obj.addProperty(
                "App::PropertyBool",
                "composite_deck",
                "Deck",
                ).composite_deck = True

        if not hasattr(obj, "ipe_name"):
            obj.addProperty(
                "App::PropertyString",
                "ipe_name",
                "childrens_name",
                )
        obj.setEditorMode("ipe_name", 1)

        if not hasattr(obj, "flang_plates_name"):
            obj.addProperty(
                "App::PropertyStringList",
                "flang_plates_name",
                "childrens_name",
                )
        obj.setEditorMode("flang_plates_name", 1)

        if not hasattr(obj, "web_plates_name"):
            obj.addProperty(
                "App::PropertyStringList",
                "web_plates_name",
                "childrens_name",
                )
        if not hasattr(obj, "side_plates_name"):
            obj.addProperty(
                "App::PropertyStringList",
                "side_plates_name",
                "childrens_name",
                )
        obj.setEditorMode("side_plates_name", 1)

        if not hasattr(obj, "connection_ipes_name"):
            obj.addProperty(
                "App::PropertyStringList",
                "connection_ipes_name",
                "childrens_name",
                )
        obj.setEditorMode("connection_ipes_name", 1)

        if not hasattr(obj, "souble_ipes_name"):
            obj.addProperty(
                "App::PropertyStringList",
                "souble_ipes_name",
                "childrens_name",
                )
        obj.setEditorMode("souble_ipes_name", 1)

        if not hasattr(obj, "base_plate_name"):
            obj.addProperty(
                "App::PropertyStringList",
                "base_plate_name",
                "childrens_name",
                )
        obj.setEditorMode("base_plate_name", 1)

        if not hasattr(obj, "neshimans_name"):
            obj.addProperty(
                "App::PropertyStringList",
                "neshimans_name",
                "childrens_name",
                )
        obj.setEditorMode("neshimans_name", 1)

        if not hasattr(obj, "nardebani_names"):
            obj.addProperty(
                "App::PropertyStringList",
                "nardebani_names",
                "childrens_name",
                )
        obj.setEditorMode("nardebani_names", 1)

        if not hasattr(obj, "sections_obj_name"):
            obj.addProperty(
                "App::PropertyStringList",
                "sections_obj_name",
                "childrens_name",
                )
        obj.setEditorMode("sections_obj_name", 1)

        if not hasattr(obj, "nardebani_plate_size"):
            obj.addProperty(
                "App::PropertyFloatList",
                "nardebani_plate_size",
                "column_type",
                )

        if not hasattr(obj, "connection_ipe_lengths"):
            obj.addProperty(
                "App::PropertyFloatList",
                "connection_ipe_lengths",
                "Connection_IPE",
                ).connection_ipe_lengths = [1., 0.5]

        


    def execute(self, obj):
        RED = (1.0, 0.0, 0.0)
        GREEN = (0., 1., 0.)
        BLUE = (0.0, 0.0, 1.0)

        scale = 1000 * obj.v_scale

        levels = []
        for i, state in enumerate(obj.levels_state):
            if state:
                levels.append(obj.level_obj.levels[i])
                last_level_index = i

        simplify_sections_name = []
        simplify_levels =[]
        for i, section_name in enumerate(obj.sections_name):
            if obj.levels_state[i]:
                
                if simplify_sections_name:
                    if section_name != simplify_sections_name[-1]:
                        if i != last_level_index:
                            simplify_sections_name.append(section_name)
                        simplify_levels.append(obj.level_obj.levels[i] * scale)
                else:
                    simplify_sections_name.append(section_name)
                    simplify_levels.append(obj.level_obj.levels[i] * scale)
        if simplify_levels[-1] != obj.level_obj.levels[last_level_index] * scale:
            simplify_levels.append(obj.level_obj.levels[last_level_index] * scale)

        obj.base_level = levels[0]
        heights = []
        for i in range(len(levels[:-1])):
            heights.append(levels[i + 1] - levels[i])
        obj.heights = heights
        obj.levels = [lev  * scale for lev in levels]


        merge_flang_plates = []
        merge_flang_levels = [simplify_levels[0]]
        merge_web_plates = []
        merge_web_levels = [simplify_levels[0]]
        merge_side_plates = []
        merge_side_levels = [simplify_levels[0]]
        souble_ipes = []
        souble_ipe_levels = [simplify_levels[0]]

        for i, name in enumerate(simplify_sections_name):
            n, _, flang_plate, web_plate, side_plate, _ = decompose_section_name(name)
            if flang_plate or (i == len(simplify_sections_name) - 1):
                extend_button_flang_length = obj.extend_plate_len_above * scale
            else:
                extend_button_flang_length = -obj.extend_plate_len_below * scale

            level = simplify_levels[i + 1] + extend_button_flang_length
            if merge_flang_plates:
                if flang_plate != merge_flang_plates[-1]:
                    merge_flang_plates.append(flang_plate)
                    merge_flang_levels.append(level)
                else:
                    merge_flang_levels[-1] = level
            else:
                merge_flang_plates.append(flang_plate)
                merge_flang_levels.append(level)
            

            if web_plate:
                extend_button_web_length = obj.extend_plate_len_above * scale
            else:
                extend_button_web_length = -obj.extend_plate_len_below * scale

            level = simplify_levels[i + 1] + extend_button_web_length
            if merge_web_plates:
                if web_plate != merge_web_plates[-1]:
                    merge_web_plates.append(web_plate)
                    merge_web_levels.append(level)
                else:
                    merge_web_levels[-1] = level
            else:
                merge_web_plates.append(web_plate)
                merge_web_levels.append(level)
            
            
            if side_plate:
                extend_button_side_length = obj.extend_plate_len_above * scale
            else:
                extend_button_side_length = -obj.extend_plate_len_below * scale

            level = simplify_levels[i + 1] + extend_button_side_length
            if merge_side_plates:
                if side_plate != merge_side_plates[-1]:
                    merge_side_plates.append(side_plate)
                    merge_side_levels.append(level)
                else:
                    merge_side_levels[-1] = level
            else:
                merge_side_plates.append(side_plate)
                merge_side_levels.append(level)

            if obj.pa_baz:
                if n == 3 or (i == len(simplify_sections_name) - 1):
                    extend_button_ipe_length = obj.extend_length * scale
                else:
                    extend_button_ipe_length = -obj.extend_3ipe_len_below * scale

                level = simplify_levels[i + 1] + extend_button_ipe_length
                if souble_ipes:
                    if n != souble_ipes[-1]:
                        souble_ipes.append(n)
                        souble_ipe_levels.append(level)
                    else:
                        souble_ipe_levels[-1] = level
                else:
                    souble_ipes.append(n)
                    souble_ipe_levels.append(level)

        # create main IPE structures
        ipe_shapes, edges, bf, d, tf, tw, bw, bh, bt, bdist = self.make_profile(obj)
        obj.nardebani_plate_size = [bw, bh, bt, bdist]
        ipe = ipe_shapes[0]
        edge = edges[0]
        ipe_section_obj = FreeCAD.ActiveDocument.addObject("Part::FeaturePython", "ipe_section")
        ipe_section_obj.Shape = Part.makeCompound(ipe_shapes)
        IPE = Arch.makeStructure(ipe_section_obj, name="IPE")
        IPE.IfcType = "Column"
        h = simplify_levels[-1] - simplify_levels[0] + obj.extend_length * scale
        IPE.Height = h
        IPE.Placement.Base = FreeCAD.Vector(0, 0, simplify_levels[0]) + obj.Placement.Base
        IPE.ViewObject.ShapeColor = RED
        obj.Shape = IPE.Shape

        # souble ipe creation
        souble_ipes_name = []
        if obj.pa_baz:
            souble_ipe_section = ipe.copy()
            for i, n in enumerate(souble_ipes):
                if n == 3:
                    souble_ipe_section.Placement.Base = FreeCAD.Vector(0, 0, souble_ipe_levels[i]) + obj.Placement.Base
                    souble_ipe_section_obj = FreeCAD.ActiveDocument.addObject("Part::FeaturePython", "ipe")
                    souble_ipe_section_obj.Shape = souble_ipe_section
                    souble_ipe_obj = Arch.makeStructure(souble_ipe_section_obj, name="IPE")
                    souble_ipe_obj.IfcType = "Column"
                    h = souble_ipe_levels[i + 1] - souble_ipe_levels[i]
                    souble_ipe_obj.Height = h
                    souble_ipe_obj.ViewObject.ShapeColor = (.80, 0.0, 0.0)
                    souble_ipes_name.append(souble_ipe_obj.Name)

        flang_plates_name = []
        connection_ipes = []
        neshiman_levels = []
        neshimans_name = []
        if obj.composite_deck:
            neshiman_base_z = 0
        else:
            neshiman_base_z = 100 * obj.v_scale * 2

        front_draw_sources_name = []
        for i, plate in enumerate(merge_flang_plates):
            if plate:
                width = plate[0]
                height = plate[1]
                y = (d + height) / 2
                plt, edge = create_plate(width, height)
                plt.Placement.Base = FreeCAD.Vector(0, y, merge_flang_levels[i]) + obj.Placement.Base
                plb = plt.copy()
                plb.Placement.Base = FreeCAD.Vector(0, -y, merge_flang_levels[i]) + obj.Placement.Base
                palte_obj = FreeCAD.ActiveDocument.addObject("Part::FeaturePython", "Flang_Plate")
                palte_obj.Shape = Part.makeCompound([plt, plb])
                PLATE = Arch.makeStructure(palte_obj)
                PLATE.IfcType = "Plate"
                h = merge_flang_levels[i + 1] - merge_flang_levels[i]
                PLATE.Height = h
                PLATE.ViewObject.ShapeColor = BLUE
                flang_plates_name.append(PLATE.Name)

                plb_edge = edge.copy()
                plb_edge.Placement.Base = FreeCAD.Vector(0, -y, merge_flang_levels[i]) + obj.Placement.Base
                line = FreeCAD.ActiveDocument.addObject("Part::FeaturePython", "line")
                line.Shape = plb_edge
                plb_draw = FreeCAD.ActiveDocument.addObject('Part::Extrusion','plate_draw')
                plb_draw.Base = line
                plb_draw.Dir = FreeCAD.Vector(0, 0, 1)
                plb_draw.LengthFwd = h
                plb_draw.ViewObject.ShapeColor = BLUE
                front_draw_sources_name.append(plb_draw.Name)

        nardebani_names = []
        if obj.pa_baz:
            empty_levels = find_empty_levels(souble_ipes_name, levels, scale)
            if empty_levels:
                connection_ipe_section = ipe.copy()
                connection_ipe_edge = edges[0].copy()
                for lev in empty_levels:
                    connection_ipe_section.Placement.Base = IPE.Placement.Base
                    connection_ipe_edge.Placement.Base = IPE.Placement.Base
                    if lev != simplify_levels[0]:
                        below_len = obj.connection_ipe_lengths[0] - obj.connection_ipe_lengths[1]
                        connection_ipe_section.Placement.Base.z = lev - below_len * scale
                        connection_ipe_edge.Placement.Base.z = lev - below_len * scale


                    connection_ipe_section_obj = FreeCAD.ActiveDocument.addObject("Part::FeaturePython", "ipe")
                    connection_ipe_section_obj.Shape = connection_ipe_section
                    connection_ipe_obj = Arch.makeStructure(connection_ipe_section_obj)
                    connection_ipe_obj.IfcType = "Column"
                    connection_ipe_obj.Height = obj.connection_ipe_lengths[0] * scale
                    connection_ipe_obj.ViewObject.ShapeColor = (.80, 0.0, 0.0)
                    connection_ipes.append(connection_ipe_obj.Name)

                    line = FreeCAD.ActiveDocument.addObject("Part::FeaturePython", "line")
                    line.Shape = connection_ipe_edge
                    connection_ipe_draw = FreeCAD.ActiveDocument.addObject('Part::Extrusion','connection_ipe_draw')
                    connection_ipe_draw.Base = line
                    connection_ipe_draw.Dir = FreeCAD.Vector(0, 0, 1)
                    connection_ipe_draw.LengthFwd = obj.connection_ipe_lengths[0] * scale
                    front_draw_sources_name.append(connection_ipe_draw.Name)


        # draw plate for pa_baz column (nardebani)
            connection_flangs_3ipes = connection_ipes + flang_plates_name + souble_ipes_name
            nardebani_levels = find_nardebani_plate_levels(connection_flangs_3ipes)
            bb = ipe_section_obj.Shape.BoundBox
            width = bw
            height = bt
            plate_height = bh * obj.v_scale
            y = (d + height) / 2
            for lev in nardebani_levels:
                z1 = lev[0]
                z2 = lev[1]
                h = z2 - z1
                if h > 0:
                    space = bdist / 1000 * scale
                    n_z = int(h // space) - 1
                    free_space = h - ((n_z - 1) * space + plate_height)
                    z1 += free_space / 2
                    plt, _ = create_plate(width, height)
                    plt.Placement.Base = FreeCAD.Vector(0, y, z1) + obj.Placement.Base
                    plb = plt.copy()
                    plb.Placement.Base = FreeCAD.Vector(0, -y, z1) + obj.Placement.Base
                    palte_obj = FreeCAD.ActiveDocument.addObject("Part::FeaturePython", "Flang_Plate")
                    palte_obj.Shape = Part.makeCompound([plt, plb])
                    PLATE = Arch.makeStructure(palte_obj)
                    PLATE.IfcType = "Plate"
                    PLATE.Height = plate_height
                    PLATE.ViewObject.ShapeColor = (0.0, 0.0, 1.0)
                    _obj_ = Draft.make_ortho_array(PLATE, v_z=FreeCAD.Vector(0.0, 0.0, space), n_x=1, n_y=1, n_z=n_z)
                    nardebani_names.append(_obj_.Name)

        web_plates_name = []
        for i, plate in enumerate(merge_web_plates):
            if plate:
                width = plate[0]
                height = plate[1]
                x = ipe.Placement.Base.x + (tw + height) / 2
                plwr, _ = create_plate(height, width)
                plwr.Placement.Base = FreeCAD.Vector(x, 0, merge_web_levels[i]) + obj.Placement.Base
                plwl = plwr.copy(False)
                plwl.Placement.Base = FreeCAD.Vector(-x, 0, merge_web_levels[i]) + obj.Placement.Base
                palte_obj = FreeCAD.ActiveDocument.addObject("Part::FeaturePython", "web_Plate")
                palte_obj.Shape = Part.makeCompound([plwr, plwl])
                PLATE = Arch.makeStructure(palte_obj)
                PLATE.IfcType = "Plate"
                h = merge_web_levels[i + 1] - merge_web_levels[i]
                PLATE.Height = h
                PLATE.ViewObject.ShapeColor = (0.0, 1.0, 0.0)
                web_plates_name.append(PLATE.Name)
        side_plates_name = []
        for i, plate in enumerate(merge_side_plates):
            if plate:
                width = plate[0]
                height = plate[1]
                x = ipe.Placement.Base.x + (tw + bf) / 2
                plsr, _ = create_plate(height, width)
                plsr.Placement.Base = FreeCAD.Vector(x, 0, merge_side_levels[i]) + obj.Placement.Base
                plsl = plsr.copy(False)
                plsl.Placement.Base = FreeCAD.Vector(-x, 0, merge_side_levels[i]) + obj.Placement.Base
                palte_obj = FreeCAD.ActiveDocument.addObject("Part::FeaturePython", "side_Plate")
                palte_obj.Shape = Part.makeCompound([plsr, plsl])
                PLATE = Arch.makeStructure(palte_obj)
                PLATE.IfcType = "Plate"
                h = merge_side_levels[i + 1] - merge_side_levels[i]
                PLATE.Height = h
                PLATE.ViewObject.ShapeColor = (0.0, 1.0, 0.0)
                side_plates_name.append(PLATE.Name)

        #  insert BASE PLATE
        h = .02 * scale
        length = 400
        base_plate = Arch.makeStructure(length=length, width=length, height= h, name='BasePlate')
        base_plate.IfcType = "Plate"
        x = obj.Placement.Base.x - length / 2
        y = obj.Placement.Base.y
        z = obj.base_level * scale - h / 2 
        base_plate.Placement.Base = FreeCAD.Vector(x, y, z)
        base_plate.ViewObject.ShapeColor = (1.0, 0.0, 0.0)

        # draw sections
        sections_obj_name = []
        for i in range(len(obj.heights)):
            level = (levels[i] + obj.heights[i] / 2) * scale
            index = obj.level_obj.levels.index(levels[i])
            section = make_section(obj.sections_name[index], level=level, scale=obj.v_scale)
            section.Placement.Base = obj.Placement.Base
            section.Placement.Base.x += 500
            sections_obj_name.append(section.Name)


        h = 300 * obj.v_scale
        i_shape = create_neshiman(2 * bf / 3, h, 6, 8)
        i_shape.Placement = FreeCAD.Placement(FreeCAD.Vector(0, -d / 2, 0) + obj.Placement.Base,
                FreeCAD.Rotation(FreeCAD.Vector(1, 0, 0), 90))
        if obj.composite_deck:
            i_shape.Placement.Base.z -= h / 2
        else:
            i_shape.Placement.Base.z += h / 2
        i_obj = FreeCAD.ActiveDocument.addObject("Part::FeaturePython", "ipe")
        i_obj.Shape = i_shape
        neshiman_obj = Arch.makeStructure(i_obj, name="IPE")
        neshiman_obj.IfcType = "Beam"
        h = 100
        neshiman_obj.Height = h
        neshiman_obj.ViewObject.ShapeColor = (.80, 0.0, 0.0)
        neshimans_name.append(neshiman_obj.Name)
        # Draft.scale(neshiman_obj, FreeCAD.Vector(1, 1, obj.v_scale * 2), copy=False)
        for lev in levels[2:]:
            neshiman_clone_obj = Arch.cloneComponent(neshiman_obj)
            neshiman_clone_obj.ViewObject.ShapeColor = (.80, 0.0, 0.0)
            neshiman_clone_obj.Placement.Base.z += lev * scale
            neshimans_name.append(neshiman_clone_obj.Name)
        
        neshiman_obj.Placement.Base.z += levels[1] * scale

        obj.ipe_name = IPE.Name
        obj.flang_plates_name = flang_plates_name
        obj.web_plates_name = web_plates_name
        obj.side_plates_name = side_plates_name
        obj.base_plate_name = [base_plate.Name]
        obj.connection_ipes_name = connection_ipes
        obj.neshimans_name = neshimans_name
        obj.souble_ipes_name = souble_ipes_name
        obj.nardebani_names = nardebani_names
        obj.sections_obj_name = sections_obj_name
        obj.front_draw_sources_name = front_draw_sources_name

        childrens_name = [IPE.Name] + flang_plates_name + web_plates_name + side_plates_name + nardebani_names + \
                        [base_plate.Name] + connection_ipes + neshimans_name + \
                        souble_ipes_name + sections_obj_name + front_draw_sources_name
        old_childrens_name = obj.childrens_name
        obj.childrens_name = childrens_name
        for name in old_childrens_name:
            remove_obj(name)
        obj.childrens_name = childrens_name

    
    def make_profile(self, obj):
        shapes = []
        edges = []
        sectionSize = int(obj.size)
        sectionType = "IPE"
        file_name = "Section_IPE.csv"
        with open(join(dirname(abspath(__file__)),"table",file_name),'r') as f:
            reader=csv.DictReader(f,delimiter=';')
            for row in reader:
                if row['SSIZE'] == f"IPE{sectionSize * 10}":
                    bf = float(row["BF"])
                    d = float(row["D"])
                    tw = float(row["TW"])
                    tf = float(row["TF"])
                    bw = float(row["BW"])
                    bh = float(row["BH"])
                    bt = float(row["BT"])
                    bdist = float(row["BDIST"])
                    break

        if obj.pa_baz:
            dist = bf
        else:
            dist = 0
        ipe, edge = create_ipe(bf, d, tw, tf)
        deltax = bf + dist
        ipe.Placement.Base.x = deltax / 2
        edge.Placement.Base.x = deltax / 2
        ipe2 = ipe.copy()
        ipe2.Placement.Base.x = -deltax / 2
        edge2 = edge.copy()
        edge2.Placement.Base.x = -deltax / 2
        shapes.extend([ipe, ipe2])
        edges.extend([edge, edge2])

        return shapes, edges, bf, d, tf, tw, bw, bh, bt, bdist


class ViewProviderColumnType:
    def __init__(self, obj):
        ''' Set this object to the proxy object of the actual view provider '''
        obj.Proxy = self

    def attach(self, vobj):
        self.ViewObject = vobj
        self.Object = vobj.Object

    def claimChildren(self):
        children=[FreeCAD.ActiveDocument.getObject(name) for name in self.Object.childrens_name]
        return children

    def getIcon(self):
        return join(dirname(abspath(__file__)),"Resources", "icons","column.png")

    def setEdit(self, vobj, mode=0):
        obj = vobj.Object
        ui = Ui(obj)
        ui.setupUi()
        FreeCADGui.Control.showDialog(ui)
        return True

    def onDelete(self,vobj,subelements):
        remove_column(vobj.Object)
        return True


    def unsetEdit(self, vobj, mode):
        FreeCADGui.Control.closeDialog()
        return

    def __getstate__(self):
        return None

    def __setstate__(self, state):
        return None


def make_column_type(
        levels_state,
        sections_name,
        level_obj,
        size=16,
        pa_baz=False,
        extend_length=.8,
        extend_3ipe_len_below=.8,
        extend_plate_len_above=.8,
        extend_plate_len_below=.8,
        connection_ipe_lengths=[1., .5],
        pos=(0, 0),
        N=1,
        ):

    obj = FreeCAD.ActiveDocument.addObject("Part::FeaturePython", "column_type")
    ColumnType(obj)
    ViewProviderColumnType(obj.ViewObject)
    obj.levels_state = levels_state
    obj.level_obj = level_obj
    n = len(level_obj.columns_names)
    obj.Label = f"C{n + 1}"
    obj.sections_name = sections_name
    obj.extend_length = extend_length
    obj.extend_3ipe_len_below = extend_3ipe_len_below
    obj.extend_plate_len_above = extend_plate_len_above
    obj.extend_plate_len_below = extend_plate_len_below
    position = FreeCAD.Vector(pos[0], pos[1], 0)
    obj.Placement.Base = position
    obj.size = str(size)
    obj.pa_baz = pa_baz
    obj.connection_ipe_lengths = connection_ipe_lengths
    obj.N = N
    return obj


class ColumnTableModel(QAbstractTableModel):

    def __init__(self, level_obj):
        super().__init__()
        self.level_obj = level_obj
        self.levels_name = []
        self.sections_name = []
        self.levels_state = []

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if role == Qt.TextAlignmentRole:
            if orientation == Qt.Horizontal:
                return int(Qt.AlignHCenter | Qt.AlignVCenter)
            return int(Qt.AlignRight | Qt.AlignVCenter)
        if role != Qt.DisplayRole:
            return

        if orientation == Qt.Horizontal:
            if section == 0:
                return "Story"
            if section == 1:
                return "Section"

        if orientation == Qt.Vertical:
            return str(section)

    def checkState(self, row):
        if self.levels_state[row]:
            return Qt.Checked
        else:
            return Qt.Unchecked

    def flags(self, index):
        if not index.isValid():
            return Qt.ItemIsEnabled
        col = index.column()
        if col == 0:
            return Qt.ItemIsEnabled | Qt.ItemIsUserCheckable

        return Qt.ItemFlags(
            QAbstractTableModel.flags(self, index) | Qt.ItemIsEditable)

    def data(self, index, role=Qt.DisplayRole):

        if not index.isValid():
            return
        row = index.row()
        col = index.column()
        if role == Qt.DisplayRole:
            if col == 0:
                return self.levels_name[row]
            elif col == 1:
                return self.sections_name[row]
        if role == Qt.CheckStateRole and col == 0:
            return self.checkState(row)
        return None

    def setData(self, index, value, role=Qt.EditRole):
        if not index.isValid():
            return False
        col = index.column()
        row = index.row()
        if role == Qt.CheckStateRole and col == 0:
            self.levels_state[row] = value
            self.dataChanged.emit(index, index)
            return True
        if role == Qt.EditRole and col == 1:
            self.sections_name[row] = str(value)
            self.dataChanged.emit(index, index)
            return True
        return False

    def rowCount(self, index=QModelIndex()):
        return len(self.levels_name)

    def columnCount(self, index=QModelIndex()):
        return 2



class ColumnDelegate(QItemDelegate):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.ui = parent

    def createEditor(self, parent, option, index):
        col = index.column()
        if col == 1:
            combobox = QComboBox(parent)
            size = self.ui.ipe_size.currentText()
            sections = index.model().level_obj.sections_name
            sections_with_current_size = [section for section in sections if f"IPE{size}" in section]
            if not sections_with_current_size:
                sections_with_current_size = [f"2IPE{size}"]
            combobox.addItems(sections_with_current_size)
            # combobox.setEditable(True)
            return combobox
        else:
            return QItemDelegate.createEditor(self, parent, option, index)

    # def setEditorData(self, editor, index):
    #     row = index.row()
    #     col = index.column()
    #     # value = index.model().items[row][column]
    #         editor.setCurrentIndex(index.row())

    def setModelData(self, editor, model, index):
        col = index.column()
        if col == 1:
            model.setData(index, editor.currentText())

    def sizeHint(self, option, index):
        fm = option.fontMetrics
        return QSize(fm.width("2IPE14FPL200X10WPL200X10"), fm.height())



class Ui:
    def __init__(self, col_obj=None):
        self.form = FreeCADGui.PySideUic.loadUi(os.path.join(
            os.path.dirname(__file__), 'Resources/ui/column.ui'))
        self.col_obj = col_obj

    def setupUi(self):
        self.add_connections()
        self.level_obj = FreeCAD.ActiveDocument.Levels
        self.model = ColumnTableModel(self.level_obj)
        json_file=os.path.join(FreeCAD.getUserAppDataDir(), 'column.json')
        self.model.levels_name = FreeCAD.ActiveDocument.Levels.levels_name
        if not self.col_obj:
            self.load_config(json_file)
            size = self.form.ipe_size.currentText()
            self.model.sections_name = [f"2IPE{size}"] * (len(self.model.levels_name))
            self.model.levels_state = [1] * len(self.model.levels_name)
        else:
            self.fill_form(self.col_obj)
            self.model.sections_name = self.col_obj.sections_name
            self.model.levels_state = self.col_obj.levels_state

        # self.set_levels_name()
        self.form.tableView.setModel(self.model)
        self.form.tableView.setItemDelegate(ColumnDelegate(self.form))

    def resizeColumns(self, tableView=None):
        for column in (0, 1):
            self.form.tableView.resizeColumnToContents(column)

    def fill_form(self, col_obj):
        size = col_obj.size
        index = self.form.ipe_size.findText(size)
        N = col_obj.N
        extend_length = col_obj.extend_length
        extend_3ipe_len_below = col_obj.extend_3ipe_len_below
        extend_plate_len_above = col_obj.extend_plate_len_above
        extend_plate_len_below = col_obj.extend_plate_len_below
        connection_ipe_length = col_obj.connection_ipe_lengths[0]
        connection_ipe_above = col_obj.connection_ipe_lengths[1]
        self.form.ipe_size.setCurrentIndex(index)
        self.form.extend_length.setValue(float(extend_length))
        self.form.extend_3ipe_len_below.setValue(float(extend_3ipe_len_below))
        self.form.extend_plate_len_above.setValue(float(extend_plate_len_above))
        self.form.extend_plate_len_below.setValue(float(extend_plate_len_below))
        self.form.connection_ipe_length.setValue(float(connection_ipe_length))
        self.form.connection_ipe_above.setValue(float(connection_ipe_above))
        self.form.number.setValue(int(N))


    def add_connections(self):
        self.form.ipe_size.currentIndexChanged.connect(self.reset_model)

    def reset_model(self):
        self.model.beginResetModel()
        sections_name = []
        for row in range(self.model.rowCount()):
            index = self.model.index(row, 1)
            name = self.model.data(index)
            size = self.form.ipe_size.currentText()
            name = f"{name[:4]}{size}{name[6:]}"
            sections_name.append(name)
        self.model.sections_name = sections_name
        self.model.endResetModel()


    def load_config(self, json_file):
        if os.path.exists(json_file):
            config.load(self.form, json_file)

    def accept(self):
        self.save_config()
        self.add_column()
        FreeCADGui.Control.closeDialog()

    def reject(self):
        FreeCADGui.Control.closeDialog()

    def save_config(self):
        json_file = os.path.join(FreeCAD.getUserAppDataDir(), 'column.json')
        config.save(self.form, json_file)

    def add_column(self):
        # self.model.beginResetModel()
        ipe_size = int(self.form.ipe_size.currentText())
        sections_name = []
        levels_state = self.model.levels_state
        for row in range(self.model.rowCount()):
            index = self.model.index(row, 1)
            name = self.model.data(index)
            sections_name.append(name)
        if not self.col_obj:
            dx = self.form.deltax.value()
            if len(self.level_obj.columns_names) >= 1:
                last_column_name = self.level_obj.columns_names[-1]
                last_col = FreeCAD.ActiveDocument.getObject(last_column_name)
                x = last_col.Placement.Base.x + dx * 1000
            else:
                x = 0
        else:
            x = self.col_obj.Placement.Base.x
        extend_length = self.form.extend_length.value()
        extend_3ipe_len_below = self.form.extend_3ipe_len_below.value()
        extend_plate_len_above = self.form.extend_plate_len_above.value()
        extend_plate_len_below = self.form.extend_plate_len_below.value()
        connection_ipe_length = self.form.connection_ipe_length.value()
        connection_ipes_above_length = self.form.connection_ipe_above.value()
        firs_section = sections_name[0]
        pa_baz = firs_section.endswith("CC")
        if firs_section.startswith("3"):
            pa_baz = True
        pos = (x, 0)
        N = self.form.number.value()
        if bool(self.col_obj):
            self.col_obj.levels_state = levels_state
            self.col_obj.sections_name = sections_name
            self.col_obj.size = str(ipe_size)
            self.col_obj.extend_length = extend_length
            self.col_obj.extend_3ipe_len_below = extend_3ipe_len_below
            self.col_obj.pa_baz = pa_baz
            self.col_obj.connection_ipe_lengths = [connection_ipe_length, connection_ipes_above_length]
            self.col_obj.extend_plate_len_above = extend_plate_len_above
            self.col_obj.extend_plate_len_below = extend_plate_len_below
            self.col_obj.N = N
            FreeCAD.ActiveDocument.recompute()
            FreeCAD.ActiveDocument.recompute()
            return


        col = make_column_type(
            levels_state,
            sections_name,
            self.level_obj,
            size=ipe_size,
            extend_length=extend_length,
            extend_3ipe_len_below = extend_3ipe_len_below,
            pos=pos,
            pa_baz=pa_baz,
            connection_ipe_lengths=[connection_ipe_length, connection_ipes_above_length],
            extend_plate_len_above=extend_plate_len_above,
            extend_plate_len_below=extend_plate_len_below,
            N=N,
            )
        col_names = self.level_obj.columns_names
        col_names.append(col.Name)
        self.level_obj.columns_names = col_names
        self.level_obj.Proxy.execute(self.level_obj)
        FreeCAD.ActiveDocument.recompute()
        FreeCAD.ActiveDocument.recompute()
        # self.model.endResetModel()


def remove_column(col_obj=None, move_other=True):
    if not col_obj:
        col_obj = FreeCADGui.Selection.getSelection()[0]
    col_name = col_obj.Name
    Levels = FreeCAD.ActiveDocument.Levels
    col_names = Levels.columns_names
    x_placements = []
    for name in col_names:
        col = FreeCAD.ActiveDocument.getObject(name)
        x_placements.append(col.Placement.Base.x)
    i = col_names.index(col_name)
    for name in col_obj.childrens_name:
        remove_obj(name)
    col_names.remove(col_name)

    if move_other:
        if len(x_placements) > i + 1:
            deltax = x_placements[i + 1] - x_placements[i]
        else:
            deltax = 0
        x_placements.remove(x_placements[i])
        if len(x_placements) > 0:
            for j, x in enumerate(x_placements[i:]):
                x_placements[i + j] -= deltax

    FreeCAD.ActiveDocument.removeObject(col_name)
    Levels.columns_names = col_names

    if move_other:
        for i, name in enumerate(col_names):
            col_obj = FreeCAD.ActiveDocument.getObject(name)
            col_obj.Placement.Base.x = x_placements[i]
        FreeCAD.ActiveDocument.recompute()
        FreeCAD.ActiveDocument.recompute()

def create_columns():
    ui = Ui()
    # ui.setupUi()
    # ui.form.exec_()
    FreeCADGui.Control.showDialog(ui)
    if ui.setupUi():
        FreeCADGui.Control.closeDialog(ui)
    FreeCAD.ActiveDocument.recompute()


if __name__ == '__main__':
    # create_columns()
    make_column_type(
        [4, 3.2, 3.2, 3.2, 3.3, 5],
        ['2IPE30FPL200x8WPL200x5SPL200X10', '2IPE30FPL200x8WPL200x5SPL200X10', '2IPE30FPL200x8','2IPE30FPL200x8', '2IPE30WPL200x5', '2IPE30WPL200x5'],
        level_obj=-1.2,
        size="30",
        )

    # make_column_type([4, 3.2, 3.2, 3.2, 3.3, 5], ['2IPE24PL300x8w200x5', '2IPE24PL250x8w200x5', '2IPE24PL200x8','2IPE24PL200x8', '2IPE24w150x5', '2IPE24w150x5'], base_level=-1.2, pos=(2000, 0), size="24", pa_baz=True)
    # make_column_type([4, 3.2, 3.2, 3.2, 3.3, 5], ['2IPE24w200x5', '2IPE24PL250x8w200x5', '2IPE24PL200x8','2IPE24PL200x8', '2IPE24w150x5', '2IPE24w150x5'], base_level=-1.2, pos=(4000, 0), size="24", pa_baz=True)
    # make_column_type([4, 3.2, 3.2, 3.2, 3.3, 5], ['2IPE14', '2IPE14', '2IPE14', '2IPE14', '2IPE14', '2IPE14'], base_level=-1.2, pos=(6000, 0), size="14", pa_baz=True)
    # make_column_type([4, 3.2, 3.2, 3.2, 3.3, 5, 3, 3], ['3IPE18PL310x10w140x8', '3IPE18PL310x10', '3IPE18PL310x8', '3IPE18PL230x8', '3IPE18PL230x6', '3IPE18', '3IPE18', '3IPE18'], base_level=-1.2, pos=(8000, 0), size="18", pa_baz=True)
    # make_column_type([4, 3.2, 3.2, 3.2, 3.3, 5, 3, 3], ['2IPE18PL310x10w140x8', '2IPE18PL310x10', '2IPE18PL310x8', '2IPE18PL230x8', '2IPE18PL230x6', '2IPE18PL230x6', '2IPE18PL230x6', '2IPE18PL230x6w140x8'], base_level=-1.2, pos=(10000, 0), size="18", pa_baz=True)

    # make_column_type([4, 3.2, 3.2, 3.2, 3.3, 5, 3, 3], ['2IPE18PL310x10w140x8', '3IPE18PL310x10', '3IPE18', '2IPE18', '3IPE18PL310x10', '2IPE18', '2IPE18', '2IPE18'], base_level=-1.2, pos=(12000, 0), size="18", pa_baz=True)
    
    # make_column_type([4, 3.2, 3.2, 3.2, 3.3, 5, 3, 3], ['2IPE14', '3IPE14PL170x6', '3IPE14PL170x6', '3IPE14', '3IPE14', '3IPE14', '3IPE14', '3IPE14'], base_level=-1.2, pos=(14000, 0), size="14", pa_baz=True)
    # make_column_type([4, 3.2, 3.2, 3.2, 3.3, 5, 3, 3], ['2IPE14', '2IPE14', '2IPE14', '2IPE14', '2IPE14', '3IPE14', '3IPE14', '3IPE14'], base_level=-1.2, pos=(16000, 0), size="14", pa_baz=True)
    # make_column_type([4, 3.2, 3.2, 3.2, 3.3, 5, 3, 3], ['2IPE16', '3IPE16PL280x8', '3IPE16PL280x8', '3IPE16PL280x8', '3IPE16PL200x6', '3IPE16PL200x6', '3IPE16', '3IPE16'], base_level=-1.2, pos=(18000, 0), size="16", pa_baz=True)
    # FreeCAD.ActiveDocument.recompute()

    # FreeCADGui.ActiveDocument.ActiveView.viewFront()
    # FreeCADGui.SendMsgToActiveView("ViewFit")


