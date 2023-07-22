#!/usr/bin/env python3

import unittest
import os
import sys
from datetime import datetime

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.renderer.htmlrenderer import HtmlRenderer
from src.jobinfo import Job, JobLocation
from src.utility import getAbsPathRelativeToFile
import src.indeed as Indeed
import src.linkedin as Linkedin

class Test_HtmlRenderer(unittest.TestCase):

    def test_HtmlRendererRendersReport(self):
        # arrange
        date = datetime(2020, 2, 2)
        job1 = Job('Nurse', 'Hospital1', date, [JobLocation('New York, NY', 'http://example1.com'), JobLocation('Troy, MO', 'http://example2.com')], ['$100,000 a year', '$50-60 an hour'])
        job1.weight = 1
        job2 = Job('Registered Nurse', 'Hospital2', date, [JobLocation('Anaheim, CA', 'http://example3.com')], ['$90,000 a year'])
        job2.weight = -10
        job2.derogatoryMarks.append('Derogatory mark 1')
        job3 = Job('School Nurse', 'School 1', date, [JobLocation('Atlanta, GA', 'http://example4.com')], [])
        job3.weight = -20
        job3.derogatoryMarks.extend([ 'Derogatory mark 2', 'Derogatory mark 3' ])
        jobs = [ job1, job2, job3 ]

        p1 = Indeed.SearchParams()
        p1.query = 'registered nurse'
        p1.location = 'Los Angeles, CA'
        p1.remoteOrTemporarilyRemote = Indeed.Enums.Remote.Remote
        p1.experienceLevel = Indeed.Enums.ExperienceLevel.MidLevel
        p1.education = Indeed.Enums.Education.Bachelor
        p1.postedBy = Indeed.Enums.PostedBy.Employer
        p1.secondaryLocation = Indeed.Location('Torrance, CA', 'fa797dbf4932c2b4')
        p1.companyFccKey = '1234567890abcdef'
        p1.encouragedToApply = Indeed.Enums.EncouragedToApply.MilitaryEncouraged
        p1.withinMiles = Indeed.Enums.WithinMiles.Within50Miles
        p1.salary = '$90,000'

        p2 = Linkedin.SearchParams()
        p2.query = 'registered nurse'
        p2.location = 'Los Angeles, CA'
        p2.experienceLevel = Linkedin.Enums.ExperienceLevel.EntryLevel
        p2.jobType = Linkedin.Enums.JobType.Contract
        p2.remoteFilter = Linkedin.Enums.Remote.OnSite
        p2.dateRange = Linkedin.Enums.DateRange.PastWeek
        p2.salary = Linkedin.Enums.Salary._100000
        p2.withinMiles = Linkedin.Enums.WithinMiles._50

        htmlRenderer = HtmlRenderer()

        # act
        result = htmlRenderer.render(jobs, date = date, searchParams = { 'Indeed Search Parameters': p1, 'Linkedin Search Parameters': p2 })

        # assert
        expectedReportFilePath = getAbsPathRelativeToFile(__file__, 'resources', 'expected_report.html')
        with open(expectedReportFilePath, newline='', encoding='utf-8') as f:
            expectedContent = f.read()
            self.assertEqual(result, expectedContent)

    def test_HtmlRendererRendersEmptyReport(self):
        # arrange
        htmlRenderer = HtmlRenderer()

        # act
        result = htmlRenderer.render([])

        # assert
        expectedReportFilePath = getAbsPathRelativeToFile(__file__, 'resources', 'expected_empty_report.html')
        with open(expectedReportFilePath, newline='', encoding='utf-8') as f:
            expectedContent = f.read()
            self.assertEqual(result, expectedContent)