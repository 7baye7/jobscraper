#!/usr/bin/env python3

from .enums import *
from ..base.basesearchparams import BaseSearchParams

class Location:
    rbl: str
    jlid: str
    def __init__(self, rbl, jlid):
        self.rbl = rbl
        self.jlid = jlid

class SearchParams(BaseSearchParams):
    dateRange: DateRange
    remoteOrTemporarilyRemote: Remote
    jobType: JobType
    withinMiles: WithinMiles
    postedBy: PostedBy
    experienceLevel: ExperienceLevel
    education: Education
    encouragedToApply: EncouragedToApply
    secondaryLocation: Location
    companyFccKey: str
    salary: str

    def __init__(self):
        super().__init__()
        self.dateRange = None
        self.remoteOrTemporarilyRemote = None
        self.jobType = None
        self.withinMiles = None
        self.postedBy = None
        self.experienceLevel = None
        self.education = None
        self.encouragedToApply = None
        self.secondaryLocation = None
        self.companyFccKey = None
        self.salary = None # "$150,000"
    