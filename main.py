#!/usr/bin/env python3

import logging
import logging.config
from selenium import webdriver 
from selenium.webdriver.chrome.service import Service as ChromeService
from datetime import datetime
import traceback
import sys

import src.indeed as Indeed
import src.linkedin as Linkedin
from src.constants import CHROME_DRIVER_PATH, STOPLIST_FILE_NAME, REPORT_FOLDER_NAME, KEEP_NEWEST_REPORTS_COUNT, LOG_CONFIG_FILE_NAME, LOGGER_NAME
from src.utility import getAbsPathRelativeToFile
from src.jobprocessor import JobProcessor
from src.renderer.htmlrenderer import HtmlRenderer
from src.filemanager import FileManager

if __name__ == "__main__":
    try:
        # configure logging
        logging.config.fileConfig(getAbsPathRelativeToFile(__file__, LOG_CONFIG_FILE_NAME))

        # setup job search parameters
        indeedParams = Indeed.SearchParams()
        indeedParams.query = 'Spanish AND (Translator OR Interpreter) NOT Medical'
        indeedParams.location = 'United States'
        indeedParams.dateRange = Indeed.Enums.DateRange.Last7Days
        indeedParams.jobType = Indeed.Enums.JobType.Contract
        indeedParams.postedBy = Indeed.Enums.PostedBy.Employer
        indeedParams.remoteOrTemporarilyRemote = Indeed.Enums.Remote.Remote

        linkedinParams = Linkedin.SearchParams()
        linkedinParams.query = 'Truck Driver NOT ("Uber Agency" OR Delivery)'
        linkedinParams.location = 'Los Angeles, California, United States'
        linkedinParams.dateRange = Linkedin.Enums.DateRange.Past24Hours
        linkedinParams.experienceLevel = Linkedin.Enums.ExperienceLevel.EntryLevel
        linkedinParams.withinMiles = Linkedin.Enums.WithinMiles._50

        # setup browser
        options = webdriver.ChromeOptions()
        options.add_argument('--headless=new')
        service = ChromeService(executable_path=CHROME_DRIVER_PATH) 
        driver = webdriver.Chrome(service=service, options=options)

        # load jobs
        jobs = []
        for j in [ { 'loader': Indeed.JobLoader(driver), 'params': indeedParams }, { 'loader': Linkedin.JobLoader(driver), 'params': linkedinParams } ]:
            jobInfos = j['loader'].loadJobs(j['params'])
            jobs.extend(jobInfos)

        driver.quit() # stop browser

        # process jobs (assign weights and derogatory marks based on job titles and company names, then sort)
        jobProcessor = JobProcessor(stopListPath = getAbsPathRelativeToFile(__file__, STOPLIST_FILE_NAME),
                                    badTitleRegexString = r'diesel|loader',
                                    badCompanyRegexString = r'recruit|hire|talent|partners',
                                    goodTitleRegexString = r'class a|local',
                                    goodCompanyRegexString = r'department')
        groupedJobs = jobProcessor.processJobs(jobs)

        # create report
        htmlString = HtmlRenderer().render(groupedJobs, date=datetime.now(), 
                                           searchParams = { 'Indeed Search Parameters': indeedParams, 'Linkedin Search Parameters': linkedinParams })

        # save report
        fileManager = FileManager(getAbsPathRelativeToFile(__file__, REPORT_FOLDER_NAME))
        fileManager.saveFile('report', 'html', htmlString)

        # do some housekeeping - remove old reports
        fileManager.deleteOldFiles('*.html', KEEP_NEWEST_REPORTS_COUNT)
    except Exception as ex:
        exInfo = sys.exc_info()
        try:
            logging.getLogger(LOGGER_NAME).critical("Critical error, application cannot continue", exc_info=1)
        except Exception as ex2: # in case logger is badly configured and we can't use it, log to console
            traceback.print_exception(*exInfo)
            traceback.print_exc()