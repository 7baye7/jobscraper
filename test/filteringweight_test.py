#!/usr/bin/env python3

import unittest
import os
import sys
from datetime import datetime

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.jobprocessor import RegexFilteringWeight, SalaryFilteringWeight
from src.jobinfo import Job, JobLocation

class Test_FilteringWeight(unittest.TestCase):

    __undesirableWordsTestParams = [('Senior Java Developer', 'Big Company', RegexFilteringWeight('title', -1, r'c\+\+|java'), 'Undesirable word in title: \'Java\''),
                                    ('Junior C++ Developer', 'Big Company', RegexFilteringWeight('title', -1, r'c\+\+|java'), 'Undesirable word in title: \'C++\''),
                                    ('Nurse', 'HireWrong', RegexFilteringWeight('company', -1, r'hire|talent'), 'Undesirable word in company: \'Hire\''),
                                    ('Dietitian', 'LocalTalent', RegexFilteringWeight('company', -1, r'hire|talent'), 'Undesirable word in company: \'Talent\'')]
     
    def test_RegexFilteringWeightSetsWeightAndDerogatorymarkIfWeightIsNegative(self):
        for title, company, weight, expectedDerogatoryMark in self.__undesirableWordsTestParams:
            with self.subTest():
                # arrange
                job = Job(title, company, datetime.now(), [JobLocation('New York, NY', 'http://example.com')], [])

                # act
                weight.assignWeightAndDerogatoryMarkToJob(job)

                # assert
                self.assertIn(expectedDerogatoryMark, job.derogatoryMarks)
                self.assertEqual(job.weight, -1)

    
    __desirableWordsTestParams = [('Senior Java Developer', 'Big Company', RegexFilteringWeight('title', 1, r'c\+\+|java')),
                                  ('Junior C++ Developer', 'Big Company', RegexFilteringWeight('title', 1, r'c\+\+|java')),
                                  ('Nurse', 'HireWrong', RegexFilteringWeight('company', 1, r'hire|talent')),
                                  ('Dietitian', 'LocalTalent', RegexFilteringWeight('company', 1, r'hire|talent'))]
     
    def test_RegexFilteringWeightSetsWeightIfWeightIsNonNegative(self):
        for title, company, weight in self.__desirableWordsTestParams:
            with self.subTest():
                # arrange
                job = Job(title, company, datetime.now(), [JobLocation('New York, NY', 'http://example.com')], [])

                # act
                weight.assignWeightAndDerogatoryMarkToJob(job)

                # assert
                self.assertEqual(len(job.derogatoryMarks), 0)
                self.assertEqual(job.weight, 1)


    __neutralWordsTestParams = [('Nurse', 'Hospital', RegexFilteringWeight('title', 1, r'c\+\+|java')),
                                ('Nurse', 'Hospital', RegexFilteringWeight('company', 1, r'hire|talent'))]
     
    def test_RegexFilteringWeightDoesNotSetWeightOnNeutralWords(self):
        for title, company, weight in self.__neutralWordsTestParams:
            with self.subTest():
                # arrange
                job = Job(title, company, datetime.now(), [JobLocation('New York, NY', 'http://example.com')], [])

                # act
                weight.assignWeightAndDerogatoryMarkToJob(job)

                # assert
                self.assertEqual(len(job.derogatoryMarks), 0)
                self.assertEqual(job.weight, 0)


    __desirableSalariesTestParams = [[ '$59,108 - $75,652 a year' ], 
                                     [ '$59,108 - $75,652 a year', '$45,000 - $55,000 a year' ],
                                     [ '$112,300 a year' ] ]
     
    def test_SalaryFilteringWeightSetsWeightIfSalaryIsHigherThanSpecified(self):
        for salaryList in self.__desirableSalariesTestParams:
            with self.subTest():
                # arrange
                job = Job('Nurse', 'Hospital', datetime.now(), [JobLocation('New York, NY', 'http://example.com')], salaryList)
                weight = SalaryFilteringWeight(1, 60000)

                # act
                weight.assignWeightAndDerogatoryMarkToJob(job)

                # assert
                self.assertEqual(len(job.derogatoryMarks), 0)
                self.assertEqual(job.weight, 1)


    __undesirableSalariesTestParams = [[ '$12 an hour' ], 
                                       [ '$32,108 - $45,652 a year', '$45,000 - $55,000 a year' ],
                                       [ '$32,108 - $45,652 a year' ],
                                       [ 'Fubar' ] ]
     
    def test_SalaryFilteringWeightDoesNotSetWeightIfSalaryIsLowerThanSpecified(self):
        for salaryList in self.__undesirableSalariesTestParams:
            with self.subTest():
                # arrange
                job = Job('Nurse', 'Hospital', datetime.now(), [JobLocation('New York, NY', 'http://example.com')], salaryList)
                weight = SalaryFilteringWeight(1, 60000)

                # act
                weight.assignWeightAndDerogatoryMarkToJob(job)

                # assert
                self.assertEqual(len(job.derogatoryMarks), 0)
                self.assertEqual(job.weight, 0)

if __name__ == '__main__':
    unittest.main()