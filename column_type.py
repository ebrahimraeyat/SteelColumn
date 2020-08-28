import csv
import FreeCAD
import Part
import Arch
import Draft
from FreeCAD import Base
from section import make_section, create_ipe, create_plate
from columnTypeFunctions import decompose_section_name
from os.path import join, dirname, abspath

class ColumnType:
    def __init__(self, obj):
        obj.Proxy = self
        self.set_properties(obj)

    def set_properties(self, obj):
        self.Type = "ColumnType"

        if not hasattr(obj, "n"):
            obj.addProperty(
                "App::PropertyEnumeration",
                "n",
                "IPE",
                )
            obj.n = ['2', '3']

        if not hasattr(obj, "size"):
            obj.addProperty(
                "App::PropertyEnumeration",
                "size",
                "IPE",
                )
            obj.size = ["14", "16", "18", "20", "22", "24", "27", "30"]

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
        
        if not hasattr(obj, "heights"):
            obj.addProperty(
                "App::PropertyFloatList",
                "heights",
                "column_type",
            )

        if not hasattr(obj, "base_level"):
            obj.addProperty(
                "App::PropertyFloat",
                "base_level",
                "column_type",
            )

        if not hasattr(obj, "childrens_name"):
            obj.addProperty(
                "App::PropertyStringList",
                "childrens_name",
                "column_type",
                )
        obj.setEditorMode("childrens_name", 1)

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
                "column_type",
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
                ).v_scale = 1

    def execute(self, obj):
        scale = 1000 * obj.v_scale
        # shapes = []
        levels = [obj.base_level]
        for height in obj.heights:
            levels.append(levels[-1] + height)

        simplify_sections_name = [obj.sections_name[0]]
        simplify_levels =[obj.base_level * scale]
        for i, section_name in enumerate(obj.sections_name):
            if section_name != simplify_sections_name[-1]:
                simplify_sections_name.append(section_name)
                simplify_levels.append((levels[i] + obj.extend_length) * scale)
        simplify_levels.append((levels[-1] + obj.extend_length) * scale)

        print(simplify_sections_name)
        print(simplify_levels)

        merge_flang_plates = []
        merge_flang_levels = [simplify_levels[0]]
        merge_web_plates = []
        merge_web_levels = [simplify_levels[0]]

        for i, name in enumerate(simplify_sections_name):
            flang_plate, web_plate = decompose_section_name(name)
            if flang_plate:
                extend_button_flang_length = 0
            else:
                extend_button_flang_length = -2 * obj.extend_length * scale

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
                extend_button_web_length = 0
            else:
                extend_button_web_length = -2 * obj.extend_length * scale

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

        print(merge_flang_plates)
        print(merge_flang_levels)
        print(merge_web_plates)
        print(merge_web_levels)                    
        ipe_shapes, bf, d, tf, tw = self.make_profile(obj)
        ipe = ipe_shapes[0]
        ipe_section_obj = FreeCAD.ActiveDocument.addObject("Part::FeaturePython", "ipe_section")
        ipe_section_obj.Shape = Part.makeCompound(ipe_shapes)
        IPE = Arch.makeStructure(ipe_section_obj)
        h = simplify_levels[-1] - simplify_levels[0]
        IPE.Height = h
        IPE.Placement.Base = FreeCAD.Vector(0, 0, simplify_levels[0]) + obj.Placement.Base
        IPE.ViewObject.ShapeColor = (1.0, 0.0, 0.0)

        flang_plate_names = []
        for i, plate in enumerate(merge_flang_plates):
            if plate:
                width = plate[0]
                height = plate[1]
                y = (d + height) / 2
                plt = create_plate(width, height)
                plt.Placement.Base = FreeCAD.Vector(0, y, merge_flang_levels[i]) + obj.Placement.Base
                plb = plt.copy()
                plb.Placement.Base = FreeCAD.Vector(0, -y, merge_flang_levels[i]) + obj.Placement.Base
                palte_obj = FreeCAD.ActiveDocument.addObject("Part::FeaturePython", "Flang_Plate")
                palte_obj.Shape = Part.makeCompound([plt, plb])
                PLATE = Arch.makeStructure(palte_obj)
                h = merge_flang_levels[i + 1] - merge_flang_levels[i]
                PLATE.Height = h
                PLATE.ViewObject.ShapeColor = (0.0, 0.0, 1.0)
                flang_plate_names.append(PLATE.Name)
            else:
                if obj.pa_baz:
                    bb = ipe_section_obj.Shape.BoundBox
                    width = bb.XLength - bf / 2
                    height = 5
                    y = (d + height) / 2
                    if i == 0:
                        level_i = merge_flang_levels[i] + 1.1 * scale# constant
                        connection_ipe_section = ipe.copy()
                        connection_ipe_section.Placement.Base = IPE.Placement.Base
                        connection_ipe_section_obj = FreeCAD.ActiveDocument.addObject("Part::FeaturePython", "ipe")
                        connection_ipe_section_obj.Shape = connection_ipe_section
                        connection_ipe_obj = Arch.makeStructure(connection_ipe_section_obj)
                        connection_ipe_obj.Height = 1 * scale
                        connection_ipe_obj.ViewObject.ShapeColor = (.80, 0.0, 0.0)


                    else:
                        level_i = merge_flang_levels[i] + .1 * scale
                    level_j = merge_flang_levels[i + 1]
                    h = level_j - level_i
                    space = .4 * scale # constant
                    n_z = int(h / space)
                    print(f"level_i = {level_i}, h = {h}, n_z = {n_z}")
                    plt = create_plate(width, height)
                    plt.Placement.Base = FreeCAD.Vector(0, y, level_i) + obj.Placement.Base
                    plb = plt.copy()
                    plb.Placement.Base = FreeCAD.Vector(0, -y, level_i) + obj.Placement.Base
                    palte_obj = FreeCAD.ActiveDocument.addObject("Part::FeaturePython", "Flang_Plate")
                    palte_obj.Shape = Part.makeCompound([plt, plb])
                    PLATE = Arch.makeStructure(palte_obj)
                    PLATE.Height = .15 * scale
                    PLATE.ViewObject.ShapeColor = (0.0, 0.0, 1.0)
                    _obj_ = Draft.make_ortho_array(PLATE, v_z=FreeCAD.Vector(0.0, 0.0, space), n_x=1, n_y=1, n_z=n_z)
                    flang_plate_names.append(_obj_.Name)

                

        web_plate_names = []
        for i, plate in enumerate(merge_web_plates):
            if plate:
                width = plate[0]
                height = plate[1]
                x = ipe.Placement.Base.x + (tw + height) / 2
                plwr = create_plate(height, width)
                plwr.Placement.Base = FreeCAD.Vector(x, 0, merge_web_levels[i]) + obj.Placement.Base
                plwl = plwr.copy()
                plwl.Placement.Base = FreeCAD.Vector(-x, 0, merge_web_levels[i]) + obj.Placement.Base
                palte_obj = FreeCAD.ActiveDocument.addObject("Part::FeaturePython", "web_Plate")
                palte_obj.Shape = Part.makeCompound([plwr, plwl])
                PLATE = Arch.makeStructure(palte_obj)
                h = merge_web_levels[i + 1] - merge_web_levels[i]
                PLATE.Height = h
                PLATE.ViewObject.ShapeColor = (0.0, 1.0, 0.0)
                web_plate_names.append(PLATE.Name)

        h = .02 * scale
        length = 700
        base_plate = Arch.makeStructure(length=length, width=length, height= h, name='BasePlate')
        x = obj.Placement.Base.x - length / 2
        y = obj.Placement.Base.y
        z = obj.base_level * scale - h / 2 
        base_plate.Placement.Base = FreeCAD.Vector(x, y, z)
        base_plate.ViewObject.ShapeColor = (1.0, 0.0, 0.0)

        childrens_name = flang_plate_names + web_plate_names + [IPE.Name] + [base_plate.Name]
        old_childrens_name = obj.childrens_name
        obj.childrens_name = childrens_name
        for name in old_childrens_name:
            children = FreeCAD.ActiveDocument.getObject(name)
            if hasattr(children, "Base") and children.Base:
                FreeCAD.ActiveDocument.removeObject(children.Base.Name)
            FreeCAD.ActiveDocument.removeObject(name)
        # for i, level in enumerate(simplify_levels[:-1]):
        #     section = make_section(simplify_sections_name[i], 0, level=level)
        #     h = simplify_levels[i + 1] - simplify_levels[i]

        #     column = Arch.makeStructure(section)
        #     column.Height = h
        #     column.Placement.Base = obj.Placement.Base
        #     columns_name.append(column.Name)
        #     # shapes.append(column.Shape.copy())

        # old_sections_name = obj.sections_name
        # old_columns_name = obj.columns_name
        # obj.columns_name = columns_name
        # for name in old_columns_name:
        #     column = FreeCAD.ActiveDocument.getObject(name)
        #     FreeCAD.ActiveDocument.removeObject(column.Base.Name)
        #     FreeCAD.ActiveDocument.removeObject(name)
        # obj.Shape = Part.makeCompound(shapes)
        obj.childrens_name = childrens_name

    def make_profile(self, obj):
        # name = ""
        shapes = []
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
                    break

        if obj.pa_baz:
            dist = bf
        else:
            dist = 0

        # doc = FreeCAD.ActiveDocument
        ipe = create_ipe(bf, d, tw, tf)
        deltax = bf + dist
        if obj.n == '3':
            ipe.Placement.Base.x = deltax
            ipe2 = ipe.copy()
            ipe2.Placement.Base.x = 0
            ipe3 = ipe.copy()
            ipe3.Placement.Base.x = -deltax
            shapes.extend([ipe, ipe2, ipe3])
            # name += f"3{sectionType}{sectionSize}"

        if obj.n == '2':
            ipe.Placement.Base.x = deltax / 2
            ipe2 = ipe.copy()
            ipe2.Placement.Base.x = -deltax / 2
            # name += f"2{sectionType}{sectionSize}"
            shapes.extend([ipe, ipe2])

        return shapes, bf, d, tf, tw

        # Components = Part.makeCompound(shapes)
        # obj.Shape = Components
        # obj.Placement.Base.z = obj.level

class ViewProviderColumnType:
    def __init__(self, obj):
        ''' Set this object to the proxy object of the actual view provider '''
        obj.Proxy = self

    def attach(self, vobj):
        self.ViewObject = vobj
        self.Object = vobj.Object

    def updateData(self, fp, prop):
        ''' If a property of the handled feature has changed we have the chance to handle this here '''
        return

    def getDisplayModes(self, obj):
        ''' Return a list of display modes. '''
        modes = []
        return modes

    def getDefaultDisplayMode(self):
        ''' Return the name of the default display mode. It must be defined in getDisplayModes. '''
        return "Shaded"

    def setDisplayMode(self, mode):
        ''' Map the display mode defined in attach with those defined in getDisplayModes.
        Since they have the same names nothing needs to be done. This method is optional.
        '''
        return mode

    def onChanged(self, vp, prop):
        ''' Print the name of the property that has changed '''
        FreeCAD.Console.PrintMessage("Change View property: " + str(prop) + "\n")

    def claimChildren(self):
        children=[FreeCAD.ActiveDocument.getObject(name) for name in self.Object.childrens_name]
        return children 




def make_column_type(heights, sections_name, n=2, size=16, pa_baz=False, base_level=0, extend_length=1.2, pos=(0, 0)):
    '''

    '''
    obj = FreeCAD.ActiveDocument.addObject("Part::FeaturePython", "column_type")
    ColumnType(obj)
    ViewProviderColumnType(obj.ViewObject)
    obj.heights = heights
    obj.sections_name = sections_name
    obj.base_level = base_level
    obj.extend_length = extend_length
    position = FreeCAD.Vector(pos[0], pos[1], 0)
    obj.Placement.Base = position
    obj.n = str(n)
    obj.size = str(size)
    obj.pa_baz = pa_baz
    FreeCAD.ActiveDocument.recompute()
    FreeCAD.ActiveDocument.recompute()
    return obj


# make_column_type([4, 3.2, 3.2, 3.2, 3.3, 5], ['2IPE16PL200x8w100x5', '2IPE16PL200x8', '2IPE16PL200x8','2IPE16PL200x8', '2IPE16', '2IPE16'], base_level=-1.2)
# make_column_type([3.3, 5], ['2IPE16', '2IPE16'], base_level=12.4, pos=(1000, 0))
make_column_type([4, 3.2, 3.2, 3.2, 3.3, 5], ['PL200x8w200x5', 'PL200x8w200x5', 'PL200x8','PL200x8', 'w200x5', 'w200x5'], base_level=-1.2, pos=(0, 0), size="30")
make_column_type([4, 3.2, 3.2, 3.2, 3.3, 5], ['PL300x8w200x5', 'PL250x8w200x5', 'PL200x8','PL200x8', 'w150x5', 'w150x5'], base_level=-1.2, pos=(4000, 0), size="24", pa_baz=True)
make_column_type([4, 3.2, 3.2, 3.2, 3.3, 5], ['w200x5', 'PL250x8w200x5', 'PL200x8','PL200x8', 'w150x5', 'w150x5'], base_level=-1.2, pos=(4000, 4000), size="24", pa_baz=True)


