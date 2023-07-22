#!/usr/bin/env python3

from enum import Enum

class DateRange(str, Enum):
    Last24Hours = '1'
    Last3Days = '3'
    Last7Days = '7'
    Last14Days = '14'

class Remote(str, Enum):
    Remote = 'attr(DSQF7)'
    TemporarilyRemote = 'attr(VAMUB)'

class JobType(str, Enum):
    FullTime = 'jt(fulltime)'
    Contract = 'jt(contract)'
    PartTime = 'jt(parttime)'
    Temporary = 'jt(temporary)'
    Internship = 'jt(internship)'

class WithinMiles(str, Enum):
    Exact = '0'
    Within5Miles = '5'
    Within10Miles = '10'
    Within15Miles = '15'
    Within25Miles = '25'
    Within35Miles = '35'
    Within50Miles = '50'
    Within100Miles = '100'

class PostedBy(str, Enum):
    Employer = 'exrec()'
    StaffingAgency = 'exdh()'

class ExperienceLevel(str, Enum):
    NoExperienceRequired = 'attr(D7S5D)'
    EntryLevel = 'explvl(ENTRY_LEVEL)'
    MidLevel = 'explvl(MID_LEVEL)'
    SeniorLevel = 'explvl(SENIOR_LEVEL)'

class Education(str, Enum):
    HighSchool = 'attr(FCGTU|QJZM9,OR)'
    Associate = 'attr(FCGTU|QJZM9|UTPWG,OR)'
    Bachelor = 'attr(FCGTU|HFDVW|QJZM9|UTPWG,OR)'
    Master = 'attr(EXSNN|FCGTU|HFDVW|QJZM9|UTPWG,OR)'
    Doctor = 'attr(6QC5F,OR)'

class EncouragedToApply(str, Enum):
    NoCollegeDiploma = 'attr(JPSJ9)'
    FairChance = 'attr(Q5R8A)'
    MilitaryEncouraged = 'attr(MUDKG)'
    BackToWork = 'attr(NKKX4)'
    NoHighSchoolDiploma = 'attr(CFNJG)'