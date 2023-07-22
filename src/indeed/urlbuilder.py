#!/usr/bin/env python3

from ..constants import INDEED_HOST, INDEED_SEARCH_PATH
from ..utility import isNullOrWhiteSpace, getTrimmedStringValueOrEmptyString, getEnumValueOrEmptyString, buildUrl
from .searchparams import *

class UrlBuilder:
   
    @staticmethod
    def __getCompanyFccKeyValue(fccKey: str) -> str:
        if isNullOrWhiteSpace(fccKey):
            return ''
        else:
            return 'fcckey(%s)' % fccKey
        
    @staticmethod
    def __getSecondaryLocationDict(secondaryLocation: Location) -> dict:
        if secondaryLocation is None:
            return {}
        else:
            return vars(secondaryLocation)

    @staticmethod
    def __getScParameterValue(searchParams: SearchParams) -> str:
        # Remote.Remote + 
        # ExperienceLevel.MidLevel + 
        # Education.Master +
        # PostedBy.Employer = 
        # sc=0bf:exrec(),kf:attr(DSQF7)attr(EXSNN|FCGTU|HFDVW|QJZM9|UTPWG,OR)explvl(MID_LEVEL);
        kfOrBfDict = {
            'bf': [ getEnumValueOrEmptyString(searchParams.postedBy) ],
            'kf': [ getEnumValueOrEmptyString(searchParams.remoteOrTemporarilyRemote),
                    getEnumValueOrEmptyString(searchParams.jobType),
                    getEnumValueOrEmptyString(searchParams.experienceLevel),
                    getEnumValueOrEmptyString(searchParams.education),
                    getEnumValueOrEmptyString(searchParams.encouragedToApply),
                    UrlBuilder.__getCompanyFccKeyValue(searchParams.companyFccKey) ]
        }

        # remove keys from kfOrBfDict if all of their values are empty strings AND remove values from keys if values are empty
        # {'kf': ['', 'attr(DSQF7)', 'explvl(MID_LEVEL)'], 'bf': ['', '']} -> {'kf': ['attr(DSQF7)', 'explvl(MID_LEVEL)']}
        filteredKfOrBfDict = {key: list(filter(lambda v: not isNullOrWhiteSpace(v), values)) for (key,values) in kfOrBfDict.items() if any([not isNullOrWhiteSpace(value) for value in values])}

        if filteredKfOrBfDict:
            # '0kf:attr(DSQF7)explvl(MID_LEVEL);'
            return '0%s;' % ','.join(list(map(lambda key: '%s:%s' % (key, ''.join(filteredKfOrBfDict[key])), filteredKfOrBfDict.keys())))
        else:
            return ''

    @staticmethod
    def buildUrl(searchParams: SearchParams, extraParams: dict = {}) -> str:
        if isNullOrWhiteSpace(searchParams.query):
            raise Exception('Query string cannot be null or white space.')
        if isNullOrWhiteSpace(searchParams.location):
            raise Exception('Location cannot be null or white space.')
        
        queryStringDict = { 
            'q': getTrimmedStringValueOrEmptyString('%s %s' % (getTrimmedStringValueOrEmptyString(searchParams.query),
                                                               getTrimmedStringValueOrEmptyString(searchParams.salary))),
            'l': getTrimmedStringValueOrEmptyString(searchParams.location),
            'fromage': getEnumValueOrEmptyString(searchParams.dateRange),
            'radius': getEnumValueOrEmptyString(searchParams.withinMiles),
            'sc': UrlBuilder.__getScParameterValue(searchParams)
        }
        
        mergedDict = {**queryStringDict, **UrlBuilder.__getSecondaryLocationDict(searchParams.secondaryLocation), **extraParams}

        # remove keys with values == ''
        filteredQueryStringDict = {key:value for (key,value) in mergedDict.items() if value}

        return buildUrl(INDEED_HOST, INDEED_SEARCH_PATH, filteredQueryStringDict)