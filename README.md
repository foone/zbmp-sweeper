ZBMP Sweeper
=============

This generates zbuffer-sweeping GIFs from ZBMP/MBMP backgrounds from Microsoft 3D Movie Maker

Requirements
============

* Python 2.7
* [numpy](http://www.numpy.org/)
* [PIL](http://www.pythonware.com/products/pil/) or [Pillow](https://pillow.readthedocs.org/en/3.0.x/installation.html)
* [3dmm Pencil++](http://frank.weindel.info/proj.pencil.html)
* [3D Movie Maker](https://en.wikipedia.org/wiki/3D_Movie_Maker)

Usage
=====
* Open BKGDS.3CN in 3dmm Pencil++. 
* Find the MBMP of the scene you want to export. 
* Click View/Edit, select the correct palette, and export to a BMP.
* Find the matching ZBMP (tree view helps here, as they'll be grouped under a single CAM)
* Click Export.. Give it a similar filename to the BMP you exported. Click "Yes" if you are asked if you want to decompress.
* Run build-sweep.py filename.bmp filename.zbmp in a console. You can run build-sweep.py --help for additional options

TODO:
=====

* Include lib3dmm & an MBMP parser so 3dmm Pencil++ isn't needed
* Configurable sweep highlight color
* Disablable sweep highlighting
* Start greyscale, and then sweep to color?