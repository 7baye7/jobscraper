#!/usr/bin/env python3

import abc
import re
import locale

from ..jobinfo import Job
from ..utility import isNullOrWhiteSpace

class BaseFilteringWeight(abc.ABC):
    fieldNameToTest: str
    weight: int

    def __init__(self, fieldNameToTest: str, weight: int):
        self.fieldNameToTest = fieldNameToTest
        self.weight = weight


    @abc.abstractmethod        
    def assignWeightAndDerogatoryMarkToJob(self, job: Job) -> None:
        pass



class RegexFilteringWeight(BaseFilteringWeight):
    regex: str

    def __init__(self, fieldNameToTest: str, weight: int, regex: str):
        super().__init__(fieldNameToTest, weight)
        self.regex = regex


    def assignWeightAndDerogatoryMarkToJob(self, job: Job) -> None:
        if isNullOrWhiteSpace(self.regex):
            return
        
        propertyValue = getattr(job, self.fieldNameToTest)
        if self.weight < 0:
            match = re.search(self.regex, propertyValue, re.IGNORECASE)
            if match:
                job.derogatoryMarks.append('Undesirable word in %s: \'%s\'' % ( self.fieldNameToTest, match.group() ) )
                job.weight += self.weight
        else:
            matches = re.findall(self.regex, propertyValue, re.IGNORECASE)
            job.weight += len(matches) * self.weight


class SalaryFilteringWeight(BaseFilteringWeight):
    __moneyRegex: str = r'[\d,\.]+'
    salaryMustBeNoLessThan: float

    def __init__(self, weight: int, salaryMustBeNoLessThan: float):
        super().__init__('salaries', weight)
        self.salaryMustBeNoLessThan = salaryMustBeNoLessThan


    def assignWeightAndDerogatoryMarkToJob(self, job: Job) -> None:
        salaryList = getattr(job, self.fieldNameToTest)
        if salaryList:
            for salaryRange in salaryList:
                salaryLimitStrings = re.findall(self.__moneyRegex, salaryRange, re.IGNORECASE)
                if salaryLimitStrings:
                    higherSalaryLimitString = salaryLimitStrings[-1] # salary range is usually "$50,000.00 - $65,000.00 a year", we're getting "65,000.00"
                    try:
                        locale.setlocale(locale.LC_NUMERIC, 'en_US.UTF-8')
                        higherSalaryLimit = locale.atof(higherSalaryLimitString)
                        if higherSalaryLimit >= self.salaryMustBeNoLessThan:
                            job.weight += self.weight
                            break
                    except (ValueError, locale.Error):
                        pass
