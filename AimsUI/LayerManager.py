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

from os.path import dirname, abspath, join

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from qgis.core import *
from qgis.gui import *
import sip
from AimsClient import Database
from AimsUI.AimsLogging import Logger
from AIMSDataManager.AimsUtility import FEEDS
from collections import OrderedDict

aimslog = Logger.setup()
uilog = None
sip.setapi('QVariant', 2)

class Mapping():
    """ 
    The mappings between UI components and AIMS object properties
    """
    adrLayerObjMappings = OrderedDict([
        ('addressType',['_components_addressType', None]),
        ('fullAddress',['_components_fullAddress', None]),
        ('fullAddressNumber',['_components_fullAddressNumber', None]),
        ('fullRoadName',['_components_fullRoadName', None]),
        ('suburbLocality',['_components_suburbLocality', None]),
        ('townCity',['_components_townCity', None]),
        ('meshblock',['_codes_meshblock', None]),
        ('mblkOverride',['_codes_isMeshblockOverride',None]),
        ('lifecycle',['_components_lifecycle', None]), 
        ('roadPrefix',['_components_roadSuffix',None]),
        ('roadName',['_components_roadName', None]),                                
        ('roadType',['_components_roadType',None]),
        ('roadSuffix',['_components_roadSuffix',None]),
        ('roadCentrelineId',['_components_roadCentrelineId',None]),
        ('waterRoute',['_components_waterRoute',None]),
        ('waterName',['_components_waterName',None]),
        ('unitValue',['_components_unitValue',None]),
        ('unitType',['_components_unitType',None]),
        ('levelType',['_components_levelType',None]),
        ('levelValue',['_components_levelValue',None]),
        ('addressNumberPrefix',['_components_addressNumberPrefix',None]),
        ('addressNumber',['_components_addressNumber',None]),
        ('addressNumberSuffix',['_components_addressNumberSuffix',None]),
        ('addressNumberHigh',['_components_addressNumberHigh',None]),
        ('addressId',['_components_addressId',None]),
        ('externalAddressId',['_components_externalAddressId',None]),
        ('externalAddressIdScheme',['_components_externalAddressIdScheme',None]),
        ('addressableObjectId',['_addressedObject_externalObjectId',None]),
        ('objectType',['_addressedObject_objectType',None]),
        ('objectName',['_addressedObject_objectName',None]),
        ('addressPositionType',['',None]),
        ('suburbLocalityId',['_codes_suburbLocalityId',None]),
        ('parcelId',['_codes_parcelId',None]),
        ('externalObjectId',['_addressedObject_externalObjectId',None]),
        ('externalObjectIdScheme',['_addressedObject_externalObjectIdScheme',None]),
        ('valuationReference',['_addressedObject_valuationReference',None]),
        ('certificateOfTitle',['_addressedObject_certificateOfTitle',None]),
        ('appellation',['_addressedObject_appellation',None]),
        ('version',['_components_version',None])
        ])

class LayerManager(QObject):
    """
    Managers the loading and updating of AIMS data as served 
    by the API and LINZ reference data.
    """
    
    # logging
    global uilog
    uilog = Logger.setup(lf='uiLog')
    
    _propBaseName='AimsClient.'
    _styledir = join(dirname(abspath(__file__)),'styles')
    _addressLayerId='adr'
    
    addressLayerAdded = pyqtSignal( QgsMapLayer, name="addressLayerAdded")
    addressLayerRemoved = pyqtSignal( name="addressLayerRemoved")

    def __init__(self, iface, controller):
        """ 
        Register the Layer manager with the Data Manager observer pattern
        therefore to be notified of new Data Manager data. 
        """
        
        QObject.__init__(self)
        self._iface = iface
        self._controller = controller
        self._canvas = self._iface.mapCanvas()
        self._statusBar = iface.mainWindow().statusBar()
        self._controller.uidm.register(self)
        self.legend = self._iface.legendInterface()
        self.rData = None
        self.prevExtFeat = None
        self.prevExtLab = None                
        self.prevRdata = None
        self._adrLayer = None
        self._rclLayer = None
        self._parLayer = None
        self._pprLayer = None # pending parcel
        self._lprLayer = None # labels, parcels
        self._locLayer = None
        self._revLayer = None
        self._extEvent = False
        
        QgsMapLayerRegistry.instance().layerWillBeRemoved.connect(self.checkRemovedLayer)
        QgsMapLayerRegistry.instance().layerWasAdded.connect( self.checkNewLayer )
    
    def initialiseExtentEvent(self):  
        """ 
        When the plugin is enabled (Via the .Controller()) 
        QGIS extentChanged signal connected to setbbox method  
        """
        
        self._canvas.extentsChanged.connect(self.setbbox)
        self._extEvent = True
    
    def disconnectExtentEvent(self):  
        """
        At plugin unload, disconnect the 
            extent changed / bbox event
        """
        #receiversCount = self.receivers(SIGNAL("self._canvas.extentsChanged()"))
        #if receiversCount > 0:
        if self._extEvent: 
            self._canvas.extentsChanged.disconnect(self.setbbox)
            self._extEvent = False   
        
    def layerId(self, layer):
        """ 
        Takes a layer as Vector Layer as a parameter and reutrns
        the layers Id as used by the plugin to reffer to the layers

        @param layer: AIMS qgis layer
        @type  layer: qgis._core.QgsVectorLayer 
        @return: AIMS layer Id as used to refered to AIMS layers
        @rtype: string
        """
        
        idprop = self._propBaseName + 'Id' 
        res = layer.customProperty(idprop)
        if isinstance(res,QVariant): res = res.toPyObject()
        return str(res)

    def setLayerId(self, layer, id):
        """
        Set id property for layer 

        @param layer: AIMS qgis layer
        @type  layer: qgis._core.QgsVectorLayer 
        @param id: AIMS Layer id
        @type  id: string
        """
        
        if id and isinstance(id, str):
            idprop = self._propBaseName + 'Id'
            layer.setCustomProperty(idprop,id)

    def layers(self):
        """
        Iterates over and yeilds all QGIS Map Layers

        @yield: qgis._core.QgsVectorLayer 
        """

        for layer in QgsMapLayerRegistry.instance().mapLayers().values():
                yield layer

    def addressLayer(self):
        """
        Return the AIMS Address Layer

        @return: AIMS Address Layer
        @rtype: qgis._core.QgsVectorLayer 
        """
        
        return self._adrLayer
    
    def rclLayer(self):
        """
        Return the Road Centre Line Layer

        @return: Road Centre Line Layer
        @rtype: qgis._core.QgsVectorLayer 
        """
        
        return self._rclLayer
    
    def revLayer(self):
        """
        Return the Review Layer

        @return: AIMS Review Layer
        @rtype: qgis._core.QgsVectorLayer 
        """
        
        return self._revLayer
    
    def checkRemovedLayer(self, id):
        """
        If layer removed set layer references to None

        @param id: The id of the layer removed
        @type  id: string
        """
        if self._adrLayer and self._adrLayer.id() == id:
            self._adrLayer = None
            self.addressLayerRemoved.emit()
        if self._rclLayer and self._rclLayer.id() == id:
            self._rclLayer = None
        if self._parLayer and self._parLayer.id() == id:
            self._parLayer = None
        if self._pprLayer and self._pprLayer.id() == id:
            self._pprLayer = None   
        if self._lprLayer and self._lprLayer.id() == id:
            self._lprLayer = None              
        if self._revLayer and self._revLayer.id() == id:
            self._revLayer = None
            
    def checkNewLayer( self, layer ):
        """
        Assign an AIMS QgsVectorLayer to a LayerManager layer property

        @param layer: New AIMS vector layer  
        @type  layer: qgis._core.QgsVectorLayer 
        """
        
        layerId = self.layerId(layer)
        if not layerId:
            return
        if layerId == self._addressLayerId:
            newlayer = self._adrLayer == None
            self._adrLayer = layer
            if newlayer:
                self.addressLayerAdded.emit(layer)
        elif layerId == 'rcl':
            self._rclLayer = layer
        elif layerId == 'par':
            self._parLayer = layer
        elif layerId == 'ppr':
            self._pprLayer = layer
        elif layerId == 'lpr':
            self._lprLayer = layer
        elif layerId == 'rev':
            self._revLayer = layer
    
    def findLayer(self, name):
        """
        Assign an AIMS QgsVectorLayer to a LayerManager layer property

        @param name: layer name
        @type  name: string

        @return: Layer that matches id
        @rtype: qgis._core.QgsVectorLayer 
        """
        
        for layer in self.layers():
            if self.layerId(layer) == name:
                return layer
        return None

    def styleLayer(self, layer, id):
        """ 
        Set layer style as per the relevant .qml file

        @param layer: AIMS Layer
        @type  layer: qgis._core.QgsVectorLayer 
        @param id: Layer Id
        @type  id: string 
        """
        
        try:
            layer.loadNamedStyle(join(self._styledir,id+'_style.qml'))
        except:
            pass
    
    def installLayer(self, id, schema, table, key, estimated, where, displayname):
        """
        Install AIMS postgres reference layers

        @param id: Layer id
        @type  id: string
        @param schema: Database Schema Name
        @type  schema: string
        @param table: Database Table Name
        @type  table: string
        @param key: Primary Key
        @type  key: string
        @param estimated: Estimate Meta Data
        @type  estimated: boolean
        @param where: SQL where cluase
        @type  where: string
        @param displayname: Layer Label
        @type  displayname: string


        @return: AIMS Layer
        @rtype: qgis._core.QgsVectorLayer 
        """
        
        layer = self.findLayer(id)
        if layer:
            if not self.legend.isLayerVisible(layer):
                self.legend.setLayerVisible(layer, True)
            return layer
        self._statusBar.showMessage("Loading layer " + displayname)
        try:
            uri = QgsDataSourceURI()
            uri.setConnection(Database.host(),str(Database.port()),Database.database(),Database.user(),Database.password())
            uri.setDataSource(schema,table,'shape',where,key)            
            uri.setUseEstimatedMetadata( estimated )            
            layer = QgsVectorLayer(uri.uri(),displayname,"postgres")
            self.setLayerId( layer, id )
            self.styleLayer(layer, id)            
            QgsMapLayerRegistry.instance().addMapLayer(layer)
        finally:
            self._statusBar.showMessage("")
        return layer

    def installRefLayers(self):
        """
        Install AIMS postgres reference layers
        """
        
              
        parQuery =  """ST_GeometryType(shape) IN ('ST_MultiPolygon', 'ST_Polygon') 
                                AND status = 'CURR' 
                                AND toc_code = 'PRIM'"""
        
        # require a better solution here to resolve failing to load due to no rows                        
        labelsQuery = """(SELECT label, par_id, shape 
                        FROM splanzer.par_label_for_bbox(177.06286,-37.97411, 177.06694,-37.97238))"""
        
        pendParQuery =  """ST_GeometryType(shape) IN ('ST_MultiPolygon', 'ST_Polygon') 
                                AND status = 'PEND' 
                                AND toc_code = 'PRIM'"""
              
        refLayers ={'par':( 'par', 'bde', 'crs_parcel', 'id', True, parQuery ,'Parcels' ) ,
                    
                    'lpr':( 'lpr', '', labelsQuery, 'par_id', True, "",'Parcels (Labels)' ) ,
                    
                    'rcl':( 'rcl', 'roads', 'simple_road_name_view', 'gid', True, "",'Roads' ),
                    
                    'ppr':( 'ppr', 'bde', 'crs_parcel', 'id', True, pendParQuery, 'Pending Parcels' )
                    }

        for layerId , layerProps in refLayers.items():
            layer = self.findLayer(layerId)
            if not layer:
                layer = self.installLayer(* layerProps) 
                
                if layerId == 'lpr':
                    self.legend.setLayerVisible(layer, False)

    def addLayerFields(self, layer, provider, id, fields):
        """
        Add fields to a layer  
        
        @param layer: AIMS vector layer  
        @type  layer: qgis._core.QgsVectorLayer 
        
        @param provider: Data Provider
        @type  provider: qgis._core.QgsVectorDataProvider
        @param id: Layer id
        @type  id: string
        @param fields: list of field names
        @type  fields: list
        """

        provider.addAttributes(fields)
        layer.updateFields()
        self.styleLayer(layer, id)     
        QgsMapLayerRegistry.instance().addMapLayer(layer)    
    
    def installAimsLayer(self, id, displayname):
        """
        Install AIMS feature and review layers

        @param id: Layer id
        @type  id: string
        @param displayname: displayname
        @type  displayname: string
        """

        if id == 'adr' and not self._adrLayer:
            layer = QgsVectorLayer("Point?crs=EPSG:4167", displayname, "memory") 
            self.setLayerId(layer, id)
            provider = layer.dataProvider()
            self.addLayerFields(layer, provider, id, [QgsField(layerAttName, QVariant.String) for layerAttName in Mapping.adrLayerObjMappings.keys()] ) 
        elif id == 'rev' and not self._revLayer:
            layer = QgsVectorLayer("Point?crs=EPSG:4167", displayname, "memory") 
            self.setLayerId(layer, id)
            provider = layer.dataProvider()
            self.addLayerFields(layer, provider, id, [QgsField('AimsId', QVariant.String), QgsField('AddressNumber', QVariant.String),QgsField('Action', QVariant.String)])
        else: return
        layer.updateFields()
        QgsMapLayerRegistry.instance().addMapLayer(layer)           
        
    def isVisible(self, layer):
        """
        Test if a layer is visible as per scale based vis 

        @param layer: AIMS vector layer  
        @type  layer: qgis._core.QgsVectorLayer 

        @return: True if Layer is visible
        @rtype: boolean
        """
        
        if layer.hasScaleBasedVisibility():
            if layer.maximumScale() > self._canvas.scale() and layer.minimumScale() < self._canvas.scale():
                return True
            else: 
                return False
        else:
            return True    

    def removeFeatures(self, layer):
        """
        Remove all features from a layer

        @param layer: AIMS vector layer  
        @type  layer: qgis._core.QgsVectorLayer 
        """

        ids = [f.id() for f in layer.getFeatures()]
        layer.startEditing()
        for fid in ids:          
            layer.deleteFeature(fid)
        layer.commitChanges()
    
    def addToLayer(self, rData, layer):
        """
        Add aims review features to reveiw layer 
        
        @param rData: Review Data
        @type  rData: dictionary
        @param layer: AIMS vector layer  
        @type  layer: qgis._core.QgsVectorLayer 
        """

        provider = layer.dataProvider()
        for k, reviewItem in rData.items():
            if hasattr(reviewItem,'_queueStatus'):
                if reviewItem._queueStatus in ('Declined, Accepted'):
                    continue 
                
            fet = QgsFeature()
            if reviewItem._changeType in ('Update', 'Add') or reviewItem.meta.requestId: 
                point = reviewItem.getAddressPositions()[0]._position_coordinates
            else:
                try:
                    point = reviewItem.meta.entities[0].getAddressPositions()[0]._position_coordinates
                except: 
                    uilog.error(' *** ERROR ***  ') 
            fet.setGeometry(QgsGeometry.fromPoint(QgsPoint(point[0], point[1])))
            fet.setAttributes([ k, reviewItem.getFullNumber(), reviewItem._changeType])
            provider.addFeatures([fet])
        layer.updateExtents()
    
    def updateReviewLayer(self):
        """
        Update review layer
        """
        
        id = 'rev'
        layer = self.findLayer(id)
        if not layer: 
            return
        self.removeFeatures(layer)
        rData = self._controller.uidm.combinedReviewData()
        uilog.info(' *** DATA ***    {} review items being loaded '.format(len(rData)))
        self.addToLayer(rData, layer)
    
    def bboxWithPrevious(self, prevExt, ext):
        """ 
        Test if the emitted canvas extent is within the previous extent
        
        @param ext: canvas extent
        @type  ext: gis._core.QgsRectangle 

        @rtype: boolean
        """

        if not prevExt: 
            return False
        elif QgsRectangle.contains(prevExt, ext):
            return True
        else: 
            return False
                        
    def setbbox(self):
        """ 
        Triggered by extent change - Set BBox in UIDataManager
        """
        
        feat_layer = self.findLayer('adr')
        parLabel_layer = self.findLayer('lpr')
        
        ext = self._canvas.extent()
        sw = (ext.xMinimum(), ext.yMinimum())
        ne = (ext.xMaximum(), ext.yMaximum())

        #if self._canvas.scale() > feat_layer.maximumScale() or self.bboxWithPrevious(ext): return
        
        # Get Features 
        if self._canvas.scale() < feat_layer.maximumScale() and not self.bboxWithPrevious(self.prevExtFeat, ext):
            uilog.info(' *** BBOX ***    {} '.format(ext.toString()))    
            self._controller.uidm.setBbox(sw, ne)
            self.prevExtFeat = ext

        # Get Par Labels 
        if (self._canvas.scale() < parLabel_layer.maximumScale() 
            and not self.bboxWithPrevious(self.prevExtLab, ext)  
            and self.isVisible(parLabel_layer)
            and self.legend.isLayerVisible(parLabel_layer)):
            
            self.updateLabels(parLabel_layer, sw, ne)
            self.prevExtLab = ext
                            
    def getAimsFeatures(self):
        """ 
        Retrieve most AIMS Features as held in UiDataManager
        """

        featureData = self._controller.uidm.featureData()
        if featureData:
            uilog.info(' *** DATA ***    {} AIMS features received '.format(len(featureData)))    
            self.updateFeaturesLayer(featureData)
    
    def notify(self, feedType):
        """ Notify registered to UiDataManager 
        
        @param feedType: Type of AIMS API
        @type  feedType: AIMSDataManager.FeatureFactory.FeedRef
        """

        uilog.info('*** NOTIFY ***     Notify A[{}]'.format(feedType))
        if feedType == FEEDS['AF']:
            self.getAimsFeatures()
        elif feedType == FEEDS['AR'] or feedType == FEEDS['GR']:
            self.updateReviewLayer()
    
    def updateLabels(self, layer, sw, ne):
        
        uilog.info(' *** UPDATING LABELS *** ')    

        
        uri = QgsDataSourceURI() # self these?
        uri.setConnection(Database.host(),str(Database.port()),Database.database(),Database.user(),Database.password())
        sql = """(SELECT label, par_id, shape 
        FROM splanzer.par_label_for_bbox({0},{1},{2},{3}))""".format(sw[0], sw[1], ne[0], ne[1])
        uri.setDataSource("", sql, "shape", "", "par_id" )
        layer.setDataSource(uri.uri(), 'Parcels (Labels)', 'postgres', False)
    
    def updateFeaturesLayer(self, featureData):
        """
        Add features to AIMS Address feature layer 

        @param featureData: feature feed data
        @type  featureData: dictionary
        """

        id = self._addressLayerId
        layer = self.findLayer(id)
        # ensure the user has not removed the layer 
        if not layer:
            self.installAimsLayer(id, 'AIMS Features')
            layer = self.findLayer(id) 
        if not self.isVisible(layer): 
            return
        if not self.legend.isLayerVisible(layer):
            self.legend.setLayerVisible(layer, True)
        # remove current features 
        self.removeFeatures(layer)
        uilog.info(' *** CANVAS ***    Adding Features') 
        for feature in featureData.itervalues():
            fet = QgsFeature()
            point = feature.getAddressPositions()[0]._position_coordinates
            fet.setGeometry(QgsGeometry.fromPoint(QgsPoint(point[0], point[1])))           
            fet.setAttributes([getattr(feature, v[0]) if hasattr (feature, v[0]) else '' for v in Mapping.adrLayerObjMappings.values()])
            if hasattr(getattr(feature,'_addressedObject_addressPositions')[0],'_positionType'):
                # If positionType update field index 30. Would rather use the explicit name...
                fet.setAttribute(30, feature._addressedObject_addressPositions[0]._positionType)
            layer.dataProvider().addFeatures([fet])
        layer.updateExtents()
        
        uilog.info(' *** CANVAS ***    FEATURES ADDED')  
        