################################################################################
#
# Copyright 2015 Crown copyright (c)
# Land Information New Zealand and the New Zealand Government.
# All rights reserved
#
# This program is released under the terms of the 3 clause BSD license. See the 
# LICENSE file for more information.
#
################################################################################

from datetime import datetime as DT
#from functools import wraps

import os
import sys
import re
import logging
import time
import threading
import Queue

from Observable import Observable
from DataPager import DataPager
from DataUpdater import DataUpdater,DataUpdaterAction,DataUpdaterApproval,DataUpdaterGroupAction,DataUpdaterGroupApproval,DataUpdaterUserAction
from AimsApi import AimsApi 
from AimsLogging import Logger
from AimsUtility import ActionType,ApprovalType,GroupActionType,GroupApprovalType,UserActionType,FeedType,FeatureType,FeedRef,LogWrap,FEEDS
from AimsUtility import AimsException
from Const import MAX_FEATURE_COUNT,THREAD_JOIN_TIMEOUT,PAGE_LIMIT,POOL_PAGE_CHECK_DELAY,THREAD_KEEPALIVE,FIRST_PAGE,LAST_PAGE_GUESS,ENABLE_ENTITY_EVALUATION,NULL_PAGE_VALUE as NPV
from FeatureFactory import FeatureFactory
aimslog = None

FPATH = os.path.join('..',os.path.dirname(__file__)) #base of local datastorage
#FNAME = 'data_hash'

#PAGES_INIT = 10
#PAGES_PERIOCDIC = 3
#FEED_REFRESH_DELAY = 10

pool_lock = threading.Lock()

class IncorrectlyConfiguredRequestClientException(AimsException):pass


class DataRequestChannel(Observable):
    '''Observable class providing request/response channel for user initiated actions '''
    
    def __init__(self,client):
        '''Initialises a new DRC using an instance of a feeds DataSync to communincate with contained feed functions
        @param client: DataSync object used as proxy to communicate with API
        @type client: DataSyncFeeds
        '''
        super(DataRequestChannel,self).__init__()
        if hasattr(client,'etft') and hasattr(client,'inq') and hasattr(client,'processInputQueue'):
            self.client = client
        else:
            raise IncorrectlyConfiguredRequestClientException('Require client with [ etft,inq,pIQ() ] attributes')
        
    def run(self):
        '''Run method using loop for thread keepalive'''
        while not self.stopped():
            aimslog.debug('DRC {} listening'.format(self.client.etft))
            time.sleep(THREAD_KEEPALIVE)
    
    def observe(self,_,*args,**kwargs):
        '''Override of observe method receiving calls from DataManager to trigger requests, on client
        @param _: Discarded observable.
        @param *args: Wrapped args
        @param **kwargs: Wrapped kwargs
        '''
        if self.stopped(): 
            aimslog.warn('DM attempt to call stopped DRC listener {}'.format(self.getName()))
            return
        aimslog.info('Processing request {}'.format(args[0]))
        if self.client.etft==args[0] and not self.client.inq.empty():
            changelist = self.client.inq.get()    
            aimslog.info('DRC {} - found {} items in queue'.format(self.client.etft,len(changelist)))
            self.client.processInputQueue(changelist)

    
class DataSync(Observable):
    '''Background thread triggering periodic data updates and synchronising update requests from DM.'''
    
    global aimslog
    aimslog = Logger.setup()
    
    duinst = {}
    
    #hash to compare latest fetched data
    #from DataManager import FEEDS
    #data_hash = {dh:0 for dh in DataManager.FEEDS}
    
    sw,ne = None,None
    
    def __init__(self,params,queues):
        '''Initialise new DataSync object splitting out config parameters
        @param params: List of configuration parameters
        @type params: List<?>
        @param queues: List of IOR queues
        @type queues: Dict<String,Queue.Queue>        
        '''
        #from DataManager import FEEDS
        super(DataSync,self).__init__()
        #thread reference, ft to AD/CF/RF, config info
        self.start_time = time.time()
        self.updater_running = False
        self.ref,self.etft,self.ftracker,self.conf = params
        self.data_hash = {dh:0 for dh in FEEDS.values()}
        self.factory = FeatureFactory.getInstance(self.etft)
        self.updater = DataUpdater.getInstance(self.etft) # unevaluated class
        self.inq = queues['in']
        self.outq = queues['out']
        self.respq = queues['resp']
        #
        self.pager = DataPager(params,queues)
        
        
    def setup(self,sw=None,ne=None):
        '''Parameter setup for coordinate feature requests.
        @param sw: South-West corner, coordinate value pair (optional)
        @type sw: List<Double>{2}
        @param ne: North-East corner, coordinate value pair (optional)
        @type ne: List<Double>{2}
        '''
        self.sw,self.ne = sw,ne

    def run(self):
        '''Continual loop running periodic feed fetch updates'''
        while not self.stopped():
            if not self.updater_running: self.pager.fetchPages(self.ftracker['threads'])
            time.sleep(self.ftracker['interval'])
            
    #@override
    def stop(self):
        '''Thread stop override to also stop subordinate threads'''
        #brutal stop on du threads
        for du in self.duinst.values():
            du.stop()
        self._stop.set()
    
    def close(self):
        '''Alias of stop'''
        self.stop()
        #self.inq.task_done()
        #self.outq.task_done()
        
    def observe(self,_,*args, **kwargs):
        '''Overridden observe method calling thread management function
        @params _: Discarded observable
        @param *args: Wrapped args, where we only use the first arg as the _updatePageRefs ref value
        @param **kwargs: Wrapped kwargs, discarded
        '''
        if not self.stopped():
            self.notify(self.etft)
            self.managePage((None,self.lastpage))
            
    #null method for features since page count not saved
    def managePage(self,p):pass

    #--------------------------------------------------------------------------
    
    def returnResp(self,resp):
        '''I{DEPRECATED} Function to put response objects in DataSync response queue
        @param resp: Response object, 
        @type resp: Feature
        '''
        aimslog.info('RESP.{}'.format(resp))
        self.respq.put(resp)
    
    #null method for features since page count not saved
    def _updatePageRefs(self,p):pass


class DataSyncFeatures(DataSync):
    '''DataSync subclass for the Features feed'''
    
    #ft = FeedType.FEATURES
    
    def __init__(self,params,queues):
        '''Initialisation for DataSync Features feed reader
        @param params: List of configuration parameters
        @type params: List<?>
        @param queues: List of IOR queues
        @type queues: Dict<String,Queue.Queue>
        '''
        super(DataSyncFeatures,self).__init__(params,queues)
        #self.ftracker = {'page':[1,1],'index':1,'threads':2,'interval':30}

        
class DataSyncFeeds(DataSync): 
    '''DataSync subclass for the Change and Resolution feeds'''
    
    parameters = {FeedRef((FeatureType.ADDRESS,FeedType.CHANGEFEED)):{'atype':ActionType,'action':DataUpdaterAction},
                  FeedRef((FeatureType.ADDRESS,FeedType.RESOLUTIONFEED)):{'atype':ApprovalType,'action':DataUpdaterApproval},
                  FeedRef((FeatureType.GROUPS,FeedType.CHANGEFEED)):{'atype':GroupActionType,'action':DataUpdaterGroupAction},
                  FeedRef((FeatureType.GROUPS,FeedType.RESOLUTIONFEED)):{'atype':GroupApprovalType,'action':DataUpdaterGroupApproval}
                  #FeedRef((FeatureType.USERS,FeedType.ADMIN)):{'atype':UserActionType,'action':DataUpdaterUserAction}
                  }
    
    def __init__(self,params,queues):
        '''Create an additional DRC thread to watch the feed input queue
        @param params: List of configuration parameters
        @type params: List<?>
        @param queues: List of IOR queues
        @type queues: Dict<String,Queue.Queue>   
        '''
        super(DataSyncFeeds,self).__init__(params,queues)
        self.drc = DataSyncFeeds.setupDRC(self,params[0])
        
    @staticmethod
    def setupDRC(client,p0):
        '''Static method to set up a request listener containing a instance of a matching DataSyncFeeds client
        @param client: DataSync object used as proxy to communicate with API
        @type client: DataSyncFeeds
        @param p0: The zero indexed parameter containing the client ref string
        @type p0: String
        @return: DataRequestChannel
        '''
        drc = DataRequestChannel(client)
        drc.setName('DRC.{}'.format(p0))
        drc.setDaemon(True)
        return drc
        
    def run(self):
        '''Start the DRC thread and then start self (doing periodic updates) using the super run'''
        self.drc.start()
        super(DataSyncFeeds,self).run()
    
    def stop(self):
        '''Thread stop also stops related DRC thread'''
        self.drc.stop()
        super(DataSyncFeeds,self).stop()

    def stopped(self):
        return super(DataSyncFeeds,self).stopped() and self.drc.stopped() 
    
    
    #Processes the input queue sending address changes to the API
    #@LogWrap.timediff
    def processInputQueue(self,changelist):
        '''Take the requests from an input queue and split out individual address objects for DU processing
        @param changelist: Dictionary of address lists taken from the input queue
        @type changelist: Dictionary<FeedRef,List<Feature>>  
        '''
        #{ADD:addr_1,RETIRE:adr_2...
        for at in changelist:
            #self.outq.put(act[addr](changelist[addr]))
            for feature in changelist[at]:
                duref = self.processFeature(at,feature)
                aimslog.info('{} thread started'.format(str(duref)))
                
    def processFeature(self,at,feature): 
        '''Individual feature request processor.
        @param at: Address/Group Action/Approval type indicator
        @type at: Integer 
        @param feature: Feature being acted upon/approved
        @type feature: Feature
        @return: Reference value for DataUpdater thread
        '''
        at2 = self.parameters[self.etft]['atype'].reverse[at][:3].capitalize()      
        ref = 'PR.{0}.{1:%y%m%d.%H%M%S}'.format(at2,DT.now())
        params = (ref,self.conf,self.factory)
        #self.ioq = {'in':Queue.Queue(),'out':Queue.Queue()}
        self.duinst[ref] = self.parameters[self.etft]['action'](params,self.respq)
        self.duinst[ref].setup(self.etft,at,feature,None)
        #print 'PROCESS FEAT',self.etft,ref
        self.duinst[ref].setName(ref)
        self.duinst[ref].setDaemon(True)
        self.duinst[ref].start()
        #self.duinst[ref].join()
        return ref
    
    def _updatePageRefs(self,p):
        '''Saves page numbers back to tracker array
        @param p: first and last page numbers
        @type p: List<Integer>{2}
        '''
        if p[0]: self.ftracker['page'][0] = p[0]
        if p[1]: self.ftracker['page'][1] = p[1]
        
class DataSyncAdmin(DataSyncFeeds):
    '''Admin DS class that doesn't update and is only used as a admin client request channel'''
    
    parameters = {FeedRef((FeatureType.USERS,FeedType.ADMIN)):{'atype':UserActionType,'action':DataUpdaterUserAction}}
        
    def __init__(self,params,queues):
        '''Admin feed initialiser
        @param params: List of configuration parameters
        @type params: List<?>
        @param queues: List of IOR queues
        @type queues: Dict<String,Queue.Queue>
        '''
        super(DataSyncAdmin,self).__init__(params,queues)
        #self.drc = DataSyncAdmin.setupDRC(self,params[0])
        
    def run(self):
        '''Admin feed run but with no requirement to read admin feed only starts the DRC'''
        self.drc.start()
        
  
        
        
    

    
        
        