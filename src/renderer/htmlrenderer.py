#!/usr/bin/env python3

import datetime
from xml.etree.ElementTree import Element, SubElement, tostring
from logging import getLogger, Logger
from enum import Enum

from ..constants import GLASSDOOR_HOST, GLASSDOOR_SEARCH_PAGE, GLASSDOOR_SEARCH_PARAM
from ..utility import buildUrl, getTrimmedStringValueOrEmptyString, getSimpleModuleName
from ..jobinfo import Job

class HtmlRenderer:
    __logger: Logger
    __cssStyle: str = ('html {font-family:system-ui,"Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;font-weight: 400;}' + 
                       'h1,h2,h3,h4,h5,h6 {font-weight: 500;}summary {display: list-item;cursor: pointer;}ul {margin-top: 0;margin-bottom: 0.3em;}' +
                       'table {border-collapse: collapse;border-spacing: 0;width: 100%;border: 1px solid #ddd;margin-top: 1em;}' +
                       'th, td {text-align: left;padding: 0.5em;}tr:nth-child(odd) {background-color: #f2f2f2;}.limited-width {width: 25%;}')
    
    def __init__(self):
        self.__logger = getLogger(getSimpleModuleName(__name__))

    def __getSalary(self, groupedJob: Job) -> str:
        if not groupedJob.salaries:
            return ''
        elif len(groupedJob.salaries) == 1:
            return groupedJob.salaries[0]
        else:
            return 'Varied: %s' % ', '.join(groupedJob.salaries)


    def __setLinks(self, tLinks: SubElement, groupedJob: Job):
        count = len(groupedJob.locations)
        for i, location in enumerate(groupedJob.locations):
            a = SubElement(tLinks, 'a', { 'href': location.link })
            a.text = location.name
            if i != count - 1:
                a.tail = ', '

    def __setDerogatoryMarks(self, tDerogatoryMarks: SubElement, groupedJob: Job):
        for dm in groupedJob.derogatoryMarks:
            SubElement(tDerogatoryMarks, 'div').text = dm

    def __setTitle(self, date: datetime, jobsWithoutDerogatoryMarksCount: int, totalJobsCount: int, *args: Element) -> None:
        dateStr = ' for %s' % date.strftime("%m/%d/%Y %H:%M:%S") if date else ''
        for elem in args:
            elem.text = ('Job Report%s, %d out of %d jobs without derogatory marks' % 
                         (dateStr, jobsWithoutDerogatoryMarksCount, totalJobsCount))


    def __setSearchParams(self, ul: SubElement, p: any) -> None:
        for key, value in p.__dict__.items():
            if value:
                if type(value) is str:
                    SubElement(ul, 'li').text = '%s: %s' % (key, getTrimmedStringValueOrEmptyString(value))
                elif isinstance(value, Enum):
                    SubElement(ul, 'li').text = '%s: %s' % (key, value.name)
                elif hasattr(value, '__class__'):
                    li = SubElement(ul, 'li')
                    li.text = key
                    innerUl = SubElement(li, 'ul')
                    self.__setSearchParams(innerUl, value)
                else:
                    SubElement(ul, 'li').text = '%s: %s' % (key, str(value))

    def render(self, groupedJobs: list[Job], **kwargs) -> str:
        root = Element('html')
        head = SubElement(root, 'head')
        title = SubElement(head, 'title')
        SubElement(head, 'style').text = self.__cssStyle
        body = SubElement(root, 'body')
        h1 = SubElement(body, 'h1')

        for name, paramObject in kwargs.pop('searchParams', {}).items():
            details = SubElement(body, 'details')
            summary = SubElement(details, 'summary')
            summary.text = name
            self.__setSearchParams(SubElement(details, 'ul'), paramObject)

        table = SubElement(body, 'table')
        tHeader = SubElement(table, 'tr')
        SubElement(tHeader, 'th').text = '#'
        SubElement(tHeader, 'th').text = 'Job Name'
        SubElement(tHeader, 'th').text = 'Company'
        SubElement(tHeader, 'th').text = 'Salary'
        SubElement(tHeader, 'th', { 'class': 'limited-width' }).text = 'Locations'
        SubElement(tHeader, 'th').text = 'Date Posted'
        SubElement(tHeader, 'th', { 'class': 'limited-width' }).text = 'Derogatory Marks'

        jobsWithoutDerogatoryMarksCounter = 0
        if groupedJobs:
            for i, groupedJob in enumerate(groupedJobs):
                tRow = SubElement(table, 'tr')
                SubElement(tRow, 'td').text = str(i + 1)
                SubElement(tRow, 'td').text = groupedJob.title
                tCompany = SubElement(tRow, 'td')
                a = SubElement(tCompany, 'a', { 'href': buildUrl(GLASSDOOR_HOST, GLASSDOOR_SEARCH_PAGE, { GLASSDOOR_SEARCH_PARAM: groupedJob.company }) })
                a.text = groupedJob.company
                SubElement(tRow, 'td').text = self.__getSalary(groupedJob)
                tLinks = SubElement(tRow, 'td')
                self.__setLinks(tLinks, groupedJob)
                SubElement(tRow, 'td').text = groupedJob.datePosted.strftime('%Y-%m-%d')
                tDerogatoryMarks = SubElement(tRow, 'td')
                self.__setDerogatoryMarks(tDerogatoryMarks, groupedJob)
                jobsWithoutDerogatoryMarksCounter += 1 if not groupedJob.derogatoryMarks else 0
        else:
            SubElement(SubElement(table, 'tr'), 'td', { 'colspan': str(len(tHeader.findall('th'))) }).text = 'No results'

        self.__setTitle(kwargs.pop('date', None), jobsWithoutDerogatoryMarksCounter, len(groupedJobs), title, h1)

        self.__logger.info('Rendered %d jobs as html', len(groupedJobs))
        return tostring(root, encoding='unicode')