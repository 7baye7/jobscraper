#!/usr/bin/env python3

import unittest
from unittest.mock import Mock
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import src.indeed as Indeed
from src.constants import INDEED_JOB_LOADING_LIMIT
from src.constants import LOGGER_NAME

class Test_IndeedJobLoader(unittest.TestCase):

    def __generateJobElements(self, count: int) -> list[Mock]:
        results = []
        for i in range(0, count):
            jobElement = Mock()
            jobElement.get.side_effect = Test_IndeedJobLoader.lmbd
            results.append(jobElement)
        return results


    def test_IndeedJobLoaderLoadsJobsInPages(self):
        with self.assertLogs(LOGGER_NAME, level='INFO') as cm:
            # arrange
            params = Indeed.SearchParams()
            params.query = 'A'
            params.location = 'B'

            driver = Mock()
            jobCount = 25
            driver.execute_script.side_effect = [ jobCount, self.__generateJobElements(15), self.__generateJobElements(10) ]
            driver.find_element.side_effect = [ Mock(), None ]

            jobLoader = Indeed.JobLoader(driver)

            # act
            result = jobLoader.loadJobs(params, shouldSleep = False)

            # assert
            self.assertEqual(len(result), jobCount)
            self.assertIn('INFO:%s:Will attempt to load 25 jobs' % LOGGER_NAME, cm.output)
            self.assertIn('INFO:%s:Loaded 15 out of 25 jobs' % LOGGER_NAME, cm.output)
            self.assertIn('INFO:%s:Loaded 25 out of 25 jobs' % LOGGER_NAME, cm.output)
            self.assertIn('INFO:%s:Next page does not exist, there are no more jobs, process finished' % LOGGER_NAME, cm.output)
            self.assertIn('INFO:%s:Loaded a total of 25 jobs' % LOGGER_NAME, cm.output)


    def test_IndeedJobLoaderDefaultsToJobLoadingLimitWhenNoLimitFound(self):
        with self.assertLogs(LOGGER_NAME, level='INFO') as cm:
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

            jobLoader = Indeed.JobLoader(driver)

            # act
            result = jobLoader.loadJobs(params, shouldSleep = False)

            # assert
            self.assertEqual(len(result), INDEED_JOB_LOADING_LIMIT)
            self.assertIn('INFO:%s:Will attempt to load 500 jobs' % LOGGER_NAME, cm.output)
            self.assertIn('INFO:%s:Loaded equal to or more jobs (510) than discovered limit (500), won\'t be loading more, process finished' % LOGGER_NAME, cm.output)
            self.assertIn('INFO:%s:Loaded a total of 500 jobs' % LOGGER_NAME, cm.output)


    def test_IndeedJobLoaderLoadsNotMoreThanLoadingLimit(self):
        with self.assertLogs(LOGGER_NAME, level='INFO') as cm:
            # arrange
            params = Indeed.SearchParams()
            params.query = 'A'
            params.location = 'B'

            driver = Mock()
            jobCount = 25
            driver.execute_script.side_effect = [ jobCount, self.__generateJobElements(15), self.__generateJobElements(10) ]
            driver.find_element.side_effect = [ Mock(), None ]

            jobLoader = Indeed.JobLoader(driver)

            # act
            result = jobLoader.loadJobs(params, shouldSleep = False)

            # assert
            self.assertEqual(len(result), jobCount)
            self.assertIn('INFO:%s:Will attempt to load 25 jobs' % LOGGER_NAME, cm.output)
            self.assertIn('INFO:%s:Loaded 15 out of 25 jobs' % LOGGER_NAME, cm.output)
            self.assertIn('INFO:%s:Loaded 25 out of 25 jobs' % LOGGER_NAME, cm.output)
            self.assertIn('INFO:%s:Next page does not exist, there are no more jobs, process finished' % LOGGER_NAME, cm.output)
            self.assertIn('INFO:%s:Loaded a total of 25 jobs' % LOGGER_NAME, cm.output)

    def test_IndeedJobLoaderLoadsEmptyListOnException(self):
        with self.assertLogs(LOGGER_NAME, level='ERROR') as cm:
            # arrange
            params = Indeed.SearchParams()
            params.query = 'A'
            params.location = 'B'

            driver = Mock()
            driver.get.side_effect = Exception('Fubar!')

            jobLoader = Indeed.JobLoader(driver)

            # act
            result = jobLoader.loadJobs(params, shouldSleep = False)

            # assert
            self.assertEqual(len(result), 0)
            self.assertEqual(len(cm.output), 1)
            self.assertIn('ERROR:%s:Exception on loading jobs' % LOGGER_NAME, cm.output[0])
            self.assertIn('Fubar!', cm.output[0])

    @staticmethod
    def lmbd(key):
        if key == 'link':
            return '/fubar?foo=bar'
        elif key == 'pubDate':
            return 123456
        else:
            return Mock()