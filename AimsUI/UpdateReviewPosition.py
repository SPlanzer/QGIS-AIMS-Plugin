################################################################################
#
# Copyright 2016 Crown copyright (c)
# Land Information New Zealand and the New Zealand Government.
# All rights reserved
#
# This program is released under the terms of the 3 clause BSD license. See the 
# LICENSE file for more information.
#
################################################################################

import sys
import time

from PyQt4.QtCore import *
from PyQt4.QtGui import *

from qgis.core import *
from qgis.gui import *

from AimsUI.AimsClient.Gui.UiUtility import UiUtility
from AimsUI.AimsClient.Gui.ResponseHandler import ResponseHandler
from AIMSDataManager.AimsUtility import FEEDS

class UpdateReviewPosition(QgsMapToolIdentifyFeature):
    """
    Tool for relocating AIMS Review Features
    """ 

    def __init__(self, iface, layerManager, controller):
        """
        Intialise Update Address Tool
        
        @param iface: QgisInterface Abstract base class defining interfaces exposed by QgisApp  
        @type iface: Qgisinterface Object
        @param layerManager: Plugins layer manager
        @type  layerManager: AimsUI.LayerManager()
        @param controller: Instance of the plugins controller
        @type  controller: AimsUI.AimsClient.Gui.Controller()
        """
       
        QgsMapToolIdentify.__init__(self, iface.mapCanvas())
        self._iface = iface
        self._controller = controller
        self._layers = layerManager
        self._canvas = iface.mapCanvas()
        self.RespHandler = ResponseHandler(self._iface, self._controller.uidm)
        self._currentRevItem = None

    def activate(self):
        """
        Activate Update Review Position Tool
        """
        
        QgsMapTool.activate(self)
        self._currentRevItem = self._controller.currentRevItem
        sb = self._iface.mainWindow().statusBar()
        sb.showMessage('Click map to select new position for review item')
    
    def deactivate(self):
        """
        Deactivate Update Review Position Tool
        """
        
        sb = self._iface.mainWindow().statusBar()
        sb.clearMessage()
        
    def setEnabled(self, enabled):
        """ 
        When Tool related QAction is checked/unchecked
        Activate / Disable the tool respectively

        @param enabled: Tool enabled. Boolean value
        @type enabled: boolean
        """
        
        self._enabled = enabled
        if enabled:
            self.activate()
        else:
            self.deactivate()
    
    def canvasReleaseEvent(self, mouseEvent):
        """
        Identify the AIMS Feature(s) the user clicked

        @param mouseEvent: QtGui.QMouseEvent
        @type mouseEvent: QtGui.QMouseEvent
        """

        self._iface.setActiveLayer(self._layers.addressLayer())
        
        results = self.identify(mouseEvent.x(), mouseEvent.y(), self.ActiveLayer, self.VectorLayer)
        if self._currentRevItem:
            
            if self._currentRevItem._changeType in ('Retire', 'AddLineage' ):
                self._iface.messageBar().pushMessage("{} review items cannot be relocated".format(self._currentRevItem._changeType), 
                                                     level=QgsMessageBar.WARNING, duration = 5)
                return
            
            if len(results) == 0:                     
                coords = self.toMapCoordinates(QPoint(mouseEvent.x(), mouseEvent.y()))
            else:
                # Snapping. i.e Move to stack
                coords = results[0].mFeature.geometry().asPoint()    
            coords = list(UiUtility.transform(self._iface, coords))
            
            respId = int(time.time())
            
            if self._currentRevItem._changeType in ('Add', 'Update'):
                feedType = FEEDS['AR']
                self._currentRevItem._addressedObject_addressPositions[0].setCoordinates(coords)
                self._controller.uidm.repairAddress(self._currentRevItem, respId)
            else:
                feedType = FEEDS['GR'] 
                changeId = self._currentRevItem._changeId
                self._currentRevItem = self._currentRevItem.meta.entities[0]
                self._currentRevItem._addressedObject_addressPositions[0].setCoordinates(coords)
                self._currentRevItem.setChangeId(changeId)
                self._controller.uidm.repairAddress(self._currentRevItem, respId)
            
            self.RespHandler.handleResp(respId, feedType)
            self._controller.setPreviousMapTool() 

