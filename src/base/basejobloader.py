import abc
import time
from logging import getLogger, Logger
from selenium.webdriver.chrome.webdriver import WebDriver
from random import randrange
from multiprocessing import Lock

from ..constants import MIN_SECONDS_TO_SLEEP, MAX_SECONDS_TO_SLEEP
from ..jobinfo import JobInfo
from .basesearchparams import BaseSearchParams
from ..utility import getSimpleModuleName

class BaseJobLoader(abc.ABC):
    _driver: WebDriver
    _tabNumber: int
    _lock: Lock
    _logger: Logger

    def __init__(self, driver: WebDriver, lock: Lock, tabNumber: int, loggerName: str):
        self._driver = driver
        self._tabNumber = tabNumber
        self._lock = lock
        self._logger = getLogger(getSimpleModuleName(loggerName))

    def _switchToProperTab(self) -> None:
        tabHandle = self._driver.window_handles[self._tabNumber]
        self._driver.switch_to.window(tabHandle)

    def loadJobs(self, searchParams: BaseSearchParams, shouldSleep: bool = True) -> list[JobInfo]:
        try:
            return self._loadJobsInner(searchParams, shouldSleep)
        except Exception:
            self._logger.exception('Exception on loading jobs')
            return []

    @abc.abstractmethod        
    def _loadJobsInner(self, searchParams: BaseSearchParams, shouldSleep: bool) -> list[JobInfo]:
        pass
    
    def _sleep(self, shouldSleep: bool) -> None:
        if shouldSleep:
            secondsToSleep = randrange(MIN_SECONDS_TO_SLEEP, MAX_SECONDS_TO_SLEEP)
            self._logger.info('Sleeping for %d seconds...', secondsToSleep)
            time.sleep(secondsToSleep)

    def _threadSafeGet(self, url: str | None) -> None:
        with self._lock:
                self._switchToProperTab()
                self._driver.get(url)

    def _threadSafeExecuteScript(self, script: any) -> any:
        with self._lock:
                self._switchToProperTab()
                return self._driver.execute_script(script)