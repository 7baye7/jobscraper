#!/usr/bin/env python3

import unittest
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import src.indeed as Indeed

class Test_IndeedUrlBuilder(unittest.TestCase):

    def __init__(self, methodName: str = "runTest") -> None:
        super().__init__(methodName)

        p1 = Indeed.SearchParams()
        p1.query = 'registered nurse'
        p1.location = 'Los Angeles, CA'
        p1.dateRange = Indeed.Enums.DateRange.Last24Hours

        p2 = Indeed.SearchParams()
        p2.query = 'registered nurse'
        p2.location = 'Los Angeles, CA'
        p2.remoteOrTemporarilyRemote = Indeed.Enums.Remote.Remote
        p2.experienceLevel = Indeed.Enums.ExperienceLevel.MidLevel
        p2.education = Indeed.Enums.Education.Bachelor
        p2.postedBy = Indeed.Enums.PostedBy.Employer
        p2.secondaryLocation = Indeed.Location('Torrance, CA', 'fa797dbf4932c2b4')
        p2.companyFccKey = '1234567890abcdef'
        p2.encouragedToApply = Indeed.Enums.EncouragedToApply.MilitaryEncouraged
        p2.withinMiles = Indeed.Enums.WithinMiles.Within50Miles
        p2.salary = '$90,000'

        pNoQuery = Indeed.SearchParams()

        pNoLocation = Indeed.SearchParams()
        pNoLocation.query = 'registered nurse'

        self.__urlBuilderParams = [(p1, {}, 'https://www.indeed.com/jobs?q=registered+nurse&l=Los+Angeles%2C+CA&fromage=1'),
                                    (p1, { 'start': 10 }, 'https://www.indeed.com/jobs?q=registered+nurse&l=Los+Angeles%2C+CA&fromage=1&start=10'),
                                    (p2, {}, 'https://www.indeed.com/jobs?q=registered+nurse+%2490%2C000&l=Los+Angeles%2C+CA&radius=50&sc=0bf%3Aexrec%28%29%2Ckf%3Aattr%28DSQF7%29explvl%28MID_LEVEL%29attr%28FCGTU%7CHFDVW%7CQJZM9%7CUTPWG%2COR%29attr%28MUDKG%29fcckey%281234567890abcdef%29%3B&rbl=Torrance%2C+CA&jlid=fa797dbf4932c2b4'),]
        
        self.__urlBuilderParamsWithValueError = [ pNoQuery, pNoLocation ]

    def test_urlBuilderBuildsUrl(self):
        for params, extraParams, expectedResult in self.__urlBuilderParams:
            with self.subTest():
                # act
                result = Indeed.UrlBuilder.buildUrl(params, extraParams)

                # assert
                self.assertEqual(result, expectedResult)

    def test_urlBuilderThrowsValueError(self):
        for params in self.__urlBuilderParamsWithValueError:
            with self.assertRaises(ValueError):
                # act
                Indeed.UrlBuilder.buildUrl(params)

if __name__ == '__main__':
    unittest.main()