#!/usr/bin/env python3

from logging import getLogger
import logging.config
import undetected_chromedriver as uc
from selenium import webdriver 
from datetime import datetime
from multiprocessing import Manager
import concurrent.futures as f
import traceback
import sys

import src.indeed as Indeed
import src.linkedin as Linkedin
from src.base.basejobloader import BaseJobLoader
from src.constants import CHROME_DRIVER_PATH, STOPLIST_FILE_NAME, REPORT_FOLDER_NAME, KEEP_NEWEST_REPORTS_COUNT
from src.constants import DEROGATORY_MARK_WEIGHT_HANDICAP, LOG_CONFIG_FILE_NAME, MAX_THREADS
from src.utility import getAbsPathRelativeToFile, getSimpleModuleName
from src.jobprocessor import JobProcessor, RegexFilteringWeight, SalaryFilteringWeight
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

        # setup job filtering/weighing after search
        weighingConditions = [RegexFilteringWeight(fieldNameToTest = 'title', weight = DEROGATORY_MARK_WEIGHT_HANDICAP, regex = r'diesel|loader'),
                              RegexFilteringWeight(fieldNameToTest = 'company', weight = DEROGATORY_MARK_WEIGHT_HANDICAP, regex = r'recruit|hire|talent|partners'),
                              RegexFilteringWeight(fieldNameToTest = 'title', weight = 2, regex = r'class a|local'),
                              RegexFilteringWeight(fieldNameToTest = 'company', weight = 1, regex = r'department'),
                              SalaryFilteringWeight(weight = 3, salaryMustBeNoLessThan = 80000)]

        # setup browser
        options = webdriver.ChromeOptions()
        options.add_argument("--lang=en-US")
        options.add_argument('--headless=new') # no browser window
        driver = uc.Chrome(options=options, driver_executable_path=CHROME_DRIVER_PATH)

        # setup multithreading
        m = Manager()
        lock = m.Lock()
        searchParams = [ indeedParams, linkedinParams ]
        for i in range(len(searchParams) - 1): # open tabs for Indeed and Linkedin in browser
            driver.execute_script("window.open('');")
        loaders = [ Indeed.JobLoader(driver, lock, tabNumber = 0), Linkedin.JobLoader(driver, lock, tabNumber = 1) ]
        jobs = []

        # load jobs
        with f.ThreadPoolExecutor(max_workers=MAX_THREADS) as executor:
            results = executor.map(BaseJobLoader.loadJobs, loaders, searchParams)
            for result in results:
                jobs.extend(result)

        # Seeing "OSError: [WinError 6] The handle is invalid" on quit?
        # Use this solution: https://github.com/ultrafunkamsterdam/undetected-chromedriver/issues/955#issuecomment-1473294652
        driver.quit() # stop browser.

        # process jobs (assign weights and derogatory marks based on job titles and company names, then sort)
        jobProcessor = JobProcessor(getAbsPathRelativeToFile(__file__, STOPLIST_FILE_NAME), weighingConditions)
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
            getLogger(getSimpleModuleName(__name__)).critical("Critical error, application cannot continue", exc_info=1)
        except Exception as ex2: # in case logger is badly configured and we can't use it, log to console
            traceback.print_exception(*exInfo)
            traceback.print_exc()