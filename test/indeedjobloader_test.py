#!/usr/bin/env python3

import unittest
from unittest.mock import Mock
import multiprocessing.dummy as multimock
import os
import sys
from selenium.common.exceptions import NoSuchElementException

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import src.indeed as Indeed
from src.constants import INDEED_JOB_LOADING_LIMIT

class Test_IndeedJobLoader(unittest.TestCase):

    def __generateJobElements(self, count: int) -> list[Mock]:
        results = []
        for i in range(0, count):
            jobElement = Mock()
            jobElement.get.side_effect = Test_IndeedJobLoader.lmbd
            results.append(jobElement)
        return results


    def test_IndeedJobLoaderLoadsJobsInPages(self):
        with self.assertLogs('indeedjobloader', level='INFO') as cm:
            # arrange
            params = Indeed.SearchParams()
            params.query = 'A'
            params.location = 'B'

            driver = Mock()
            jobCount = 25
            driver.execute_script.side_effect = [ jobCount, self.__generateJobElements(15), self.__generateJobElements(10) ]
            driver.find_element.side_effect = [ Mock(), NoSuchElementException() ]
            driver.window_handles = [0]

            lock = multimock.Lock()

            jobLoader = Indeed.JobLoader(driver, lock, 0)

            # act
            result = jobLoader.loadJobs(params, shouldSleep = False)

            # assert
            self.assertEqual(len(result), jobCount)
            self.assertIn('INFO:indeedjobloader:Will attempt to load 25 jobs', cm.output)
            self.assertIn('INFO:indeedjobloader:Loaded 15 out of 25 jobs', cm.output)
            self.assertIn('INFO:indeedjobloader:Loaded 25 out of 25 jobs', cm.output)
            self.assertIn('INFO:indeedjobloader:Next page does not exist, there are no more jobs, process finished', cm.output)
            self.assertIn('INFO:indeedjobloader:Loaded a total of 25 jobs', cm.output)


    def test_IndeedJobLoaderDefaultsToJobLoadingLimitWhenNoLimitFound(self):
        with self.assertLogs('indeedjobloader', level='INFO') as cm:
            # arrange
            params = Indeed.SearchParams()
            params.query = 'A'
            params.location = 'B'

            driver = Mock()
            pageSize = 15
            jobCount = INDEED_JOB_LOADING_LIMIT + pageSize

            jobElementBatches = []
            nextPageMocks = []
            for i in range(0, jobCount, pageSize):
                jobElementBatches.append(self.__generateJobElements(pageSize))
                nextPageMocks.append( Mock() )

            driver.execute_script.side_effect = [ jobCount ] + jobElementBatches
            driver.find_elements.side_effect = nextPageMocks
            driver.window_handles = [0]

            lock = multimock.Lock()

            jobLoader = Indeed.JobLoader(driver, lock, 0)

            # act
            result = jobLoader.loadJobs(params, shouldSleep = False)

            # assert
            self.assertEqual(len(result), INDEED_JOB_LOADING_LIMIT)
            self.assertIn('INFO:indeedjobloader:Will attempt to load 500 jobs', cm.output)
            self.assertIn('INFO:indeedjobloader:Loaded equal to or more jobs (510) than discovered limit (500), won\'t be loading more, process finished', cm.output)
            self.assertIn('INFO:indeedjobloader:Loaded a total of 500 jobs', cm.output)


    def test_IndeedJobLoaderLoadsNotMoreThanLoadingLimit(self):
        with self.assertLogs('indeedjobloader', level='INFO') as cm:
            # arrange
            params = Indeed.SearchParams()
            params.query = 'A'
            params.location = 'B'

            driver = Mock()
            jobCount = 25
            driver.execute_script.side_effect = [ jobCount, self.__generateJobElements(15), self.__generateJobElements(15) ]
            driver.find_element.side_effect = [ Mock(), NoSuchElementException() ]
            driver.window_handles = [0]

            lock = multimock.Lock()

            jobLoader = Indeed.JobLoader(driver, lock, 0)

            # act
            result = jobLoader.loadJobs(params, shouldSleep = False)

            # assert
            self.assertEqual(len(result), jobCount)
            self.assertIn('INFO:indeedjobloader:Will attempt to load 25 jobs', cm.output)
            self.assertIn('INFO:indeedjobloader:Loaded 15 out of 25 jobs', cm.output)
            self.assertIn('INFO:indeedjobloader:Loaded 30 out of 25 jobs', cm.output)
            self.assertIn('INFO:indeedjobloader:Next page does not exist, there are no more jobs, process finished', cm.output)
            self.assertIn('INFO:indeedjobloader:Loaded a total of 25 jobs', cm.output)


    def test_IndeedJobLoaderLoadsNothingIfZeroJobsIsFound(self):
        with self.assertLogs('indeedjobloader', level='INFO') as cm:
            # arrange
            params = Indeed.SearchParams()
            params.query = 'A'
            params.location = 'B'

            driver = Mock()
            jobCount = 0
            driver.execute_script.side_effect = [ jobCount ]
            driver.window_handles = [0]

            lock = multimock.Lock()

            jobLoader = Indeed.JobLoader(driver, lock, 0)

            # act
            result = jobLoader.loadJobs(params, shouldSleep = False)

            # assert
            self.assertEqual(len(result), jobCount)
            self.assertIn('WARNING:indeedjobloader:No jobs found with given search criteria', cm.output)
            self.assertIn('INFO:indeedjobloader:Loaded a total of 0 jobs', cm.output)


    def test_IndeedJobLoaderLoadsNothingIfJobCounterIsNotFound(self):
        with self.assertLogs('indeedjobloader', level='INFO') as cm:
            # arrange
            params = Indeed.SearchParams()
            params.query = 'A'
            params.location = 'B'

            driver = Mock()
            jobCount = 0
            driver.execute_script.side_effect = [ None ]
            driver.window_handles = [0]

            lock = multimock.Lock()

            jobLoader = Indeed.JobLoader(driver, lock, 0)

            # act
            result = jobLoader.loadJobs(params, shouldSleep = False)

            # assert
            self.assertEqual(len(result), jobCount)
            self.assertIn('WARNING:indeedjobloader:Could not determine how many jobs to load, will exit without loading jobs', cm.output)
            self.assertIn('INFO:indeedjobloader:Loaded a total of 0 jobs', cm.output)


    def test_IndeedJobLoaderLoadsEmptyListOnException(self):
        with self.assertLogs('indeedjobloader', level='ERROR') as cm:
            # arrange
            params = Indeed.SearchParams()
            params.query = 'A'
            params.location = 'B'

            driver = Mock()
            driver.get.side_effect = Exception('Fubar!')
            driver.window_handles = [0]

            lock = multimock.Lock()

            jobLoader = Indeed.JobLoader(driver, lock, 0)

            # act
            result = jobLoader.loadJobs(params, shouldSleep = False)

            # assert
            self.assertEqual(len(result), 0)
            self.assertEqual(len(cm.output), 1)
            self.assertIn('ERROR:indeedjobloader:Exception on loading jobs', cm.output[0])
            self.assertIn('Fubar!', cm.output[0])

    @staticmethod
    def lmbd(key):
        if key == 'link':
            return '/fubar?foo=bar'
        elif key == 'pubDate':
            return 123456
        else:
            return Mock()
        

if __name__ == '__main__':
    unittest.main()