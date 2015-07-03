#!/usr/bin/env python
#----------------------------------------------------------------------
# Description:
# Author: Carsten Richter <carsten.richter@desy.de>
# Created at: Do 2. Jul 14:27:28 CEST 2015
# Computer: haso227r 
# System: Linux 3.13.0-55-generic on x86_64
#
# Copyright (c) 2015 Carsten Richter  All rights reserved.
#----------------------------------------------------------------------
import os
import sys
import time
import glob
import itertools

import numpy as np
import pyqtgraph as pg
import fabio

import matplotlib.cm




def open_img(fpath, tmpfile = "/tmp/atlasccd.img"):
    """
        Tiny wrapper around fabio to open a compressed atlas ccd .img file.
        Header and footer due to copying with netcat is removed.
        
        Returns: an fabio.OXDimage.OXDimage instance
    """
    with open(fpath, "r") as fh:
        s = fh.read(10)
        if s=="get(DATA):":
            s = fh.read(72) # discard header
            s = fh.read(-8)
        else:
            s = None
    if s != None:
        with open(tmpfile, "w") as fh:
            fh.write(s)
        fpath = tmpfile
    
    im = fabio.open(fpath)
    return im


def open_img_stack(files):
    """
        Opens several `.img` files from atlas ccd.
        
        Returns: an 2D or 3D numpy.ndarray containing the data.
                 Dimensions:
                    0 - image number
                    1 - x
                    2 - y
    """
    if isinstance(files, (str, unicode)):
        files = glob.glob(files)
    if not files:
        raise ValueError("Empty argument.")
    elif len(files)==1:
        return open_img(files[0]).data
    return np.dstack([open_img(fname).data for fname in files]).transpose(2,0,1)



class _ImageWindow(pg.ImageWindow):
    def set_cm(self, cmap):
        hw = self.getHistogramWidget()
        nativeCM = pg.graphicsItems.GradientEditorItem.Gradients.keys()
        mplCM = [cm for cm in dir(matplotlib.cm) if not cm.startswith("_")]
        if cmap in nativeCM:
            hw.item.gradient.loadPreset(cmap)
        elif cmap in mplCM:
            ticks =  [(i, (map(lambda j: int(j*255), getattr(matplotlib.cm, cmap)(i)))) for i in np.linspace(0,1,11)]
            gradient = dict(ticks=ticks, mode="rgb")
            hw.item.gradient.restoreState(gradient)
        else:
            raise ValueError("Unknown color map. Choose one of: %s"
            %(", ".join(nativeCM + mplCM)))
    
    def setCurrentIndex(self, ind, *args, **kargs):
        #if hasattr(self, "labels") and ind < len(self.labels):
        #    self.win.setWindowTitle(self.labels[ind])
        super(_ImageWindow, self).setCurrentIndex(ind, *args, **kargs)
        if hasattr(self, "labels") and self.currentIndex < len(self.labels):
            self.win.setWindowTitle(self.labels[self.currentIndex])



def show_img(data, title=None):
    if isinstance(data, fabio.OXDimage.OXDimage):
        data = data.data
    if data.ndim == 2:
        #axes=dict(x=0, y=1)
        data = np.rot90(data, -1)
    elif data.ndim == 3:
        #axes=dict(x=0, y=1, t=2)
        data = data.transpose(0,2,1)
        data = data[:,:,::-1]
    else:
        raise ValueError("Need 2D or 3D data.")
    iw = _ImageWindow(data)#, title=title)
    if title:
        iw.win.setWindowTitle(title)
    iw.roi.setSize((data.shape[-2]/5,data.shape[-1]/10))
    iw.set_cm("jet")
    iw.view.setAspectLocked(False)
    return iw   



def scan_folder(directory):
    time0 = [0]
    iw = _ImageWindow()
    iw.labels = list()
    def helper():
        flist = glob.iglob(os.path.join(directory, "*.img"))
        flist = list(itertools.ifilter(lambda f: os.path.getmtime(f) > time0[0], 
                                       flist))
        
        if not flist:
            return
        flist.sort(key=os.path.getmtime)
        
        fpath = flist[-1]
        time0[0] = os.path.getmtime(fpath)
        data = open_img(fpath).data
        data = np.rot90(data, -1)
        if np.ndim(iw.image)==2 and iw.image.shape==data.shape:
            newdata = np.concatenate([data[np.newaxis], iw.image[np.newaxis]], 
                                     axis=0)
        elif np.ndim(iw.image)==3 and iw.image.shape[1:3]==data.shape:
            newdata = np.concatenate([data[np.newaxis], iw.image], axis=0)
        elif np.ndim(data)==2:
            newdata = data
        else:
            return
        print fpath
        iw.setImage(newdata, autoLevels=False)
        iw.labels.insert(0, fpath)
        iw.win.setWindowTitle(fpath)
    helper()
    if np.ndim(iw.image)>=2:
        iw.roi.setSize((max(10, iw.image.shape[-2]/5),
                        max(5, iw.image.shape[-1]/10)))
    iw.set_cm("jet")
    iw.view.setAspectLocked(False)
    return helper

