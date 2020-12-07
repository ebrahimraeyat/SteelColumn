import FreeCAD, FreeCADGui
import Part
from FreeCAD import Vector
import ArchProfile
from Arch import makeStructure
import csv
from os.path import join, dirname, abspath
import os
from columnTypeFunctions import *
# from PySide2.QtWidgets import *
# from PySide2.QtCore import *
from PySide2.QtGui import *
import section_config as config


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

        if not hasattr(obj, "flang_plate_size"):
            obj.addProperty(
                "App::PropertyIntegerList",
                "flang_plate_size",
                "section",
            )

        if not hasattr(obj, "web_plate_size"):
            obj.addProperty(
                "App::PropertyIntegerList",
                "web_plate_size",
                "section",
            )

        if not hasattr(obj, "pa_baz"):
            obj.addProperty(
                "App::PropertyBool",
                "pa_baz",
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
        if obj.n == 3 or obj.pa_baz:
            dist = bf
        else:
            dist = 0
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
            shapes.append(ipe3)
            name = f"3{sectionType}{sectionSize}"

        if obj.flang_plate_size:
            width = obj.flang_plate_size[0]
            height = obj.flang_plate_size[1]
            y = (d + height) / 2
            plt, _ = create_plate(width, height)
            plt.Placement.Base.y = y
            plb = plt.copy()
            plb.Placement.Base.y = -y
            shapes.extend([plt, plb])
            name += f"FPL{width}X{height}"

        if obj.web_plate_size:
            width = obj.web_plate_size[0]
            height = obj.web_plate_size[1]
            x = ipe.Placement.Base.x + (tw + height) / 2

            plwr, _ = create_plate(height, width)
            plwr.Placement.Base.x = x

            plwl = plwr.copy()
            plwl.Placement.Base.x = -x
            shapes.extend([plwr, plwl])
            name += f"WPL{width}X{height}"
        if obj.pa_baz:
            name += "CC"

        Components = Part.makeCompound(shapes)
        obj.Shape = Components
        obj.Placement.Base.z = obj.level
        obj.Placement.Rotation = FreeCAD.Rotation(FreeCAD.Vector(1,0,0),90)
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

    tf2 = 10
    tw2 = tf2

    s2, _ = create_plate(1.7 * width, tf2)
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
    edge = Part.makeLine(p1, p2)
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


def make_section_gui(n, size, flang_plate_size, web_plate_size, pa_baz):
    obj = FreeCAD.ActiveDocument.addObject("Part::Part2DObjectPython", "section")
    Section(obj)
    ViewProviderSection(obj.ViewObject)
    name = f"{n}IPE{size}"
    if flang_plate_size:
        bf, tf = flang_plate_size
        name += f"FPL{bf}X{tf}"
    if web_plate_size:
        bw, tw = web_plate_size
        name += f"WPL{bw}X{tw}"
    obj.Label = name
    obj.n = n
    obj.size = size
    obj.flang_plate_size = flang_plate_size
    obj.web_plate_size = web_plate_size
    obj.pa_baz = pa_baz
    return obj


def make_section(name, level=0, scale=.25, obj=None):
    n, size, flang_plate_size, web_plate_size, pa_baz = decompose_section_name(name)
    if not obj:
        obj = FreeCAD.ActiveDocument.addObject("Part::Part2DObjectPython", "section")
        Section(obj)
        ViewProviderSection(obj.ViewObject)
    obj.Label = name
    obj.n = n
    obj.size = size
    obj.flang_plate_size = flang_plate_size
    obj.web_plate_size = web_plate_size
    obj.pa_baz = pa_baz
    obj.level = level
    obj.scale = scale
    return obj


class Ui:
    def __init__(self, level_obj):
        steel_dir = os.path.dirname(__file__)
        self.form = FreeCADGui.PySideUic.loadUi(steel_dir + '/Resources/ui/sections.ui')
        self.form.add_button.setIcon(QPixmap(steel_dir + "/Resources/icons/add.svg"))
        self.form.remove_button.setIcon(QPixmap(steel_dir + "/Resources/icons/remove.svg"))
        self.level_obj = level_obj
        self.json_file = os.path.join(FreeCAD.getUserAppDataDir(), 'sections_name.json')
        self.load_config()

    def setupUi(self):
        self.add_connections()
        sections_name = self.level_obj.sections_name
        self.form.section_list.addItems(sections_name)
        FreeCAD.newDocument()
        FreeCADGui.ActiveDocument.ActiveView.viewFront()
        self.section_obj = make_section_gui(2, 14, [], [], False)
        FreeCAD.ActiveDocument.recompute()
        FreeCADGui.SendMsgToActiveView("ViewFit")

    def add_connections(self):
        self.form.ipe_size.currentIndexChanged.connect(self.reset_section_obj)
        self.form.number.currentIndexChanged.connect(self.reset_section_obj)
        self.form.bf.valueChanged.connect(self.reset_section_obj)
        self.form.tf.valueChanged.connect(self.reset_section_obj)
        self.form.bw.valueChanged.connect(self.reset_section_obj)
        self.form.tw.valueChanged.connect(self.reset_section_obj)
        self.form.flang_plate.toggled.connect(self.reset_section_obj)
        self.form.web_plate.toggled.connect(self.reset_section_obj)
        self.form.pa_baz.stateChanged.connect(self.reset_section_obj)
        self.form.add_button.clicked.connect(self.add_section)
        self.form.remove_button.clicked.connect(self.remove_section)
        self.form.section_list.itemClicked.connect(self.itemClicked)


    def itemClicked(self, item):
        name = item.text()
        make_section(name, obj=self.section_obj)
        FreeCAD.ActiveDocument.recompute()
        FreeCADGui.SendMsgToActiveView("ViewFit")



    def reset_section_obj(self):
        n, size, pa_baz, bf, tf, bw, tw, flang_plate, web_plate = self.current_form_values()
        obj = self.section_obj
        obj.n = n
        obj.size = size
        obj.pa_baz = pa_baz
        
        if flang_plate:
            obj.flang_plate_size = [bf, tf]
        else:
            obj.flang_plate_size = []
        if web_plate:
            obj.web_plate_size = [bw, tw]
        else:
            obj.web_plate_size = []
        FreeCAD.ActiveDocument.recompute()
        FreeCADGui.SendMsgToActiveView("ViewFit")

    def add_section(self):
        name = self.section_obj.name
        sections_name = [self.form.section_list.item(i).text() for i in range(self.form.section_list.count())]
        if not name in sections_name:
            self.form.section_list.addItem(name)

    def remove_section(self):
        i = self.form.section_list.currentRow()
        item = self.form.section_list.takeItem(i)
        self.form.section_list.removeItemWidget(item)

    def current_form_values(self):
        n = int(self.form.number.currentText())
        size = int(self.form.ipe_size.currentText())
        pa_baz = self.form.pa_baz.isChecked()
        bf = self.form.bf.value() * 10
        tf = self.form.tf.value()
        bw = self.form.bw.value() * 10
        tw = self.form.tw.value()
        flang_plate = self.form.flang_plate.isChecked()
        web_plate = self.form.web_plate.isChecked()

        return n, size, pa_baz, bf, tf, bw, tw, flang_plate, web_plate

    def save_config(self):
        sections_name = self.level_obj.sections_name
        config.save(sections_name, self.json_file)

    def load_config(self):
        if os.path.exists(self.json_file):
            self.level_obj.sections_name = config.load(self.json_file)


    def accept(self):
        name = FreeCAD.ActiveDocument.Name
        FreeCAD.closeDocument(name)
        sections_name = [self.form.section_list.item(i).text() for i in range(self.form.section_list.count())]
        FreeCAD.ActiveDocument.Levels.sections_name = sections_name
        self.save_config()
        FreeCADGui.Control.closeDialog(self)


    def reject(self):
        self.accept()


def create_sections():
    level_obj = FreeCAD.ActiveDocument.Levels
    ui = Ui(level_obj)
    # ui.setupUi()
    # ui.form.exec_()
    FreeCADGui.Control.showDialog(ui)
    if ui.setupUi():
        FreeCADGui.Control.closeDialog(ui)
    FreeCAD.ActiveDocument.recompute()




if __name__ == '__main__':
    create_sections()
    

