

def decompose_section_name(name):
    '''
    
    decompose_section_name(name)

    '''
    name = name.upper()
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

    return(flang_plate_dim, web_plate_dim)

