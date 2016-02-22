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

from urllib2 import HTTPError, base64, ProxyHandler
from datetime import datetime as DT
#from functools import wraps

import Image, ImageStat, ImageDraw
import urllib2
import StringIO
import random
import os
import sys
import re
import pickle
import getopt
import logging
import zipfile
import time
import threading
import Queue


from DataUpdater import DataUpdater,DataUpdaterAction,DataUpdaterApproval
from AimsApi import AimsApi 
from AimsLogging import Logger
from AimsUtility import ActionType,ApprovalType,FeedType,LogWrap,MAX_FEATURE_COUNT
from AddressFactory import AddressFactory#,AddressChangeFactory,AddressResolutionFactory
aimslog = None

FPATH = os.path.join('..',os.path.dirname(__file__)) #base of local datastorage
FNAME = 'data_hash'

PAGES_INIT = 10
PAGE_LIMIT = 1000
PAGES_PERIOCDIC = 3
POOL_PAGE_CHECK_DELAY = 0.2
QUEUE_CHECK_DELAY = 1
LAST_PAGE_GUESS = 1000


class DataSync(threading.Thread):
    '''Background thread triggering periodic data updates and synchronising update requests from DM.  
    '''
    
    global aimslog
    aimslog = Logger.setup()
    
    lock = threading.Lock()
    duinst = {}
    
    #hash to compare latest fetched data
    data_hash = {ft:0 for ft in FeedType.reverse}
    
    sw,ne = None,None
    
    def __init__(self,params,queues):
        threading.Thread.__init__(self)
        #thread reference, ft to AD/CF/RF, config info
        self.ref,self.ft,self.ftracker,self.conf = params
        self.afactory = AddressFactory.getInstance(self.ft)
        self.inq = queues['in']
        self.outq = queues['out']
        self.respq = queues['resp']
        self._stop = threading.Event()
        
    def setup(self,sw=None,ne=None):
        '''Parameter setup'''
        self.sw,self.ne = sw,ne
        

    def run(self):
        '''Continual loop looking for input queue requests and running periodic updates'''
        start = int(time.time())
        while True:
            #if there are things in the input queue, process them, push to CF #TODO. there shouldnt ever be anything in the FF inq
            now = int(time.time())
            if not self.inq.empty():
                changelist = self.inq.get()    
                aimslog.info('FT {} - found {} items in queue'.format(FeedType.reverse[self.ft],len(changelist)))
                self.processInputQueue(changelist)
            
            if (now-start) % self.ftracker['interval']:
                #aimslog.debug('process Q={}'.format(len(self.duinst)))
                self.syncFeeds(self.fetchFeedUpdates(self.ftracker['threads']))
                aimslog.debug('FT {} sleeping {} with size(Qin)={}'.format(FeedType.reverse[self.ft],self.ftracker['interval'],self.inq.qsize())) 
            time.sleep(QUEUE_CHECK_DELAY)
            
        
    def stop(self):
        self._stop.set()

    def stopped(self):
        return self._stop.isSet()
    
    def close(self):
        self.inq.task_done()
        self.outq.task_done()

    #--------------------------------------------------------------------------
#     def fetchAllUpdates(self,pt):
#         '''get full page loads from the three different queues, maybe split out layer'''
#         for ft in FeedType.reverse:
#             self.fetchFeedUpdates(ft, pt)
            

    @LogWrap.timediff
    def fetchFeedUpdates(self,thr):
        '''get full page loads'''
        exhausted = PAGE_LIMIT
        newaddr = []
        pg,ii = self.ftracker['page'],self.ftracker['index']
        backpage,lastpage = pg if pg else 2*(self._findLastPage(LAST_PAGE_GUESS),)
        #setup pool
        #print 'LP {} {}->{}'.format(FeedType.reverse[self.ft][:2].capitalize(),lastpage,lastpage+thr)
        pool = [{'page':p,'ref':None} for p in range(lastpage,lastpage+thr)]
        for r in pool:
            r['ref'] = self.fetchPage(r['page'])
        
        while len(pool)>0:#any([p[2] for p in pool if p[2]>1])
            for r in pool:
                print 'checking page {}{} pool={}'.format(FeedType.reverse[self.ft][:2].capitalize(), r['page'],[p['page'] for p in pool]) 
                du = self.duinst[r['ref']]
                #print 'DU',du.isAlive()
                #if len(pool) == 1 and r['page'] == 6: #DEBUG
                #    print 'halt' 
                if not du.isAlive():
                    print '{}{} finished'.format(FeedType.reverse[self.ft][:2].capitalize(),r['page'])
                    alist = du.queue.get()
                    acount = len(alist)
                    newaddr += alist
                    nextpage = max([r2['page'] for r2 in pool])+1
                    del self.duinst[r['ref']]
                    pool.remove(r)
                    #if N>0 features return, spawn another thread
                    if acount<MAX_FEATURE_COUNT:
                        exhausted = r['page']
                    if acount>0:
                        lastpage = max(r['page'],lastpage)
                        if nextpage<exhausted:
                            ref = self.fetchPage(nextpage)
                            pool.append({'page':nextpage,'ref':ref})
                    else:
                        pass
                        print 'no addresses in page {}{}'.format(FeedType.reverse[self.ft][:2].capitalize(),r['page'])
                time.sleep(POOL_PAGE_CHECK_DELAY)
                print '---------\n'
        #update CF tracker with latest page number
        self.managePage((backpage,lastpage))
        print 'leaving {} with pool={}'.format(FeedType.reverse[self.ft][:2].capitalize(),[p['page'] for p in pool])
        print [a.__str__() for a in newaddr]
        return newaddr
            
    def fetchPage(self,p):
        '''Regular page fetch, periodic or demand'''   
        ft2 = FeedType.reverse[self.ft][:2].capitalize()
        ref = 'Get.{0}.Page{1}.{2:%y%m%d.%H%M%S}.{3}'.format(ft2,p,DT.now(),p)
        params = (ref,self.conf,self.afactory)
        adrq = Queue.Queue()
        self.duinst[ref] = DataUpdater(params,adrq)
        if self.ft==FeedType.FEATURES: self.duinst[ref].setup(self.ft,self.sw,self.ne,p)
        else: self.duinst[ref].setup(self.ft,None,None,p)
        self.duinst[ref].setDaemon(False)
        self.duinst[ref].start()
        return ref
        #self.duinst[ref].join()
        #return adrq.get()

    def syncFeeds(self,new_addr):
        '''return all new addresses'''
        new_hash = hash(frozenset(new_addr))
        if self.data_hash != new_hash:
            self.data_hash = new_hash
            self.outq.put(new_addr)
            
    def managePage(self,p):
        ''''default behaviour is to not manage page counts and re read features from scratch
        for the CF (RF too?) we must read from the last saved page but reset on startup'''
        pass
    #--------------------------------------------------------------------------
    
    def returnResp(self,resp):
        aimslog.info('RESP.{}'.format(resp))
        self.respq.put(resp)


class DataSyncFeatures(DataSync):
    
    #ft = FeedType.FEATURES
    
    def __init__(self,params,queues):
        super(DataSyncFeatures,self).__init__(params,queues)
        self.ftracker = {'page':[1,1],'index':1,'threads':3,'interval':60}    


class DataSyncFeeds(DataSync): 
    
    def fetchFeedUpdates(self,thr):
        '''run forward updates and tack on a single backfill, update page count accordingly'''
        res = super(DataSyncFeeds,self).fetchFeedUpdates(thr)
        ps,pe = self.ftracker['page']
        #for i in range(5):#do a bunch of backfills?
        res += self.backfillPage(ps)
        return res
        
    def _findLastPage(self,p_end):
        '''Inefficient way to find the last page in the feed sequence'''
        p_start = 0
        p_end = p_end*2
        while True:
            p = int((pstart+p_end)/2)
            ref = self.fetchPage((pstart+p_end)/2)
            self.duinst[ref]
            if not self.duinst[ref].isAlive():
                acount = len(du.queue.get())
                aimslog.debug('Page Find p{}={}'.format(p,acount))
                if acount==AimsApi.MAX_COUNT:
                    if p == p_start: p_end = p_end*2 
                    p_start = p
                elif acount>0: return p
                else: p_end = p         
    
    def backfillPage(self,prevpage):
        '''backfills pages from requested page. non-pooled/non-tracked since non critical'''
        newaddr = []
                
        ref = self.fetchPage(prevpage)
        du = self.duinst[ref]
        while du.isAlive(): pass
        alist = du.queue.get()
        acount = len(alist)
        newaddr += self._statusFilter(alist)
        del self.duinst[ref]
        if acount>0:
            prevpage = max(0,prevpage-1)
            ref = self.fetchPage(prevpage)                
                
        #update CF tracker with latest page number
        self.managePage((prevpage,None))
        return newaddr

    def _statusFilter(self,alist):
        #something like this
        return [a for a in alist if a.getQueueStatus().lower() not in ('expired','deleted')]
    
    #Processes the input queue sending address changes to the API
    @LogWrap.timediff
    def processInputQueue(self,changelist):
        '''Take the input change queue and split out individual address objects for DU processing'''
        #{ADD:addr_1,RETIRE:adr_2...
        for at in changelist:
            #self.outq.put(act[addr](changelist[addr]))
            for address in changelist[at]:
                resp = self.processAddress(at,address)
                aimslog.info('{} finished'.format(str(resp)))
                
    def managePage(self,p):
        if p[0]: self.ftracker['page'][0] = p[0]
        if p[1]: self.ftracker['page'][1] = p[1]

class DataSyncChangeFeed(DataSyncFeeds):
      
    def __init__(self,params,queues):
        super(DataSyncChangeFeed,self).__init__(params,queues)
        self.ftracker = {'page':[1,1],'index':1,'threads':1,'interval':10}

    def processAddress(self,at,addr):  
        at2 = ApprovalType.reverse[at][:3].capitalize()      
        ref = 'Req{0}.{1:%y%m%d.%H%M%S}'.format(at2,DT.now())
        params = (ref,self.conf,self.afactory)
        #self.ioq = {'in':Queue.Queue(),'out':Queue.Queue()}
        self.duinst[ref] = DataUpdaterAction(params,self.respq)
        self.duinst[ref].setup(at,addr)
        self.duinst[ref].setDaemon(False)
        self.duinst[ref].start()
        #self.duinst[ref].join()
        return ref


class DataSyncResolutionFeed(DataSyncFeeds):
    
    def __init__(self,params,queues):
        super(DataSyncResolutionFeed,self).__init__(params,queues)
        self.ftracker = {'page':[1,1],'index':1,'threads':1,'interval':10}
        
    def processAddress(self,at,addr):  
        at2 = ApprovalType.reverse[at][:3].capitalize()      
        ref = 'Req{0}.{1:%y%m%d.%H%M%S}'.format(at2,DT.now())
        params = (ref,self.conf,self.afactory)
        #self.ioq = {'in':Queue.Queue(),'out':Queue.Queue()}
        self.duinst[ref] = DataUpdaterApproval(params,self.respq)
        self.duinst[ref].setup(at,addr)
        self.duinst[ref].setDaemon(False)
        self.duinst[ref].start()
        #self.duinst[ref].join()
        return ref
    

    
        
        