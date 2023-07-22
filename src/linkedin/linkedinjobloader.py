import time
from datetime import datetime
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
import re

from ..constants import LINKEDIN_JOB_LOADING_LIMIT, LINKEDIN_PAGE_SIZE
from ..base.basejobloader import BaseJobLoader
from ..utility import getTrimmedStringValueOrEmptyString
from ..jobinfo import JobInfo
from ..base.basesearchparams import BaseSearchParams
from .urlbuilder import UrlBuilder

class JobLoader(BaseJobLoader):
    def __init__(self, driver: WebDriver):
        super().__init__(driver)

    def __getElementTextOrEmptyString(self, element: WebElement) -> str:
        return getTrimmedStringValueOrEmptyString(element.text) if element else ''
    
    def __getElementAttributeOrEmptyString(self, element: WebElement, attributeName: str) -> str:
        return getTrimmedStringValueOrEmptyString(element.get_attribute(attributeName)) if element else ''
        
    def __findElementInElementWithoutException(self, element: WebElement, by: By, selector: str):
        try:
            return element.find_element(by, selector)
        except NoSuchElementException:
            return None

    def __parseJob(self, jobElement: WebElement) -> JobInfo:
        if jobElement.tag_name == 'a':
            # Every once in a while Linkedin would try and generate a weird job element that looks normal but its html is nothing like standard.
            # But we'll parse it nonetheless
            titleElement = self.__findElementInElementWithoutException(jobElement, By.CLASS_NAME, 'base-search-card__title')
            companyElement = self.__findElementInElementWithoutException(jobElement, By.CLASS_NAME, 'base-search-card__subtitle')
            joblinkElement = jobElement
        else:
            # Normal standard boring job element
            titleElement = self.__findElementInElementWithoutException(jobElement, By.CLASS_NAME, 'base-card__full-link')
            companyElement = self.__findElementInElementWithoutException(jobElement, By.CLASS_NAME, 'hidden-nested-link')
            joblinkElement = titleElement

        locationElement = self.__findElementInElementWithoutException(jobElement, By.CLASS_NAME, 'job-search-card__location')
        salaryElement = self.__findElementInElementWithoutException(jobElement, By.CLASS_NAME, 'job-search-card__salary-info')
        dateElement = self.__findElementInElementWithoutException(jobElement, By.TAG_NAME, 'time') # <time class="job-search-card__listdate--new" datetime="2023-06-19">

        postedDateString = self.__getElementAttributeOrEmptyString(dateElement, 'datetime')
        
        return JobInfo(self.__getElementTextOrEmptyString(titleElement),
            self.__getElementTextOrEmptyString(companyElement),
            re.sub(r'\?.+', '', (self.__getElementAttributeOrEmptyString(joblinkElement, 'href'))), # cut off useless url tracking parameters
            self.__getElementTextOrEmptyString(locationElement),
            self.__getElementTextOrEmptyString(salaryElement),
            datetime.now() if not postedDateString else datetime.strptime(postedDateString, '%Y-%m-%d')
        )
    
    def __getJobCountLimit(self, totalJobsFoundElement: WebElement) -> int:
        try:
            limit = min(int(totalJobsFoundElement.text), LINKEDIN_JOB_LOADING_LIMIT)
            self._logger.info('Will attempt to load %d jobs', limit)
            return limit
        except:
            self._logger.warning('Could not determine how many jobs to load, will attempt to load the configured maximum of %d jobs', LINKEDIN_JOB_LOADING_LIMIT)
            return LINKEDIN_JOB_LOADING_LIMIT

    def _loadJobsInner(self, searchParams: BaseSearchParams, shouldSleep: bool = True) -> list[JobInfo]:
        results = []
        startFrom = 0
        limit = 0
        url = UrlBuilder.buildUrl(searchParams)

        while True: # do-while imitation
            self._logger.info('Loading jobs from url = "%s"...', url)
            self._driver.get(url)

            if startFrom == 0:
                totalJobsFoundElement = self._findElementWithoutException(By.CLASS_NAME, 'results-context-header__job-count')
                limit = self.__getJobCountLimit(totalJobsFoundElement)

            jobElements = self._driver.find_elements(By.CLASS_NAME, 'base-search-card--link')
            for jobElement in jobElements:
                job = self.__parseJob(jobElement)
                results.append(job)

            self._logger.info('Loaded %d out of %d jobs', len(results), limit)

            if len(jobElements) < LINKEDIN_PAGE_SIZE:
                self._logger.info('Loaded less jobs (%d) than configured page size (%d), looks like there are no more jobs, process finished', 
                                  len(jobElements), LINKEDIN_PAGE_SIZE)
                break
            elif len(results) >= limit:
                self._logger.info('Loaded equal to or more jobs (%d) than discovered limit (%d), won\'t be loading more, process finished', len(results), limit)
                break
            else:
                startFrom += LINKEDIN_PAGE_SIZE
                url = UrlBuilder.buildUrl(searchParams, { 'start': startFrom, 'partial': True })
                self._sleep(shouldSleep)

        finalResults = results[0:limit]
        self._logger.info('Loaded a total of %d jobs', len(finalResults))
        return finalResults