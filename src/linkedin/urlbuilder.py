#!/usr/bin/env python3

from ..constants import LINKEDIN_HOST, LINKEDIN_NORMAL_SEARCH_PATH, LINKEDIN_PARTIAL_SEARCH_PATH
from ..utility import isNullOrWhiteSpace, buildUrl, getTrimmedStringValueOrEmptyString, getEnumValueOrEmptyString
from .searchparams import *

class UrlBuilder:

    @staticmethod
    def buildUrl(searchParams: SearchParams, extraParams: dict = {}) -> str:
        if isNullOrWhiteSpace(searchParams.query):
            raise ValueError('Query string cannot be null or white space.')
        if isNullOrWhiteSpace(searchParams.location):
            raise ValueError('Location cannot be null or white space.')
        
        queryStringDict = { 
            'keywords': getTrimmedStringValueOrEmptyString(searchParams.query),
            'location': getTrimmedStringValueOrEmptyString(searchParams.location),
            'f_TPR': getEnumValueOrEmptyString(searchParams.dateRange),
            'f_SB2': getEnumValueOrEmptyString(searchParams.salary),
            'f_E': getEnumValueOrEmptyString(searchParams.experienceLevel),
            'f_WT': getEnumValueOrEmptyString(searchParams.remoteFilter),
            'f_JT': getEnumValueOrEmptyString(searchParams.jobType),
            'distance': getEnumValueOrEmptyString(searchParams.withinMiles)
        }

        # pop: delete key from dict and return its value, substitute with default value if doesn't exist
        if extraParams.pop('partial', False):
            searchPath = LINKEDIN_PARTIAL_SEARCH_PATH
        else:
            searchPath = LINKEDIN_NORMAL_SEARCH_PATH
        
        mergedDict = {**queryStringDict, **extraParams}

        # remove keys with values == ''
        filteredQueryStringDict = {key:value for (key,value) in mergedDict.items() if value}

        return buildUrl(LINKEDIN_HOST, searchPath, filteredQueryStringDict)