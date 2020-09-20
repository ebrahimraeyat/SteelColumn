import FreeCAD, FreeCADGui
import Part
from FreeCAD import Vector
import ArchProfile
from Arch import makeStructure
import Draft
import csv
from os.path import join, dirname, abspath
from columnTypeFunctions import *


class Section:
    def __init__(self, obj):
        obj.Proxy = self
        self.set_properties(obj)

    def set_properties(self, obj):
        self.Type = "Section"
        
        if not hasattr(obj, "n"):
            obj.addProperty(
                "App::PropertyInteger",
                "n",
                "section",
            )

        if not hasattr(obj, "size"):
            obj.addProperty(
                "App::PropertyInteger",
                "size",
                "section",
            )

        if not hasattr(obj, "flange_plate_size"):
            obj.addProperty(
                "App::PropertyIntegerList",
                "flange_plate_size",
                "section",
            )

        if not hasattr(obj, "web_plate_size"):
            obj.addProperty(
                "App::PropertyIntegerList",
                "web_plate_size",
                "section",
            )

        if not hasattr(obj, "dist"):
            obj.addProperty(
                "App::PropertyFloat",
                "dist",
                "section",
                )

        if not hasattr(obj, "level"):
            obj.addProperty(
                "App::PropertyFloat",
                "level",
                "section",
                )

        if not hasattr(obj, "scale"):
            obj.addProperty(
                "App::PropertyFloat",
                "scale",
                "section",
                )

        if not hasattr(obj, "name"):
            obj.addProperty(
                "App::PropertyString",
                "name",
                "section",
                )


    def execute(self, obj):
        name = ""
        shapes = []
        sectionSize = obj.size
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

        dist = obj.dist
        doc = FreeCAD.ActiveDocument
        ipe, _ = create_ipe(bf, d, tw, tf)
        deltax = bf + dist

        # if obj.n == 2:
        ipe.Placement.Base.x = deltax / 2
        ipe2 = ipe.copy()
        ipe2.Placement.Base.x = -deltax / 2
        name += f"2{sectionType}{sectionSize}"
        shapes.extend([ipe, ipe2])

        if obj.n == 3:
            ipe3 = ipe.copy()
            ipe3.Placement.Base.x = 0
            # ipe2 = Draft.move(ipe, FreeCAD.Vector(-deltax, 0, 0), copy=True)
            # ipe3 = Draft.move(ipe, FreeCAD.Vector(-2 * deltax, 0, 0), copy=True)
            shapes.append(ipe3)
            name = f"3{sectionType}{sectionSize}"

        if obj.flange_plate_size:
            width = obj.flange_plate_size[0]
            height = obj.flange_plate_size[1]
            y = (d + height) / 2
            plt, _ = create_plate(width, height)
            plt.Placement.Base.y = y
            # plt.ViewObject.ShapeColor = (0.0, 0.0, 1.0)
            # gui.getObject(plt.Label).DisplayMode = "Wireframe"
            plb = plt.copy()
            plb.Placement.Base.y = -y
            # group.addObjects([plt, plb])
            shapes.extend([plt, plb])
            name += f"PL{width}X{height}"

        if obj.web_plate_size:
            width = obj.web_plate_size[0]
            height = obj.web_plate_size[1]
            # x = ipe.Shape.BoundBox.Center.x + (ipe.WebThickness.Value + height) / 2
            x = ipe.Placement.Base.x + (tw + height) / 2

            plwr, _ = create_plate(height, width)
            plwr.Placement.Base.x = x

            # gui.getObject(plwr.Label).ShapeColor = (0.0, 1.0, 0.0)
            # gui.getObject(plwr.Label).DisplayMode = "Wireframe"
            plwl = plwr.copy()
            plwl.Placement.Base.x = -x
            # group.addObjects([plwr, plwl])
            shapes.extend([plwr, plwl])
            name += f"W{width}X{height}"

        Components = Part.makeCompound(shapes)
        # Components.scale = obj.scale
        obj.Shape = Components
        obj.Placement.Base.z = obj.level
        obj.Placement.Rotation = FreeCAD.Rotation(FreeCAD.Vector(1,0,0),90)
        # for o in (obj.core_section + obj.flange_plate + obj.web_plate):
        #     hide(o)
        #     print(o.Label)
        #     FreeCAD.ActiveDocument.removeObject(o.Label)
        obj.Label = name
        obj.name = name
        

def create_ipe(width, height, tw, tf):
    import Part
    p1 = Vector(-width/2,-height/2,0)
    p2 = Vector(width/2,-height/2,0)
    p3 = Vector(width/2,(-height/2)+tf,0)
    p4 = Vector(tw/2,(-height/2)+tf,0)
    p5 = Vector(tw/2,height/2-tf,0)
    p6 = Vector(width/2,height/2-tf,0)
    p7 = Vector(width/2,height/2,0)
    p8 = Vector(-width/2,height/2,0)
    p9 = Vector(-width/2,height/2-tf,0)
    p10 = Vector(-tw/2,height/2-tf,0)
    p11 = Vector(-tw/2,(-height/2)+tf,0)
    p12 = Vector(-width/2,(-height/2)+tf,0)
    p = Part.makePolygon([p1,p2,p3,p4,p5,p6,p7,p8,p9,p10,p11,p12,p1])
    p = Part.Face(p)
    edge = Part.makeLine(p1, p2)
    return p, edge


def create_neshiman(width, height, tw, tf):
    s1, _ = create_ipe(width, height, tw, tf)

    tf2 = height / 10
    tw2 = 10

    s2, _ = create_plate(1.5 * width, tf2)
    s2.Placement.Base.y -= height / 2 + tf2 / 2

    x1 = -(width + tw2) / 2
    x2 = x1 + tw2
    y1 = -height / 2 - tf2
    y2 = y1 - height / 2
    p1 = Vector(x1, y1, 0)
    p2 = Vector(x2, y1, 0)
    p3 = Vector(x2, y2, 0)
    p4 = Vector(x1, y2, 0)
    s3 = Part.makePolygon([p1, p2, p3, p4, p1])
    s3 = Part.Face(s3)

    s4 = s3.copy()
    s4.Placement.Base.x = width

    return Part.makeCompound([s1, s2, s3, s4])





def create_plate(width, height):
    import Part
    p1 = Vector(-width/2,-height/2,0)
    p2 = Vector(width/2,-height/2,0)
    p3 = Vector(width/2,height/2,0)
    p4 = Vector(-width/2,height/2,0)
    p = Part.makePolygon([p1,p2,p3,p4,p1])
    p = Part.Face(p)
    edge = Part.makeLine(p4, p3)
    return p, edge

        # for i, section in enumerate(obj.sections):
        #     if i > max_index:
        #         return
        #     height = obj.levels[i+1] - obj.levels[i]
class ViewProviderSection:

    "A View Provider for the Section object"

    def __init__(self, vobj):
        vobj.Proxy = self

    def attach(self, obj):
        ''' Setup the scene sub-graph of the view provider, this method is mandatory '''
        return

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




def make_section(name, dist=0, level=0, scale=.25):
    # for o in FreeCAD.ActiveDocument.Objects:
    #     if o.Label == name.upper():
    #         return
    n, size, flange_plate_size, web_plate_size = decompose_section_name(name)
    FreeCAD.Console.PrintMessage(f"{n}, {size}, {flange_plate_size}, {web_plate_size}")
    obj = FreeCAD.ActiveDocument.addObject("Part::Part2DObjectPython", "section")
    Section(obj)
    ViewProviderSection(obj.ViewObject)
    obj.Label = name
    obj.n = n
    obj.size = size
    obj.flange_plate_size = flange_plate_size
    obj.web_plate_size = web_plate_size
    obj.dist = dist
    obj.level = level
    obj.scale = scale
    # FreeCAD.ActiveDocument.recompute()
    # FreeCAD.ActiveDocument.recompute()
    return obj

if __name__ == '__main__':
    make_section("3IPE18pl200x10w130x5")
    make_section("3IPE18pl200x10", 0, 3000)


