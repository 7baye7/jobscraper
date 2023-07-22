#!/usr/bin/env python3

import unittest
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.utility import *
from src.indeed.enums import DateRange

class Test_Utility(unittest.TestCase):

    __isNullOrWhiteSpaceParams = [(None, True),
                                  ('', True), 
                                  ('   ', True),
                                  ('string', False)]
    def test_isNullOrWhiteSpaceReturnsTrueOnEmptyStrings(self):
        for s, expectedResult in self.__isNullOrWhiteSpaceParams:
            with self.subTest():    
                # act
                result = isNullOrWhiteSpace(s)

                # assert
                self.assertEqual(result, expectedResult)


    __buildUrlParams = [('https://www.example.com', 'fubar/foo', { 'param1': 'value 1', 'param2': 2 }, 'https://www.example.com/fubar/foo?param1=value+1&param2=2'),
                        ('https://www.example.com/', '/fubar/', {}, 'https://www.example.com/fubar/')]
    def test_buildUrl(self):
        for host, path, params, expectedResult in self.__buildUrlParams:
            with self.subTest():    
                # act
                result = buildUrl(host, path, params)

                # assert
                self.assertEqual(result, expectedResult)


    __getTrimmedStringValueOrEmptyStringParams = [(None, ''),
                                                  ('', ''),
                                                  ('   ', ''),
                                                  ('string', 'string'),
                                                  ('  string  ', 'string')]
    def test_getTrimmedStringValueOrEmptyString(self):
        for s, expectedResult in self.__getTrimmedStringValueOrEmptyStringParams:
            with self.subTest():    
                # act
                result = getTrimmedStringValueOrEmptyString(s)

                # assert
                self.assertEqual(result, expectedResult)


    __getEnumValueOrEmptyStringParams = [(DateRange.Last7Days, '7'),
                                         (None, '')]
    def test_getEnumValueOrEmptyString(self):
        for s, expectedResult in self.__getEnumValueOrEmptyStringParams:
            with self.subTest():    
                # act
                result = getEnumValueOrEmptyString(s)

                # assert
                self.assertEqual(result, expectedResult)

if __name__ == '__main__':
    unittest.main()