import FreeCAD, FreeCADGui
import Part
import ArchProfile
import Draft


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

        if not hasattr(obj, "Shape"):
            obj.addProperty(
                "App::PropertyPartShape",
                "Shape",
                "section")


    def execute(self, obj):
        name = ""
        sectionType = "IPE"
        sectionSize = obj.size
        
        # baseSection = sectionProp[sectionType][sectionSize] # IPE22 SECTION
        baseSectionType = "H"
        bf = 90
        d = 180
        tf = 8
        tw = 6
        dist = 70
        doc = FreeCAD.ActiveDocument
        ipe = ArchProfile.makeProfile([0, sectionType, sectionType , baseSectionType ,bf, d, tw, tf])
        deltax = bf + dist

        if obj.n == 3:
            ipe.Placement.Base.x = deltax
            s2 = Draft.move(ipe, FreeCAD.Vector(-deltax, 0, 0), copy=True)
            s3 = Draft.move(ipe, FreeCAD.Vector(-2 * deltax, 0, 0), copy=True)
            name += f"3{sectionType}{sectionSize}"

        if obj.n == 2:
            ipe.Placement.Base.x = deltax / 2
            s2 = Draft.rotate(ipe, 180, center=FreeCAD.Vector(0, 0, 0), copy=True)
            name += f"2{sectionType}{sectionSize}"
            
        Components = Part.makeCompound([o.Shape.copy() for o in (ipe, s2, s3)])
        obj.Shape = Components
        # for o in (obj.core_section + obj.flange_plate + obj.web_plate):
            # hide(o)
        #     print(o.Label)
        #     FreeCAD.ActiveDocument.removeObject(o.Label)
        obj.Label = name



# class ViewProviderSection:

#     "A View Provider for the Section object"

#     def __init__(self, vobj):
#         vobj.Proxy = self

#     def attach(self, obj):
#         ''' Setup the scene sub-graph of the view provider, this method is mandatory '''
#         return

#     def updateData(self, fp, prop):
#         ''' If a property of the handled feature has changed we have the chance to handle this here '''
#         return

#     def getDisplayModes(self, obj):
#         ''' Return a list of display modes. '''
#         modes = []
#         return modes

#     def getDefaultDisplayMode(self):
#         ''' Return the name of the default display mode. It must be defined in getDisplayModes. '''
#         return "Shaded"

#     def setDisplayMode(self, mode):
#         ''' Map the display mode defined in attach with those defined in getDisplayModes.
#         Since they have the same names nothing needs to be done. This method is optional.
#         '''
#         return mode

#     def onChanged(self, vp, prop):
#         ''' Print the name of the property that has changed '''
#         FreeCAD.Console.PrintMessage("Change View property: " + str(prop) + "\n")




def make_section(name):
    # for o in FreeCAD.ActiveDocument.Objects:
    #     if o.Label == name.upper():
    #         return
    n, size = 3, 18
    obj = FreeCAD.ActiveDocument.addObject("Part::Part2DObjectPython", "section")
    Section(obj)
    obj.Label = name
    obj.n = n
    obj.size = size
    obj.ViewObject.Proxy = 0
    # ViewProviderSection(obj.ViewObject)
    FreeCAD.ActiveDocument.recompute()
    FreeCAD.ActiveDocument.recompute()

def hide(obj):
    if hasattr(obj, 'ViewObject') and obj.ViewObject:
        obj.ViewObject.Visibility = False

make_section("3IPE18")