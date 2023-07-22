import abc
import time
from logging import Logger, getLogger
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from random import randrange

from ..constants import LOGGER_NAME, MIN_SECONDS_TO_SLEEP, MAX_SECONDS_TO_SLEEP
from ..jobinfo import JobInfo
from .basesearchparams import BaseSearchParams

class BaseJobLoader(abc.ABC):
    _driver: WebDriver
    _logger: Logger
    def __init__(self, driver: WebDriver):
        self._driver = driver
        self._logger = getLogger(LOGGER_NAME)

    def loadJobs(self, searchParams: BaseSearchParams, shouldSleep: bool = True) -> list[JobInfo]:
        try:
            return self._loadJobsInner(searchParams, shouldSleep)
        except Exception:
            self._logger.exception('Exception on loading jobs')
            return []

    @abc.abstractmethod        
    def _loadJobsInner(self, searchParams: BaseSearchParams, shouldSleep: bool) -> list[JobInfo]:
        pass

    def _findElementWithoutException(self, by: By, selector: str):
        try:
            return self._driver.find_element(by, selector)
        except NoSuchElementException:
            return None
    
    def _sleep(self, shouldSleep: bool) -> None:
        if shouldSleep:
            secondsToSleep = randrange(MIN_SECONDS_TO_SLEEP, MAX_SECONDS_TO_SLEEP)
            self._logger.info('Sleeping for %d seconds...', secondsToSleep)
            time.sleep(secondsToSleep)