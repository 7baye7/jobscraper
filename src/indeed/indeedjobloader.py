#!/usr/bin/env python3

from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.common.by import By
from datetime import datetime
import re

from ..constants import INDEED_HOST, INDEED_JOB_LOADING_LIMIT
from ..base.basejobloader import BaseJobLoader
from ..jobinfo import JobInfo
from ..base.basesearchparams import BaseSearchParams
from .urlbuilder import UrlBuilder

class JobLoader(BaseJobLoader):
    def __init__(self, driver: WebDriver):
        super().__init__(driver)
        
    def __mapJsonJobToJobInfo(self, jsonJob: dict) -> JobInfo:
        return JobInfo(
                jsonJob.get('displayTitle'),
                jsonJob.get('company'),
                re.sub('/{2,}', '/', '/'.join([ INDEED_HOST, jsonJob.get('link') ])), # take care of slashes when joining url parts
                jsonJob.get('formattedLocation'),
                jsonJob.get('salarySnippet').get('text') if jsonJob.get('salarySnippet') else '',
                datetime.fromtimestamp(jsonJob.get('pubDate') / 1000.0)) # jsonJob['pubDate'] is in milliseconds

    def _loadJobsInner(self, searchParams: BaseSearchParams, shouldSleep: bool = True) -> list[JobInfo]:
        results = []
        limit = 0
        url = UrlBuilder.buildUrl(searchParams)

        while True: # do-while imitation
            self._logger.info('Loading jobs from url = "%s"...', url)
            self._driver.get(url)

            if not results: # nothing is loaded yet - get loading limit
                limit = self._driver.execute_script('return window._initialData ? window._initialData.uniqueJobsCount : null')
                if not limit:
                    self._logger.warning('Could not determine how many jobs to load, will attempt to load the configured maximum of %d jobs', INDEED_JOB_LOADING_LIMIT)
                    limit = INDEED_JOB_LOADING_LIMIT
                else:
                    limit = min(limit, INDEED_JOB_LOADING_LIMIT)
                    self._logger.info('Will attempt to load %d jobs', limit)

            jsonJobs = self._driver.execute_script('try { return window.mosaic.providerData["mosaic-provider-jobcards"].metaData.mosaicProviderJobCardsModel.results } catch(e) { return null }')
            if not jsonJobs:
                self._logger.error('Could not load any jobs from url = "%s", its html was "%s"', url, self._driver.page_source)
            else:
                results.extend(map(lambda jsonJob: self.__mapJsonJobToJobInfo(jsonJob), jsonJobs))
                self._logger.info('Loaded %d out of %d jobs', len(results), limit)

            nextPageLink = self._findElementWithoutException(By.CSS_SELECTOR, 'a[data-testid="pagination-page-next"]')
            if not nextPageLink:
                self._logger.info('Next page does not exist, there are no more jobs, process finished')
                break
            elif len(results) >= limit:
                self._logger.info('Loaded equal to or more jobs (%d) than discovered limit (%d), won\'t be loading more, process finished', len(results), limit)
                break
            else:
                url = nextPageLink.get_attribute('href')
                self._sleep(shouldSleep)

        finalResults = results[0:limit]
        self._logger.info('Loaded a total of %d jobs', len(finalResults))
        return finalResults