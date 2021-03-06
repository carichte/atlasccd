#!/usr/bin/env python
from setuptools import setup, find_packages
import sys


try:
    import pyqtgraph
except ImportError:
    raise ImportError("Required package `pyqtgraph` not found. "
                      "Please install it to proceed.")

try:
    import fabio
except ImportError:
    raise ImportError("Required package `fabio` not found. "
                      "Please install it to proceed.")





if len(sys.argv)<2:
    print("see install.txt for installation instructions.")


setup( name = "atlasccd", 
       version = "0.1",
       packages = ["atlasccd"],
       package_dir = {"atlasccd":"lib"},
       author = "Carsten Richter",
       author_email = "carsten.richter@physik.tu-freiberg.de",
       url = "https://github.com/carichte/atlasccd",
       description = "functions to open and visualize images from agilents atlas ccd based on fabio and pyqtgraph", 
     )

