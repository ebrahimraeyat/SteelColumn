
import FreeCAD


def decompose_section_name(name):
    '''
    
    decompose_section_name(name)

    '''
    name = name.upper()
    n = int(name[0])
    size = int(name[4:6])
    fi = name.find("FPL")
    wi = name.find("WPL")
    if fi != -1:
        if wi == -1:
            flang_plate = name[fi:]
        else:
            flang_plate = name[fi: wi]
        flang_plate = flang_plate.lstrip("FPL")
        flang_plate = flang_plate.split("X")
        flang_plate_dim = [int(i) for i in flang_plate]
    else:
        flang_plate_dim = []
    if wi != -1:
        web_plate = name[wi:]
        web_plate = web_plate.lstrip("WPL")
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

def find_nardebani_plate_levels(names):
    sort_objects_by_minz = sorted(names, key=lambda name: FreeCAD.ActiveDocument.getObject(name).Base.Shape.BoundBox.ZMin)
    ZMins = [FreeCAD.ActiveDocument.getObject(name).Base.Shape.BoundBox.ZMin for name in sort_objects_by_minz]
    ZMaxs = [(FreeCAD.ActiveDocument.getObject(name).Base.Shape.BoundBox.ZMin + FreeCAD.ActiveDocument.getObject(name).Height.Value) for name in sort_objects_by_minz]
    levels = []
    zmin = ZMins[0]
    zmax = ZMaxs[0]
    for z1, z2 in zip(ZMins[1:], ZMaxs[1:]):
        if z1 < zmax:
            zmax = max(zmax, z2)
        else:
            levels.append([zmin, zmax])
            zmin = z1
            zmax = max(zmax, z2)
    levels.append([zmin, zmax])
    if not levels:
        return []
    empty_levels = []
    for i in range(len(levels) - 1):
        empty_levels.append([levels[i][1], levels[i + 1][0]])
    return empty_levels