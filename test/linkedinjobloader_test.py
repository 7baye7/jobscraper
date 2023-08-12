#!/usr/bin/env python3

import unittest
from unittest.mock import Mock
import multiprocessing.dummy as multimock
import os
import sys
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import src.linkedin as Linkedin
from src.constants import LINKEDIN_PAGE_SIZE, LINKEDIN_JOB_LOADING_LIMIT

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
        with self.assertLogs('linkedinjobloader', level='INFO') as cm:
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
            driver.window_handles = [0]

            lock = multimock.Lock()

            jobLoader = Linkedin.JobLoader(driver, lock, 0)

            # act
            result = jobLoader.loadJobs(params, shouldSleep = False)

            # assert
            self.assertEqual(len(result), jobCount)
            self.assertIn('INFO:linkedinjobloader:Will attempt to load 26 jobs', cm.output)
            self.assertIn('INFO:linkedinjobloader:Loaded 25 out of 26 jobs', cm.output)
            self.assertIn('INFO:linkedinjobloader:Loaded 26 out of 26 jobs', cm.output)
            self.assertIn('INFO:linkedinjobloader:Loaded equal to or more jobs (26) than discovered limit (26), won\'t be loading more, process finished', cm.output)
            self.assertIn('INFO:linkedinjobloader:Loaded a total of 26 jobs', cm.output)


    def test_LinkedinJobLoaderLoadsNotMoreThanLoadingLimit(self):
        with self.assertLogs('linkedinjobloader', level='INFO') as cm:
            # arrange
            params = Linkedin.SearchParams()
            params.query = 'A'
            params.location = 'B'

            driver = Mock()

            jobCount = LINKEDIN_JOB_LOADING_LIMIT + LINKEDIN_PAGE_SIZE
            limitElement = Mock()
            limitElement.text = str(jobCount)
            driver.find_element.return_value = limitElement
            driver.window_handles = [0]

            jobElements = []
            for i in range(0, jobCount, LINKEDIN_PAGE_SIZE):
                jobElements.append(self.__generateJobElements(LINKEDIN_PAGE_SIZE))
            driver.find_elements.side_effect = jobElements

            lock = multimock.Lock()

            jobLoader = Linkedin.JobLoader(driver, lock, 0)

            # act
            result = jobLoader.loadJobs(params, shouldSleep = False)

            # assert
            self.assertEqual(len(result), LINKEDIN_JOB_LOADING_LIMIT)
            self.assertIn('INFO:linkedinjobloader:Loaded equal to or more jobs (500) than discovered limit (500), won\'t be loading more, process finished', cm.output)


    def test_LinkedinJobLoaderLoadsNothingIfNoJobCounterElementIsFound(self):
        with self.assertLogs('linkedinjobloader', level='INFO') as cm:
            # arrange
            params = Linkedin.SearchParams()
            params.query = 'A'
            params.location = 'B'

            driver = Mock()

            jobCount = 0
            driver.find_element.side_effect = NoSuchElementException('No Job Counter!')
            driver.window_handles = [0]

            lock = multimock.Lock()

            jobLoader = Linkedin.JobLoader(driver, lock, 0)

            # act
            result = jobLoader.loadJobs(params, shouldSleep = False)

            # assert
            self.assertEqual(len(result), jobCount)
            self.assertIn('WARNING:linkedinjobloader:Could not determine how many jobs to load, will exit without loading jobs', cm.output)
            self.assertIn('INFO:linkedinjobloader:Loaded a total of 0 jobs', cm.output)


    # yes this is legit, linkedin can sometimes give you 24 results on a page instead of 25
    def test_LinkedinJobLoaderLoadsJobsIfOneOfThePagesIs1JobLessThanNormal(self):
        with self.assertLogs('linkedinjobloader', level='INFO') as cm:
            # arrange
            params = Linkedin.SearchParams()
            params.query = 'A'
            params.location = 'B'

            driver = Mock()

            jobCount = LINKEDIN_PAGE_SIZE * 3 + 1
            limitElement = Mock()
            limitElement.text = str(jobCount)
            driver.find_element.return_value = limitElement
            driver.find_elements.side_effect = [ 
                self.__generateJobElements(LINKEDIN_PAGE_SIZE), 
                self.__generateJobElements(LINKEDIN_PAGE_SIZE - 1), # tricky page
                self.__generateJobElements(LINKEDIN_PAGE_SIZE),
                 self.__generateJobElements(3) ] # another tricky page (linkedin sometimes gives you more results than expected)
            driver.window_handles = [0]

            lock = multimock.Lock()

            jobLoader = Linkedin.JobLoader(driver, lock, 0)

            # act
            result = jobLoader.loadJobs(params, shouldSleep = False)

            # assert
            self.assertEqual(len(result), jobCount)
            self.assertIn('INFO:linkedinjobloader:Will attempt to load 76 jobs', cm.output)
            self.assertIn('INFO:linkedinjobloader:Loaded 25 out of 76 jobs', cm.output)
            self.assertIn('INFO:linkedinjobloader:Loaded 49 out of 76 jobs', cm.output)
            self.assertIn('INFO:linkedinjobloader:Loaded 74 out of 76 jobs', cm.output)
            self.assertIn('INFO:linkedinjobloader:Loaded 77 out of 76 jobs', cm.output)
            self.assertIn('INFO:linkedinjobloader:Loaded equal to or more jobs (77) than discovered limit (76), won\'t be loading more, process finished', cm.output)
            self.assertIn('INFO:linkedinjobloader:Loaded a total of 76 jobs', cm.output)


    def test_LinkedinJobLoaderLoadsNothingIfJobCounterElementTextCannotBeParsed(self):
        with self.assertLogs('linkedinjobloader', level='INFO') as cm:
            # arrange
            params = Linkedin.SearchParams()
            params.query = 'A'
            params.location = 'B'

            driver = Mock()

            jobCount = 0
            limitElement = Mock()
            limitElement.text = 'Text that cannot be parsed as int'
            driver.find_element.return_value = limitElement
            driver.window_handles = [0]

            lock = multimock.Lock()

            jobLoader = Linkedin.JobLoader(driver, lock, 0)

            # act
            result = jobLoader.loadJobs(params, shouldSleep = False)

            # assert
            self.assertEqual(len(result), jobCount)
            self.assertIn('ERROR:linkedinjobloader:Error parsing job count', cm.output)
            self.assertIn('WARNING:linkedinjobloader:Could not determine how many jobs to load, will exit without loading jobs', cm.output)
            self.assertIn('INFO:linkedinjobloader:Loaded a total of 0 jobs', cm.output)


    def test_LinkedinJobLoaderLoadsEmptyListOnException(self):
        with self.assertLogs('linkedinjobloader', level='ERROR') as cm:
            # arrange
            params = Linkedin.SearchParams()
            params.query = 'A'
            params.location = 'B'

            driver = Mock()
            driver.get.side_effect = Exception('Fubar!')
            driver.window_handles = [0]

            lock = multimock.Lock()

            jobLoader = Linkedin.JobLoader(driver, lock, 0)

            # act
            result = jobLoader.loadJobs(params, shouldSleep = False)

            # assert
            self.assertEqual(len(result), 0)
            self.assertEqual(len(cm.output), 1)
            self.assertIn('ERROR:linkedinjobloader:Exception on loading jobs', cm.output[0])
            self.assertIn('Fubar!', cm.output[0])


    def test_LinkedinJobLoaderStopsLoadingJobsIfPageHasZeroResults(self):
        with self.assertLogs('linkedinjobloader', level='INFO') as cm:
            # arrange
            params = Linkedin.SearchParams()
            params.query = 'A'
            params.location = 'B'

            driver = Mock()

            jobCount = 125
            limitElement = Mock()
            limitElement.text = str(jobCount)
            driver.find_element.return_value = limitElement
            driver.find_elements.side_effect = [ self.__generateJobElements(LINKEDIN_PAGE_SIZE), self.__generateJobElements(0) ]
            driver.window_handles = [0]

            lock = multimock.Lock()

            jobLoader = Linkedin.JobLoader(driver, lock, 0)

            # act
            result = jobLoader.loadJobs(params, shouldSleep = False)

            # assert
            self.assertEqual(len(result), LINKEDIN_PAGE_SIZE)
            self.assertIn('INFO:linkedinjobloader:Will attempt to load 125 jobs', cm.output)
            self.assertIn('INFO:linkedinjobloader:Loaded 25 out of 125 jobs', cm.output)
            self.assertIn('INFO:linkedinjobloader:Found zero jobs on page, looks like there are no more jobs, process finished', cm.output)
            self.assertIn('INFO:linkedinjobloader:Loaded a total of 25 jobs', cm.output)


if __name__ == '__main__':
    unittest.main()