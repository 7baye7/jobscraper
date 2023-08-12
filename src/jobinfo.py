#!/usr/bin/env python3

from functools import total_ordering
from datetime import datetime

@total_ordering
class JobKey:
    title: str
    company: str

    def __init__(self, title: str, company: str):
        self.title = title
        self.company = company

    def __is_valid_operand(self, other):
        return (hasattr(other, 'title') and hasattr(other, 'company'))
    
    def __eq__(self, other):
        if not self.__is_valid_operand(other):
            return NotImplemented
        return ((self.title.casefold(), self.company.casefold()) == (other.title.casefold(), other.company.casefold()))

    def __lt__(self, other):
        if not self.__is_valid_operand(other):
            return NotImplemented
        return ((self.title.casefold(), self.company.casefold()) < (other.title.casefold(), other.company.casefold()))
    
    def __hash__(self):
        return hash((self.title, self.company))
    
    def __repr__(self):
        return str(self.__dict__)

class JobInfo(JobKey):
    jobLink: str
    location: str
    salary: str
    datePosted: datetime

    def __init__(self, title: str, company: str, jobLink: str, location: str, salary: str, datePosted: datetime):
        super().__init__(title, company)
        self.jobLink = jobLink
        self.location = location
        self.salary = salary
        self.datePosted = datePosted

    def __repr__(self):
        return str(self.__dict__)

class JobLocation:
    link: str
    name: str

    def __init__(self, name: str, link: str):
        self.link = link
        self.name = name

    def __is_valid_operand(self, other):
        return (hasattr(other, 'link') and hasattr(other, 'name'))
    
    def __eq__(self, other):
        if not self.__is_valid_operand(other):
            return NotImplemented
        return ((self.link.casefold(), self.name.casefold()) == (other.link.casefold(), other.name.casefold()))
    
    def __hash__(self):
        return hash((self.link, self.name))
    
    def __repr__(self):
        return str(self.__dict__)

class Job(JobKey):
    locations: list[JobLocation]
    salaries: list[str]
    datePosted: datetime
    weight: int
    derogatoryMarks: list[str]

    def __init__(self, title: str, company: str, datePosted: datetime, locations: list[JobLocation], salaries: list[str]):
        super().__init__(title, company)
        self.datePosted = datePosted
        self.locations = locations
        self.salaries = salaries
        self.weight = 0
        self.derogatoryMarks = []

    def __repr__(self):
        return str(self.__dict__)