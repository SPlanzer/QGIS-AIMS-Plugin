# -*- coding: utf-8 -*-
################################################################################
#
# Copyright 2015 Crown copyright (c)
# Land Information New Zealand and the New Zealand Government.
# All rights reserved
#
# This program is released under the terms of the 3 clause BSD license. See the 
# LICENSE file for more information.
#
###############################################################################
import sys

from PyQt4.QtCore import *
from PyQt4.QtGui import *

from qgis.core import *
from qgis.gui import *

from AimsClient.Gui.NewAddressDialog import NewAddressDialog
from AimsUI.AimsClient.Gui.UiUtility import UiUtility
from AIMSDataManager.AimsUtility import FeedType, FeatureType, FeedRef
from AIMSDataManager.AddressFactory import AddressFactory

class CreateNewAddressTool(QgsMapToolIdentify):
    ''' tool for creating new address information ''' 

    def __init__(self, iface, layerManager, controller=None):        
        QgsMapToolIdentify.__init__(self, iface.mapCanvas())
        self._iface = iface
        self._layers = layerManager
        self._controller = controller
        self._canvas = iface.mapCanvas()
        self.af = AddressFactory.getInstance(FeedRef((FeatureType.ADDRESS, FeedType.CHANGEFEED)))
        self.activate()
        
    def activate(self):
        QgsMapTool.activate(self)
        sb = self._iface.mainWindow().statusBar()
        sb.showMessage("Click map to create point")
        self.cursor = QCursor(Qt.CrossCursor)
        self.parent().setCursor(self.cursor)
    
    def deactivate(self):
        sb = self._iface.mainWindow().statusBar()
        sb.clearMessage()

    def setEnabled(self, enabled):
        self._enabled = True #enabled
        if enabled:
            self.activate()
        else:
            self.deactivate()
 
    def canvasReleaseEvent(self,mouseEvent):
        self._iface.setActiveLayer(self._layers.addressLayer())
        
        if mouseEvent.button() == Qt.LeftButton:
            results = self.identify(mouseEvent.x(), mouseEvent.y(), self.ActiveLayer, self.VectorLayer)
            # Ensure feature list and highlighting is reset            
            if len(results) == 0: 
                # no results - therefore we ain't snapping
                coords = self.toMapCoordinates(QPoint(mouseEvent.x(), mouseEvent.y()))
            else:
                # snap by taking the coords from the point within the 
                # tolerance as defined by QGIS maptool settings under options
                coords = results[0].mFeature.geometry().asPoint()
            self.setPoint(coords)
    
    def setMarker(self, coords):
        self._marker = UiUtility.highlight(self._iface, coords, QgsVertexMarker.ICON_X)
   
    def setPoint( self, coords ):
        ''' guarantee srs and pass to the API '''
        self.setMarker(coords)
        coords = UiUtility.transform(self._iface, coords)            
        # init new address object and open form
        afc = self.af.getInstance(FeedType.CHANGEFEED)
        addInstance = afc.getAddress()#(adr='AddressChange',model='')
        NewAddressDialog.newAddress(addInstance, self._layers, self._controller, self._iface.mainWindow(), coords)
        self._canvas.scene().removeItem(self._marker)
        self._enabled = True
