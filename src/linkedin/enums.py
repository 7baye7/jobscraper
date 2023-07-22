#!/usr/bin/env python3

from enum import Enum

class DateRange(str, Enum):
    PastMonth = 'r2592000'
    PastWeek = 'r604800'
    Past24Hours = 'r86400'

class ExperienceLevel(str, Enum):
    Internship = '1'
    EntryLevel = '2'
    Associate  = '3'
    Senior = '4'
    Director = '5'
    Executive = '6'

class JobType(str, Enum):
    FullTime = 'F'
    PartTime = 'P'
    Contract = 'C'
    Temporary = 'T'
    Volunteer = 'V'
    Internship = 'I'

class Remote(str, Enum):
    OnSite = '1'
    Remote = '2'
    Hybrid = '3'

class Salary(str, Enum):
    _40000 = '1'
    _60000 = '2'
    _80000  = '3'
    _100000 = '4'
    _120000 = '5'

class WithinMiles(str, Enum):
    _10 = '10'
    _25 = '25'
    _50 = '50'
    _75 = '75'
    _100 = '100'