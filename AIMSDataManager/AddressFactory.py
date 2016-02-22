#!/usr/bin/python
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
################################################################################

#http://devassgeo01:8080/aims/api/address/features - properties
import re
import os
import copy
from AimsUtility import ActionType,ApprovalType,FeedType,InvalidEnumerationType
from Address import Address,AddressChange,AddressResolution,Position,DEF_SEP

P = os.path.join(os.path.dirname(__file__),'../resources/')

TP = {FeedType.FEATURES:{},
      FeedType.CHANGEFEED:{ActionType.reverse[at]:None for at in ActionType.reverse},
      FeedType.RESOLUTIONFEED:{ApprovalType.reverse[at]:None for at in ApprovalType.reverse}}

#AT = {FeedType.FEATURES:Address,FeedType.CHANGEFEED:AddressChange,FeedType.RESOLUTIONFEED:AddressResolution}

DEF_SEP = '_'
SKIP_NULL = True

    
class AddressFieldRequiredException(Exception): pass
class AddressFieldIncorrectException(Exception): pass

class AddressFactory(object):
    ''' AddressFactory class used to build address objects without the overhead of re-reading templates each time''' 
    AFFT = FeedType.FEATURES
    addrtype = Address
    reqtype = None
    
    def __init__(self, ref=None): 
        self.template = TemplateReader().get()[self.AFFT]
    
    def __str__(self):
        return 'AFC.{}'.format(FeedType.reverse(self.AFFT)[:3])
    
    @staticmethod
    def getInstance(ft):
        '''gets a factory instance'''
        if ft==FeedType.FEATURES: return AddressFactory(ft)
        elif ft==FeedType.CHANGEFEED: return AddressChangeFactory(ft)
        elif ft==FeedType.RESOLUTIONFEED: return AddressResolutionFactory(ft)
        else: raise InvalidEnumerationType('FeedType {} not available'.format(ft))
    
    
    def getAddress(self,ref=None,adr=None,model=None,prefix=''):
        '''Creates an address object from a model using a template if not provided'''
        adr = adr if adr else self.addrtype(ref)
        data = model if model else self.template['response']   
        for k in data:
            setter = 'set'+k[0].upper()+k[1:]
            if isinstance(data[k],dict): adr = self.getAddress(ref=ref,adr=adr,model=data[k],prefix=prefix+DEF_SEP+k)
            else: getattr(adr,setter)(data[k] or None) if hasattr(adr,setter) else setattr(adr,prefix+DEF_SEP+k,data[k] or None)
        return adr
        

class AddressFeedFactory(AddressFactory):
        
    PBRANCH = '{d}{}{d}{}'.format(d=DEF_SEP,*Position.BRANCH)
    
    def convertAddress(self,adr,at):
        '''Converts an address into its json payload equivalent '''
        full = self._convert(adr, copy.copy(self.template[self.reqtype.reverse[at]]), '')
        return self._delNull(full) if SKIP_NULL else full
    
    def _convert(self,adr,dat,key):
        for attr in dat:
            new_key = key+DEF_SEP+attr
            if new_key == self.PBRANCH:
                dat[attr] = adr.getAddressPositions()
            elif isinstance(dat[attr],dict):
                dat[attr] = self._convert(adr, dat[attr],new_key)
            else:
                dat[attr] = self._assign(dat,adr,new_key)
        return dat
    
    def _assign(self,dat,adr,key):
        '''validates address data value against template requirements'''
        required,oneof,default,datatype = 4*(None,)
        val = adr.__dict__[key] if hasattr(adr,key) else None
        dft =  dat[key[key.rfind(DEF_SEP)+1:]]
        if dft and dft.startswith('#'):
            pi = dft.replace('#','').split(',')
            required = 'required' in pi
            oneof = [pv[6:].strip('()').split('|') for pv in pi if pv.startswith('oneof')]
            default = oneof[0][0] if required and oneof else None
        if required and not val:
            print 'error AddressFieldRequired',key
            raise AddressFieldRequiredException('Address field {} required'.format(key))
        if oneof and val and val not in oneof[0]:
            print 'error AddressFieldIncorrect',key,val
            raise AddressFieldIncorrectException('Address field {}={} not one of {}'.format(key,val,oneof[0]))
        return val if val else default
    
    def _delNull(self, obj):
        if hasattr(obj, 'items'):
            new_obj = type(obj)()
            for k in obj:
                #if k != 'NULL' and obj[k] != 'NULL' and obj[k] != None:
                if k and obj[k]:
                    res = self._delNull(obj[k])
                    if res: new_obj[k] = res
        elif hasattr(obj, '__iter__'):
            new_obj = [] 
            for it in obj:
                #if it != 'NULL' and it != None:
                if it: new_obj.append(self._delNull(it))
        else: return obj
        return type(obj)(new_obj)     

            
        
        
class AddressChangeFactory(AddressFeedFactory):
    AFFT = FeedType.CHANGEFEED
    addrtype = AddressChange
    reqtype = ActionType
    def __init__(self,ref=None):
        super(AddressChangeFactory,self).__init__(ref)


class AddressResolutionFactory(AddressFeedFactory):
    AFFT = FeedType.RESOLUTIONFEED
    addrtype = AddressResolution
    reqtype = ApprovalType
    def __init__(self,ref=None):
        super(AddressResolutionFactory,self).__init__(ref)
        
    def getAddress(self,ref=None,adr=None,model=None,prefix=''):
        adrr = super(AddressResolutionFactory,self).getAddress(ref,adr,model,prefix)
        adrr.setWarnings([])
        return adrr


class TemplateReader(object):
    tp = TP
    def __init__(self):
        for t1 in self.tp:
            t1t = FeedType.reverse[t1].lower()
            for t2 in self.tp[t1]:
                #t2t = ActionType.reverse[t2].lower()
                t2t = t2.lower()
                with open(os.path.join(P,'{}.{}.template'.format(t1t,t2t)),'r') as handle:
                    tstr = handle.read()
                    #print 'read template',t1t,t2t
                    self.tp[t1][t2] = eval(tstr) if tstr else ''
            #response address type is the template of the address-json we get from the api
            with open(os.path.join(P,'{}.response.template'.format(t1t)),'r') as handle:
                tstr = handle.read()
                self.tp[t1]['response'] = eval(tstr) if tstr else ''

    def get(self):
        return self.tp
    
    
def test():
    from pprint import pprint as pp
    af_f = AddressFactory.getInstance(FeedType.FEATURES)
    af_c = AddressFactory.getInstance(FeedType.CHANGEFEED)
    af_r = AddressFactory.getInstance(FeedType.RESOLUTIONFEED)
    
    
    axx = af_r.getAddress()
    ac1 = af_f.getAddress()
    #ac1._addressedObject_externalObjectId = 1000
    ac1._components_addressType = 'Road'
    ac1._components_addressNumber = 100
    ac1._components_roadName = 'The Terrace'
    ac1._version = 1
    ac1._components_addressId = 100
    
    ac1a = af_c.convertAddress(ac1,ActionType.ADD)
    ac1r = af_c.convertAddress(ac1,ActionType.RETIRE)
    ac1u = af_c.convertAddress(ac1,ActionType.UPDATE)
    
    #------------------------------------------------
    
    ar1 = af_c.getAddress()
    ar1._version = 100
    ar1._changeId = 100
    ar1._components_addressType = 'Road'
    ar1._components_addressNumber = 100
    ar1._components_roadName = 'The Terrace'
    
    ar1a = af_r.convertAddress(ar1,ApprovalType.ACCEPT)
    ar1d = af_r.convertAddress(ar1,ApprovalType.DECLINE)
    ar1u = af_r.convertAddress(ar1,ApprovalType.UPDATE)
    
    print 'CHGF-ADD'
    pp(ac1a)
    print 'CHGF-RET'
    pp(ac1r)
    print 'CHGF-UPD'
    pp(ac1u)
    
    print 'RESF-ACC'
    pp(ar1a)
    print 'RESF-DEC'
    pp(ar1d)
    print 'RESF-UPD'
    pp(ar1u)

            
if __name__ == '__main__':
    test()      