#!/usr/bin/env python3

from .enums import *

class SearchParams:
    query: str
    location: str
    dateRange: DateRange
    experienceLevel: ExperienceLevel
    jobType: JobType
    remoteFilter: Remote
    withinMiles: WithinMiles
    salary: Salary

    def __init__(self):
        self.query = None
        self.location = None
        self.dateRange = None
        self.experienceLevel = None
        self.jobType = None
        self.remoteFilter = None
        self.withinMiles = None
        self.salary = None