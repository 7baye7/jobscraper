#!/usr/bin/env python3

import unittest
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import src.linkedin as Linkedin

class Test_LinkedinUrlBuilder(unittest.TestCase):

    def __init__(self, methodName: str = "runTest") -> None:
        super().__init__(methodName)

        p1 = Linkedin.SearchParams()
        p1.query = 'registered nurse'
        p1.location = 'Los Angeles, CA'
        p1.dateRange = Linkedin.Enums.DateRange.PastMonth

        p2 = Linkedin.SearchParams()
        p2.query = 'registered nurse'
        p2.location = 'Los Angeles, CA'
        p2.experienceLevel = Linkedin.Enums.ExperienceLevel.EntryLevel
        p2.jobType = Linkedin.Enums.JobType.Contract
        p2.remoteFilter = Linkedin.Enums.Remote.OnSite
        p2.dateRange = Linkedin.Enums.DateRange.PastWeek
        p2.salary = Linkedin.Enums.Salary._100000
        p2.withinMiles = Linkedin.Enums.WithinMiles._50

        pNoQuery = Linkedin.SearchParams()

        pNoLocation = Linkedin.SearchParams()
        pNoLocation.query = 'registered nurse'

        self.__urlBuilderParams = [(p1, {}, 'https://www.linkedin.com/jobs/search?keywords=registered+nurse&location=Los+Angeles%2C+CA&f_TPR=r2592000'),
                                    (p1, { 'startFrom': 25, 'partial': True }, 'https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search?keywords=registered+nurse&location=Los+Angeles%2C+CA&f_TPR=r2592000&startFrom=25'),
                                    (p2, {}, 'https://www.linkedin.com/jobs/search?keywords=registered+nurse&location=Los+Angeles%2C+CA&f_TPR=r604800&f_SB2=4&f_E=2&f_WT=1&f_JT=C&distance=50'),]
        
        self.__urlBuilderParamsWithValueError = [ pNoQuery, pNoLocation ]

    def test_urlBuilderBuildsUrl(self):
        for params, extraParams, expectedResult in self.__urlBuilderParams:
            with self.subTest():
                # act
                result = Linkedin.UrlBuilder.buildUrl(params, extraParams)

                # assert
                self.assertEqual(result, expectedResult)

    def test_urlBuilderThrowsValueError(self):
        for params in self.__urlBuilderParamsWithValueError:
            with self.assertRaises(ValueError):
                # act
                Linkedin.UrlBuilder.buildUrl(params)

if __name__ == '__main__':
    unittest.main()