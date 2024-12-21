#!/usr/bin/env python3

from .base import basesearchparams, basejobloader
from .indeed import JobLoader as IndeedJobLoader, SearchParams as IndeedSearchParams
from .linkedin import JobLoader as LinkedinJobLoader, SearchParams as LinkedinSearchParams
from selenium.webdriver.chrome.webdriver import WebDriver
from multiprocessing.managers import AcquirerProxy

class JobLoaderFactory:
    def createJobLoader(self, searchParams: basesearchparams.BaseSearchParams,
                        driver: WebDriver, lock: AcquirerProxy, tabNumber: int) -> basejobloader.BaseJobLoader:
        if isinstance(searchParams, IndeedSearchParams):
            return IndeedJobLoader(driver, lock, tabNumber = tabNumber)
        elif isinstance(searchParams, LinkedinSearchParams):
            return LinkedinJobLoader(driver, lock, tabNumber = tabNumber)
        else:
            raise TypeError("Unknown search parameters type: '%s'" % type(searchParams).__name__)