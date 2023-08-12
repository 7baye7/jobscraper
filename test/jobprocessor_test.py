#!/usr/bin/env python3

import unittest
import os
import sys
from datetime import datetime

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.jobprocessor import JobProcessor, RegexFilteringWeight, SalaryFilteringWeight
from src.jobinfo import JobInfo, JobLocation
from src.utility import getAbsPathRelativeToFile

class Test_JobProcessor(unittest.TestCase):

    def test_JobProcessorGroupsJobsByTitleAndCompany(self):
        # arrange
        date = datetime.now()
        jobs = [ JobInfo('Nurse', 'Hospital', 'http://example1.com', 'New York, NY', '$100,000 a year', date),
                 JobInfo('Nurse', 'Hospital', 'http://example2.com', 'Troy, MO', '$90,000 a year', date) ]
        jobProcessor = JobProcessor(getAbsPathRelativeToFile(__file__, 'resources', 'stoplist.csv'))

        # act
        result = jobProcessor.processJobs(jobs)

        # assert
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].title, 'Nurse')
        self.assertEqual(result[0].company, 'Hospital')
        self.assertEqual(result[0].datePosted, date)
        self.assertCountEqual(result[0].locations, [ JobLocation('New York, NY', 'http://example1.com'), JobLocation('Troy, MO', 'http://example2.com') ])
        self.assertCountEqual(result[0].salaries, [ '$100,000 a year', '$90,000 a year' ])


    __stoplistTestParams = [('Junior Developer', 'No Matter What Company', 'Stoplist entry found for job title = \'Junior Developer\' with reason: Bad pay'),
                            ('No Matter What Title', 'Facebook', 'Stoplist entry found for company name = \'Facebook\' with reason: Annoying company'),
                            ('Driver', 'UPS', 'Stoplist entry found for job title = \'Driver\' and company name = \'UPS\' with reason: They don\'t have cookies')]

    def test_StoplistEntryResultsInDerogatoryMark(self):
        for title, company, expectedDerogatoryMark in self.__stoplistTestParams:
            with self.subTest():    
                # arrange
                jobs = [ JobInfo(title, company, 'http://example.com', 'New York, NY', '', datetime.now()) ]
                jobProcessor = JobProcessor(stopListPath = getAbsPathRelativeToFile(__file__, 'resources', 'stoplist.csv'))

                # act
                result = jobProcessor.processJobs(jobs)

                # assert
                self.assertIn(expectedDerogatoryMark, result[0].derogatoryMarks)
                self.assertLess(result[0].weight, 0)


    def test_NoStoplistIsLogged(self):
        with self.assertLogs('jobprocessor', level='WARNING') as cm:
            # arrange
            jobs = [ JobInfo('Nurse', 'Hospital', 'http://example.com', 'New York, NY', '', datetime.now()) ]
            nonexistentPath = getAbsPathRelativeToFile(__file__, 'resources', 'nonexistent.csv')
            jobProcessor = JobProcessor(stopListPath = nonexistentPath)

            # act
            jobProcessor.processJobs(jobs)

            # assert
            self.assertEqual(cm.output, 
                             ['WARNING:jobprocessor:Expected to find stoplist at "%s" but it was not there. Jobs will not be processed against stoplist.' % nonexistentPath ])  
            
               

    def test_JobProcessorUsesFilteringWeights(self):
            with self.assertLogs('jobprocessor', level='INFO'):
                # arrange
                jobs = [ JobInfo('Junior C++ Developer', 'Big Company', 'http://example.com', 'New York, NY', '$59,108 - $75,652 a year', datetime.now()) ]
                jobProcessor = JobProcessor(filteringWeights=[RegexFilteringWeight('title', -5, r'c\+\+|java'), SalaryFilteringWeight(10, 75000)])

                # act
                result = jobProcessor.processJobs(jobs)

                # assert
                self.assertIn('Undesirable word in title: \'C++\'', result[0].derogatoryMarks)
                self.assertEqual(result[0].weight, 5)


    def test_JobProcessorSquashesIdenticalJobLocationsAndSalaries(self):
        # arrange
        date = datetime.now()
        jobs = [ JobInfo('Nurse', 'Hospital', 'http://example1.com', 'New York, NY', '$100,000 a year', date),
                 JobInfo('Nurse', 'Hospital', 'http://example1.com', 'New York, NY', '$100,000 a year', date) ]
        jobProcessor = JobProcessor(getAbsPathRelativeToFile(__file__, 'resources', 'stoplist.csv'))

        # act
        result = jobProcessor.processJobs(jobs)

        # assert
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].title, 'Nurse')
        self.assertEqual(result[0].company, 'Hospital')
        self.assertEqual(result[0].datePosted, date)
        self.assertCountEqual(result[0].locations, [ JobLocation('New York, NY', 'http://example1.com') ])
        self.assertCountEqual(result[0].salaries, [ '$100,000 a year' ])


if __name__ == '__main__':
    unittest.main()