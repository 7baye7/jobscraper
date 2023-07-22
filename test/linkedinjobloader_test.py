#!/usr/bin/env python3

import unittest
from unittest.mock import Mock
import os
import sys
from selenium.webdriver.common.by import By

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import src.linkedin as Linkedin
from src.constants import LINKEDIN_PAGE_SIZE, LINKEDIN_JOB_LOADING_LIMIT
from src.constants import LOGGER_NAME

class Test_LinkedinJobLoader(unittest.TestCase):

    def __generateJobElements(self, count: int) -> list[Mock]:
        results = []
        for i in range(0, count):
            jobElement = Mock()
            jobElement.tag_name = 'a'
            jobElement.get_attribute.return_value = 'http://example.com'

            timeElement = Mock()
            timeElement.get_attribute.return_value = '2020-02-02'
            jobElement.find_element.side_effect = lambda by, selector: timeElement if by == By.TAG_NAME and selector == 'time' else Mock()

            results.append(jobElement)
        return results


    def test_LinkedinJobLoaderLoadsJobsInPages(self):
        with self.assertLogs(LOGGER_NAME, level='INFO') as cm:
            # arrange
            params = Linkedin.SearchParams()
            params.query = 'A'
            params.location = 'B'

            driver = Mock()

            jobCount = LINKEDIN_PAGE_SIZE + 1
            limitElement = Mock()
            limitElement.text = str(jobCount)
            driver.find_element.return_value = limitElement
            driver.find_elements.side_effect = [ self.__generateJobElements(LINKEDIN_PAGE_SIZE), self.__generateJobElements(1) ]

            jobLoader = Linkedin.JobLoader(driver)

            # act
            result = jobLoader.loadJobs(params, shouldSleep = False)

            # assert
            self.assertEqual(len(result), jobCount)
            self.assertIn('INFO:%s:Will attempt to load 26 jobs' % LOGGER_NAME, cm.output)
            self.assertIn('INFO:%s:Loaded 25 out of 26 jobs' % LOGGER_NAME, cm.output)
            self.assertIn('INFO:%s:Loaded less jobs (1) than configured page size (25), looks like there are no more jobs, process finished' % LOGGER_NAME, cm.output)
            self.assertIn('INFO:%s:Loaded a total of 26 jobs' % LOGGER_NAME, cm.output)


    def test_LinkedinJobLoaderLoadsNotMoreThanLoadingLimit(self):
        with self.assertLogs(LOGGER_NAME, level='INFO') as cm:
            # arrange
            params = Linkedin.SearchParams()
            params.query = 'A'
            params.location = 'B'

            driver = Mock()

            jobCount = LINKEDIN_JOB_LOADING_LIMIT + LINKEDIN_PAGE_SIZE
            limitElement = Mock()
            limitElement.text = str(jobCount)
            driver.find_element.return_value = limitElement

            jobElements = []
            for i in range(0, jobCount, LINKEDIN_PAGE_SIZE):
                jobElements.append(self.__generateJobElements(LINKEDIN_PAGE_SIZE))
            driver.find_elements.side_effect = jobElements

            jobLoader = Linkedin.JobLoader(driver)

            # act
            result = jobLoader.loadJobs(params, shouldSleep = False)

            # assert
            self.assertEqual(len(result), LINKEDIN_JOB_LOADING_LIMIT)
            self.assertIn('INFO:%s:Loaded equal to or more jobs (500) than discovered limit (500), won\'t be loading more, process finished' % LOGGER_NAME, cm.output)


    def test_LinkedinJobLoaderLoadsEmptyListOnException(self):
        with self.assertLogs(LOGGER_NAME, level='ERROR') as cm:
            # arrange
            params = Linkedin.SearchParams()
            params.query = 'A'
            params.location = 'B'

            driver = Mock()
            driver.get.side_effect = Exception('Fubar!')

            jobLoader = Linkedin.JobLoader(driver)

            # act
            result = jobLoader.loadJobs(params, shouldSleep = False)

            # assert
            self.assertEqual(len(result), 0)
            self.assertEqual(len(cm.output), 1)
            self.assertIn('ERROR:%s:Exception on loading jobs' % LOGGER_NAME, cm.output[0])
            self.assertIn('Fubar!', cm.output[0])