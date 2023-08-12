#!/usr/bin/env python3

import csv
from pathlib import Path
import itertools
from datetime import datetime
from logging import getLogger, Logger

from .filteringweight import BaseFilteringWeight
from ..jobinfo import *
from ..utility import isNullOrWhiteSpace, getTrimmedStringValueOrEmptyString, getSimpleModuleName
from ..constants import DEROGATORY_MARK_WEIGHT_HANDICAP


class JobProcessor:
    __stopListPath: str
    __filteringWeights: list[BaseFilteringWeight]
    __logAfterLines: int
    __logger: Logger

    def __init__(self, stopListPath: str = None, filteringWeights: list[BaseFilteringWeight] = None):
        self.__stopListPath = stopListPath
        self.__filteringWeights = filteringWeights
        self.__logAfterLines = 500
        self.__logger = getLogger(getSimpleModuleName(__name__))

    def __setDerogatoryMarksAndWeightsByStoplist(self, jobs: list[Job]) -> None:
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
                        if ((isNullOrWhiteSpace(t) or t.casefold() == job.title.casefold()) and 
                            (isNullOrWhiteSpace(c) or c.casefold() == job.company.casefold())):
                            # 'Stoplist entry found for job title = "A" and company name = "B" with reason: C'
                            stoplistObjectArray = [ ('job title', t), ('company name', c) ]
                            stoplistObjectString = ' and '.join(map(lambda elem: '%s = \'%s\'' % (elem[0], elem[1]), filter(lambda elem: elem[1], stoplistObjectArray)))
                            job.derogatoryMarks.append('Stoplist entry found for %s with reason: %s' % (stoplistObjectString, stoplistObject.get('reason')))
                            job.weight += DEROGATORY_MARK_WEIGHT_HANDICAP

                    if not lineCounter % self.__logAfterLines:
                        self.__logger.info('Processed %d items of stoplist...', lineCounter)
                    lineCounter += 1

            self.__logger.info('Finished processing jobs against stoplist at "%s".', self.__stopListPath)
        except csv.Error:
            self.__logger.exception('Error processing stoplist file at "%s".', self.__stopListPath)
        except OSError:
            self.__logger.exception('Error reading stoplist file at "%s".', self.__stopListPath)
        

    def processJobs(self, jobs: list[JobInfo]) -> list[Job]:
        groupedJobs = []
        
        if jobs:
            # group jobs by title and company
            lmbdGroup = lambda job: JobKey(job.title, job.company)
            for key, value in itertools.groupby(sorted(jobs, key=lmbdGroup), lmbdGroup):
                minDatePosted = datetime.now()
                locations = set()
                salaries = set()
                for job in value:
                    if job.datePosted < minDatePosted:
                        minDatePosted = job.datePosted
                    locations.add(JobLocation(job.location, job.jobLink))
                    if job.salary:
                        salaries.add(job.salary)
                groupedJobs.append(Job(key.title, key.company, minDatePosted, list(locations), list(salaries)))

            # process jobs against stoplist:
            self.__setDerogatoryMarksAndWeightsByStoplist(groupedJobs)

            # process jobs against regexes:
            if self.__filteringWeights:
                for groupedJob in groupedJobs:
                    for filteringWeight in self.__filteringWeights:
                        filteringWeight.assignWeightAndDerogatoryMarkToJob(groupedJob)

            groupedJobs.sort(key = lambda groupedJob: (groupedJob.weight, groupedJob.datePosted), reverse = True)

            self.__logger.info('Processed %d jobs and grouped them into %d groups', len(jobs), len(groupedJobs))

        return groupedJobs