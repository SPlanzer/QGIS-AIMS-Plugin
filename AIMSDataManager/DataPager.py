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
import random

from Observable import Observable
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

 
class DataPager(Observable):
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
        super(DataPager,self).__init__()
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

        

    def run(self):
        '''Continual loop running periodic feed fetch updates'''
        while not self.stopped():
            if not self.updater_running: self.fetchPages(self.ftracker['threads'])
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
        @param *args: Wrapped args, where we only use the first arg as the managePage ref value
        @param **kwargs: Wrapped kwargs, discarded
        '''
        if not self.stopped():
            self._managePage(args[0])
        
    def _managePage(self,ref):
        '''Thread management function called when a periodic thread ends, posting new data and starting a new thread in pool if required
        @param ref: Unique reference string
        @type ref: String
        '''
        print 'REF (remove)',ref
        #print '{}{} finished'.format(FeedType.reverse[self.ft][:2].capitalize(),r['page'])
        aimslog.info('Extracting queue for DU pool {}'.format(ref))
        #print [r['ref'] for r in self.pool]
        #print 'extracting queue for DU pool {}'.format(ref)
        r = None
        with pool_lock:
            aimslog.info('{} complete'.format(ref))
            #print 'POOLSTATE',self.pool  
            #print 'POOLREMOVE',ref
            r = [x for x in self.pool if x['ref']==ref][0] 
            alist = self.duinst[ref].queue.get()
            acount = len(alist)
            self.newaddr += alist
            nextpage = max([r2['page'] for r2 in self.pool])+1
            #del self.duinst[ref]#ERROR? this cant be good, removing the DU during its own call to notify
            aimslog.debug('PAGE TIME {} {}s'.format(ref,time.time()-r['time']))
            #print 'POOLTIME {} {}'.format(ref,time.time()-r['time'])
            self.pool.remove(r)
            #if N>0 features return, spawn another thread
            if acount<MAX_FEATURE_COUNT:
                #non-full page returned, must be the last one
                self.exhausted = r['page']
            if acount>0:
                #features returned, not zero and not less than max so get another
                self.lastpage = max(r['page'],self.lastpage)
                if nextpage<self.exhausted:
                    ref = self._monitorPage(nextpage)
                    self.pool.append({'page':nextpage,'ref':ref,'time':time.time()})
                    #print 'POOLADD 2',ref
            else:
                pass
                #print 'No addresses found in page {}{}'.format(FeedType.reverse[self.ft][:2].capitalize(),r['page'])
            
        #when the pool is empty all the pages have been fetched. bundle these and notify
        if len(self.pool)==0:
            #syncfeeds does notify DS
            self.returnFeeds(self.newaddr)
            #managepage does tracker updating
            #self.managePage((None,self.lastpage))
            aimslog.debug('FULL TIME {} took {}s'.format(ref,time.time()-self.start_time))
            self.updater_running = False
            #print 'POOLCLOSE',ref,time.strftime('%Y-%M-%d %H:%m:%S')
            self.notify(self.etft)
            
    #NOTE. To override the behaviour, return feed once full, override this method RLock
    def returnFeeds(self,new_addresses):
        '''Checks if supplied addresses are different from a saved existing set and return in the out queue, with notification
        @param new_addresses: List of all fetched pages from a full feed request, spanning all pages
        @type new_addresses: List<Feature>
        '''
        #new_hash = hash(frozenset(new_addresses))
        new_hash = hash(frozenset([na.getHash() for na in new_addresses]))
        if self.data_hash[self.etft] != new_hash:
            #print '>>> Changes in {} hash\n{}\n{}'.format(self.etft,self.data_hash[self.etft],new_hash)
            self.data_hash[self.etft] = new_hash
            #with sync_lock:
            self.outq.put(new_addresses)
            self.outq.task_done()


    #--------------------------------------------------------------------------            

    #@LogWrap.timediff
    def fetchPages(self,thr,lastpage=FIRST_PAGE):
        '''Main feed updater method
        @param thr: Number of updater threads to spawn into pool, this can be negative to count back from a lastpage value
        @type thr; Integer
        @param lastpage: Initial page number for feed requests
        @type lastpage: Integer
        '''
        self.updater_running = True
        self.exhausted = PAGE_LIMIT
        self.lastpage = lastpage
        self.newaddr = []
        #print 'LP {} {}->{}'.format(FeedType.reverse[self.ft][:2].capitalize(),lastpage,lastpage+thr)
        with pool_lock: self.pool = self._buildPool(lastpage,thr)

    def _buildPool(self,lastpage,thr):
        '''Builds a pool based on page spec provided, accepts negative thresholds for backfill requests
        @param thr: Number of updater threads to spawn into pool, this can be negative to count back from a lastpage value
        @type thr; Integer
        @param lastpage: Initial page number for feed requests
        @type lastpage: Integer
        '''
        span = range(min(lastpage,lastpage+thr),max(lastpage,lastpage+thr))
        return [{'page':pno,'ref':self._monitorPage(pno),'time':time.time()} for pno in span]
    
    def _monitorPage(self,pno):
        '''Initialise and store a DataUpdater instance for a single page request
        @param pno: Page number to build DataUpdater request from
        @type pno: Integer
        @return: DataUpdater reference value
        '''
        
        ref = 'FP.{0}.Page{1}.{2:%y%m%d.%H%M%S}.{3}'.format(self.etft,pno,DT.now(),str(random.randint(0,1000)).zfill(3))
        aimslog.info('init DU {}'.format(ref))
        self.duinst[ref] = self._fetchFeedPage(ref,pno)
        self.duinst[ref].register(self)
        self.duinst[ref].start()
        print 'REF (append)',ref
        return ref    
    
    
    def _fetchRequestPage(self,ref,pno):
        '''Build DataUpdate request instance          
        @param ref: Unique reference string
        @type ref: String      
        @param pno: Page number to build DataUpdater request from
        @type pno: Integer
        @return: DataUpdater
        '''   
        params = (ref,self.conf,self.factory)
        adrq = Queue.Queue()
        du = self.updater(params,adrq)
        #address/feature requests called with bbox parameters
        if self.etft==FEEDS['AF']: du.setup(self.etft,self.sw,self.ne,pno)
        else: du.setup(self.etft,None,None,pno)
        du.setName(ref)
        du.setDaemon(True)
        return du
    
    def _fetchFeedPage(self,ref,pno):
        '''Build DataUpdate instance          
        @param ref: Unique reference string
        @type ref: String      
        @param pno: Page number to build DataUpdater request from
        @type pno: Integer
        @return: DataUpdater
        '''   
        params = (ref,self.conf,self.factory)
        adrq = Queue.Queue()
        du = self.updater(params,adrq)
        #address/feature requests called with bbox parameters
        if self.etft==FEEDS['AF']: du.setup(self.etft,self.sw,self.ne,pno)
        else: du.setup(self.etft,None,None,pno)
        du.setName(ref)
        du.setDaemon(True)
        return du
    

    

    
        
        