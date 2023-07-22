#!/usr/bin/env python3

import unittest
import os
import sys
from datetime import datetime

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.jobprocessor import JobProcessor
from src.jobinfo import JobInfo, JobLocation
from src.utility import getAbsPathRelativeToFile
from src.constants import LOGGER_NAME

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
        self.assertListEqual(list(map(vars, result[0].locations)), list(map(vars, [ JobLocation('New York, NY', 'http://example1.com'), JobLocation('Troy, MO', 'http://example2.com') ])))
        self.assertListEqual(result[0].salaries, [ '$100,000 a year', '$90,000 a year' ])


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
        with self.assertLogs(LOGGER_NAME, level='WARNING') as cm:
            # arrange
            jobs = [ JobInfo('Nurse', 'Hospital', 'http://example.com', 'New York, NY', '', datetime.now()) ]
            nonexistentPath = getAbsPathRelativeToFile(__file__, 'resources', 'nonexistent.csv')
            jobProcessor = JobProcessor(stopListPath = nonexistentPath)

            # act
            jobProcessor.processJobs(jobs)

            # assert
            self.assertEqual(cm.output, 
                             ['WARNING:%s:Expected to find stoplist at "%s" but it was not there. Jobs will not be processed against stoplist.' % ( LOGGER_NAME, nonexistentPath )])  
            
               

    __undesirableWordsInTitleTestParams = [('Senior Java Developer', 'Undesirable word in job title: \'Java\''),
                                           ('Junior C++ Developer', 'Undesirable word in job title: \'C++\'')]
    
    def test_UndesirableWordInTitleResultsInDerogatoryMark(self):
        for title, expectedDerogatoryMark in self.__undesirableWordsInTitleTestParams:
            with self.subTest():
                with self.assertLogs(LOGGER_NAME, level='INFO'):
                    # arrange
                    jobs = [ JobInfo(title, 'Big Company', 'http://example.com', 'New York, NY', '', datetime.now()) ]
                    jobProcessor = JobProcessor(badTitleRegexString = r'c\+\+|java')

                    # act
                    result = jobProcessor.processJobs(jobs)

                    # assert
                    self.assertIn(expectedDerogatoryMark, result[0].derogatoryMarks)
                    self.assertLess(result[0].weight, 0)


    __undesirableWordsInCompanyTestParams = [('HireWrong', 'Undesirable word in company name: \'Hire\''),
                                             ('LocalTalent', 'Undesirable word in company name: \'Talent\'')]


    def test_UndesirableWordInCompanyResultsInDerogatoryMark(self):
        for company, expectedDerogatoryMark in self.__undesirableWordsInCompanyTestParams:
            with self.subTest():
                with self.assertLogs(LOGGER_NAME, level='INFO'):
                    # arrange
                    jobs = [ JobInfo('Nurse', company, 'http://example.com', 'New York, NY', '', datetime.now()) ]
                    jobProcessor = JobProcessor(badCompanyRegexString = r'hire|talent')

                    # act
                    result = jobProcessor.processJobs(jobs)

                    # assert
                    self.assertIn(expectedDerogatoryMark, result[0].derogatoryMarks)
                    self.assertLess(result[0].weight, 0)


    __desirableWordsInTitleTestParams = [('Senior Java Developer'), ('Junior C++ Developer')]

    def test_DesirableWordInTitleResultsInHigherWeight(self):
        for title in self.__desirableWordsInTitleTestParams:
            with self.subTest():
                with self.assertLogs(LOGGER_NAME, level='INFO'):
                    # arrange
                    jobs = [ JobInfo(title, 'Big Company', 'http://example.com', 'New York, NY', '', datetime.now()) ]
                    jobProcessor = JobProcessor(goodTitleRegexString = r'c\+\+|java')

                    # act
                    result = jobProcessor.processJobs(jobs)

                    # assert
                    self.assertGreater(result[0].weight, 0)


    __desirableWordsInCompanyTestParams = [('HireWrong'), ('LocalTalent')]

    def test_DesirableWordInCompanyResultsInHigherWeight(self):
        for company in self.__desirableWordsInCompanyTestParams:
            with self.subTest():
                with self.assertLogs(LOGGER_NAME, level='INFO'):
                    # arrange
                    jobs = [ JobInfo('Nurse', company, 'http://example.com', 'New York, NY', '', datetime.now()) ]
                    jobProcessor = JobProcessor(goodCompanyRegexString = r'hire|talent')

                    # act
                    result = jobProcessor.processJobs(jobs)

                    # assert
                    self.assertGreater(result[0].weight, 0)


    def test_NeutralWordInTitleOrCompanyDoesNotAffectWeight(self):
        with self.assertLogs(LOGGER_NAME, level='INFO'):
            # arrange
            jobs = [ JobInfo('Nurse', 'Hospital', 'http://example.com', 'New York, NY', '', datetime.now()) ]
            jobProcessor = JobProcessor()

            # act
            result = jobProcessor.processJobs(jobs)

            # assert
            self.assertEqual(result[0].weight, 0)

    def test_SalaryPresenceResultsInHigherWeight(self):
        with self.assertLogs(LOGGER_NAME, level='INFO'):
            # arrange
            jobs = [ JobInfo('Nurse', 'Hospital', 'http://example.com', 'New York, NY', '$100,000 a year', datetime.now()) ]
            jobProcessor = JobProcessor()

            # act
            result = jobProcessor.processJobs(jobs)

            # assert
            self.assertGreater(result[0].weight, 0)

if __name__ == '__main__':
    unittest.main()