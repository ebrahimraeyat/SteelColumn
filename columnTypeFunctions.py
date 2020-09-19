
import FreeCAD


def decompose_section_name(name):
    '''
    
    decompose_section_name(name)

    '''
    name = name.upper()
    n = int(name[0])
    size = int(name[4:6])
    fi = name.find("PL")
    wi = name.find("W")
    if fi != -1:
        if wi == -1:
            flang_plate = name[fi:]
        else:
            flang_plate = name[fi: wi]
        flang_plate = flang_plate.lstrip("PL")
        flang_plate = flang_plate.split("X")
        flang_plate_dim = [int(i) for i in flang_plate]
    else:
        flang_plate_dim = []
    if wi != -1:
        web_plate = name[wi:]
        web_plate = web_plate.lstrip("W")
        web_plate = web_plate.split("X")
        web_plate_dim = [int(i) for i in web_plate]
    else:
        web_plate_dim = []

    return(n, size, flang_plate_dim, web_plate_dim)


def remove_obj(name):
    o = FreeCAD.ActiveDocument.getObject(name)
    if hasattr(o, "Base") and o.Base:
        remove_obj(o.Base.Name)
    FreeCAD.ActiveDocument.removeObject(name)

def find_empty_levels(names, levels, scale):
    empty_levels = set(levels.copy())
    for name in names:
        o = FreeCAD.ActiveDocument.getObject(name)
        zmin = o.Base.Shape.BoundBox.ZMin
        zmax = zmin + o.Height.Value
        for lev in levels:
            if zmin <= lev * scale <= zmax:
                if lev in empty_levels:
                    empty_levels.remove(lev)
    empty_levels = [lev * scale for lev in empty_levels]

    return sorted(empty_levels)



def find_nardebani_plate_levels(connection_names, names):
    sort_objects_by_minz = sorted(names, key=lambda name: FreeCAD.ActiveDocument.getObject(name).Base.Shape.BoundBox.ZMin)
    ZMins = [FreeCAD.ActiveDocument.getObject(name).Base.Shape.BoundBox.ZMin for name in sort_objects_by_minz]
    sort_objects_by_maxz = sorted(names, key=lambda name: FreeCAD.ActiveDocument.getObject(name).Shape.BoundBox.ZMin + FreeCAD.ActiveDocument.getObject(name).Height.Value)
    ZMaxs = [(FreeCAD.ActiveDocument.getObject(name).Base.Shape.BoundBox.ZMin + FreeCAD.ActiveDocument.getObject(name).Height.Value) for name in sort_objects_by_maxz]
    levels = []
    for i in range(len(connection_names)):
        o1 = FreeCAD.ActiveDocument.getObject(connection_names[i])
        zmin1 = o1.Base.Shape.BoundBox.ZMin
        zmax1 = zmin1 + o1.Height.Value

        # zmax2 = o2.Shape.BoundBox.ZMax
        if i > 0:
            pre_o = FreeCAD.ActiveDocument.getObject(connection_names[i - 1])
            zmax_pre = pre_o.Base.Shape.BoundBox.ZMin + pre_o.Height.Value
            z_that_less_than_zmin1 = [z for z in ZMaxs if zmax_pre < z < zmin1]
        else:
            z_that_less_than_zmin1 = [z for z in ZMaxs if z < zmin1]
        print(f"z_that_less_than_zmin1 = {z_that_less_than_zmin1}, zmin1 = {zmin1}, ZMaxs = {ZMaxs}")
        if z_that_less_than_zmin1:
            levels.append([max(z_that_less_than_zmin1), zmin1])

        z_that_greater_than_zmax1 = [z for z in ZMins if z > zmax1]
        if z_that_greater_than_zmax1:
            if i < len(connection_names) - 1:
                o2 = FreeCAD.ActiveDocument.getObject(connection_names[i + 1])
                zmin2 = o2.Base.Shape.BoundBox.ZMin
                z = min(zmin2, min(z_that_greater_than_zmax1))
            else:
                z = min(z_that_greater_than_zmax1)
            levels.append([zmax1, z])
        else:
            if i < len(connection_names) - 1:
                o2 = FreeCAD.ActiveDocument.getObject(connection_names[i + 1])
                z = o2.Base.Shape.BoundBox.ZMin
                levels.append([zmax1, z])

    return levels
    



        




