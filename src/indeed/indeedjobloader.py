#!/usr/bin/env python3

from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from datetime import datetime
import re
from multiprocessing import Lock

from ..constants import INDEED_HOST, INDEED_JOB_LOADING_LIMIT
from ..base.basejobloader import BaseJobLoader
from ..jobinfo import JobInfo
from ..base.basesearchparams import BaseSearchParams
from .urlbuilder import UrlBuilder

class JobLoader(BaseJobLoader):
    def __init__(self, driver: WebDriver, lock: Lock, tabNumber: int):
        super().__init__(driver, lock, tabNumber, __name__)
        
    def __mapJsonJobToJobInfo(self, jsonJob: dict) -> JobInfo:
        return JobInfo(
                jsonJob.get('displayTitle'),
                jsonJob.get('company'),
                re.sub('/{2,}', '/', '/'.join([ INDEED_HOST, jsonJob.get('link') ])), # take care of slashes when joining url parts
                jsonJob.get('formattedLocation'),
                jsonJob.get('salarySnippet').get('text') if jsonJob.get('salarySnippet') else '',
                datetime.fromtimestamp(jsonJob.get('pubDate') / 1000.0)) # jsonJob['pubDate'] is in milliseconds


    def __threadSafeGetNextPageUrl(self) -> str | None:
        try:
            with self._lock:
                self._switchToProperTab()
                nextPageLinkElement = self._driver.find_element(By.CSS_SELECTOR, 'a[data-testid="pagination-page-next"]')
                return nextPageLinkElement.get_attribute('href')
        except NoSuchElementException:
            return None

    def _loadJobsInner(self, searchParams: BaseSearchParams, shouldSleep: bool = True) -> list[JobInfo]:
        results = []
        limit = 0
        url = UrlBuilder.buildUrl(searchParams)

        while True: # do-while imitation
            self._logger.info('Loading jobs from url = "%s"...', url)
            self._threadSafeGet(url)

            if not results: # nothing is loaded yet - get loading limit
                limit = self._threadSafeExecuteScript('return window._initialData ? window._initialData.uniqueJobsCount : null')
                if limit is None:
                    self._logger.warning('Could not determine how many jobs to load, will exit without loading jobs')
                    break
                else:
                    limit = min(limit, INDEED_JOB_LOADING_LIMIT)
                    if limit == 0:
                        self._logger.warning('No jobs found with given search criteria')
                        break
                    else:
                        self._logger.info('Will attempt to load %d jobs', limit)

            jsonJobs = self._threadSafeExecuteScript('try { return window.mosaic.providerData["mosaic-provider-jobcards"].metaData.mosaicProviderJobCardsModel.results } catch(e) { return null }')
            if not jsonJobs:
                self._logger.error('Could not load any jobs from url = "%s", its html was "%s"', url, self._driver.page_source)
            else:
                results.extend(map(lambda jsonJob: self.__mapJsonJobToJobInfo(jsonJob), jsonJobs))
                self._logger.info('Loaded %d out of %d jobs', len(results), limit)

            nextPageUrl = self.__threadSafeGetNextPageUrl()
            if not nextPageUrl:
                self._logger.info('Next page does not exist, there are no more jobs, process finished')
                break
            elif len(results) >= limit:
                self._logger.info('Loaded equal to or more jobs (%d) than discovered limit (%d), won\'t be loading more, process finished', len(results), limit)
                break
            else:
                url = nextPageUrl
                self._sleep(shouldSleep)

        finalResults = results[0:limit]
        self._logger.info('Loaded a total of %d jobs', len(finalResults))
        return finalResults