## SteelColumn Workbench
Creating Steel Columns in [FreeCAD](https://freecadweb.org) that combined from IPE profile and plates.

![steelcolumn](https://user-images.githubusercontent.com/8196112/102282896-9b423480-3f46-11eb-935c-a7cae324e165.gif)

## Installation
### Ubuntu (Debian base system)

```bash
$ sudo apt install freecad-python3
$ sudo update-alternatives --set freecad /usr/lib/freecad/bin/freecad-python3
$ pip install ezdxf
$ mkdir -p $HOME/.FreeCAD/Mod
$ cd $HOME/.FreeCAD/Mod
$ git clone https://github.com/ebrahimraeyat/momen.git SteelColumn
``` 

## Discussion
Forum thread to discuss this workbench can be found in the [FreeCAD Subforums](https://forum.freecadweb.org/viewtopic.php?f=23&t=49509)

## How TO Work
It's so easy. You must click on icons from left to right!
1- create levels: click on the level's icon to create all required levels. You can modify the heights after creating columns.
2- create sections: click on section's icon to create steel sections.
3- create column: click on plus icon to create columns.

- For exporting to DXF you can click on DXF icon
- For updating Workbench you can click on Update icon.

## Contribute
Pull Requests are welcome. Please feel free to discuss them on the forum thread.