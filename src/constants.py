#!/usr/bin/env python3

CHROME_DRIVER_PATH = 'C:\Path\To\Your\chromedriver.exe'
LOG_CONFIG_FILE_NAME = 'logging.conf'
STOPLIST_FILE_NAME = 'stoplist.csv'
REPORT_FOLDER_NAME = 'reports'
KEEP_NEWEST_REPORTS_COUNT = 10

INDEED_HOST = 'https://www.indeed.com/'
INDEED_SEARCH_PATH = 'jobs'
INDEED_JOB_LOADING_LIMIT = 500

LINKEDIN_HOST = 'https://www.linkedin.com/'
LINKEDIN_NORMAL_SEARCH_PATH = 'jobs/search'; # returns normally rendered page
LINKEDIN_PARTIAL_SEARCH_PATH = 'jobs-guest/jobs/api/seeMoreJobPostings/search'; # returns only html for job list
LINKEDIN_PAGE_SIZE = 25
LINKEDIN_JOB_LOADING_LIMIT = 500

GLASSDOOR_HOST = 'https://www.glassdoor.com'
GLASSDOOR_SEARCH_PAGE = 'Search/results.htm'
GLASSDOOR_SEARCH_PARAM = 'keyword'

LOGGER_NAME = 'scrapeLogger'
MIN_SECONDS_TO_SLEEP = 5
MAX_SECONDS_TO_SLEEP = 15

DEROGATORY_MARK_WEIGHT_HANDICAP = -10
DESIRABLE_WORD_WEIGHT_BONUS = 2