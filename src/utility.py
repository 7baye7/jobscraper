#!/usr/bin/env python3

import urllib
from enum import Enum
import os

def isNullOrWhiteSpace (s: str) -> bool:
    return not (s and s.strip())

def buildUrl(baseUrl: str, path: str, queryParams: dict) -> str:
    # Returns a list in the structure of urlparse.ParseResult
    url_parts = list(urllib.parse.urlparse(baseUrl))
    url_parts[2] = path
    url_parts[4] = urllib.parse.urlencode(queryParams)
    return urllib.parse.urlunparse(url_parts)

def getTrimmedStringValueOrEmptyString(s: str) -> str:
    return '' if isNullOrWhiteSpace(s) else s.strip()
        
def getEnumValueOrEmptyString(v: Enum) -> str:
    return '' if v is None else v.value
    
def getAbsPathRelativeToFile(filePath: str, *childPathParts: str) -> str:
    return os.path.join(os.path.dirname(os.path.abspath(filePath)), *childPathParts)