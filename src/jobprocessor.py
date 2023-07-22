#!/usr/bin/env python3

import csv
import re
from pathlib import Path
from logging import Logger, getLogger
import itertools
from datetime import datetime

from .jobinfo import *
from .utility import isNullOrWhiteSpace, getTrimmedStringValueOrEmptyString
from .constants import DEROGATORY_MARK_WEIGHT_HANDICAP, DESIRABLE_WORD_WEIGHT_BONUS, LOGGER_NAME


class JobProcessor:
    __stopListPath: str
    __badTitleRegexString: str
    __badCompanyRegexString: str
    __goodTitleRegexString: str
    __goodCompanyRegexString: str
    __logger: Logger
    __logAfterLines: int

    def __init__(self, stopListPath: str = None,
                 badTitleRegexString: str = None, badCompanyRegexString: str = None, 
                 goodTitleRegexString: str = None, goodCompanyRegexString: str = None):
        self.__stopListPath = stopListPath
        self.__badTitleRegexString = badTitleRegexString
        self.__badCompanyRegexString = badCompanyRegexString
        self.__goodTitleRegexString = goodTitleRegexString
        self.__goodCompanyRegexString = goodCompanyRegexString
        self.__logger = getLogger(LOGGER_NAME)
        self.__logAfterLines = 500

    def __setDerogatoryMarksForJobsInStoplist(self, jobs: list[Job]) -> None:
        if not self.__stopListPath or not Path(self.__stopListPath).is_file():
            self.__logger.warning('Expected to find stoplist at "%s" but it was not there. Jobs will not be processed against stoplist.', self.__stopListPath)
            return

        try:
            self.__logger.info('Processing jobs against stoplist at "%s"...', self.__stopListPath)
            with open(self.__stopListPath, newline='', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                lineCounter = 1
                for stoplistObject in reader:
                    t = getTrimmedStringValueOrEmptyString(stoplistObject.get('title'))
                    c = getTrimmedStringValueOrEmptyString(stoplistObject.get('company'))
                    if isNullOrWhiteSpace(t) and isNullOrWhiteSpace(c):
                        self.__logger.warning('Encountered stoplist entry where both job title and company name are blank, skipping it.')
                        continue

                    for job in jobs:
                        if ((isNullOrWhiteSpace(t) or t == job.title) and (isNullOrWhiteSpace(c) or c == job.company)):
                            # 'Stoplist entry found for job title = "A" and company name = "B" with reason: C'
                            stoplistObjectArray = [ ('job title', t), ('company name', c) ]
                            stoplistObjectString = ' and '.join(map(lambda elem: '%s = \'%s\'' % (elem[0], elem[1]), filter(lambda elem: elem[1], stoplistObjectArray)))
                            job.derogatoryMarks.append('Stoplist entry found for %s with reason: %s' % (stoplistObjectString, stoplistObject.get('reason')))

                    if not lineCounter % self.__logAfterLines:
                        self.__logger.info('Processed %d items of stoplist...', lineCounter)
                    lineCounter += 1

            self.__logger.info('Finished processing jobs against stoplist at "%s".', self.__stopListPath)
        except csv.Error:
            self.__logger.exception('Error processing stoplist file at "%s".', self.__stopListPath)
        except OSError:
            self.__logger.exception('Error reading stoplist file at "%s".', self.__stopListPath)

    def __setDerogatoryMarkForUndesirableWords(self, job: Job, propertyName: str, regexPattern: str, derogatoryMarkFormatter: str) -> None:
        if isNullOrWhiteSpace(regexPattern):
            return
        
        propertyValue = getattr(job, propertyName)
        match = re.search(regexPattern, propertyValue, re.IGNORECASE)
        if match:
            job.derogatoryMarks.append(derogatoryMarkFormatter % match.group())

    def __getDesirableWordsBonus(self, job: Job, propertyName: str, regexPattern: str) -> int:
        if isNullOrWhiteSpace(regexPattern):
            return 0
        
        propertyValue = getattr(job, propertyName)
        matches = re.findall(regexPattern, propertyValue, re.IGNORECASE)
        return len(matches) * DESIRABLE_WORD_WEIGHT_BONUS
    
    def __getSalaryBonus(self, job: Job) -> int:
        if job.salaries:
            return 1
        else:
            return 0

    def processJobs(self, jobs: list[JobInfo]) -> list[Job]:
        groupedJobs = []
        
        if jobs:
            # group jobs by title and company
            lmbdGroup = lambda job: JobKey(job.title, job.company)
            for key, value in itertools.groupby(sorted(jobs, key=lmbdGroup), lmbdGroup):
                minDatePosted = datetime.now()
                locations = []
                salaries = []
                for job in value:
                    if job.datePosted < minDatePosted:
                        minDatePosted = job.datePosted
                    locations.append(JobLocation(job.location, job.jobLink))
                    if job.salary:
                        salaries.append(job.salary)
                groupedJobs.append(Job(key.title, key.company, minDatePosted, locations, salaries))

            # process jobs:
            self.__setDerogatoryMarksForJobsInStoplist(groupedJobs)

            for groupedJob in groupedJobs:
                self.__setDerogatoryMarkForUndesirableWords(groupedJob, 'title', self.__badTitleRegexString, 'Undesirable word in job title: \'%s\'')
                self.__setDerogatoryMarkForUndesirableWords(groupedJob, 'company', self.__badCompanyRegexString, 'Undesirable word in company name: \'%s\'')
                groupedJob.weight += (len(groupedJob.derogatoryMarks) * DEROGATORY_MARK_WEIGHT_HANDICAP + 
                                    self.__getDesirableWordsBonus(groupedJob, 'title', self.__goodTitleRegexString) + 
                                    self.__getDesirableWordsBonus(groupedJob, 'company', self.__goodCompanyRegexString) + 
                                    self.__getSalaryBonus(groupedJob))

            groupedJobs.sort(key = lambda groupedJob: (groupedJob.weight, groupedJob.datePosted), reverse = True)

            self.__logger.info('Processed %d jobs and grouped them into %d groups', len(jobs), len(groupedJobs))

        return groupedJobs