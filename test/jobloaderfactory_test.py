#!/usr/bin/env python3

import unittest
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import src.linkedin as Linkedin
import src.indeed as Indeed
from src.jobloaderfactory import JobLoaderFactory

class Test_JobLoaderFactory(unittest.TestCase):

    __jobLoaderFactoryTestParams = [ (Linkedin.SearchParams(), Linkedin.JobLoader), (Indeed.SearchParams(), Indeed.JobLoader) ]

    def test_JobLoaderFactoryCreatesJobLoaderBySearchParamType(self):
        for searchParams, t in self.__jobLoaderFactoryTestParams:
            with self.subTest():    
                # arrange
                factory = JobLoaderFactory()

                # act
                result = factory.createJobLoader(searchParams, None, None, 0)

                # assert
                self.assertIsInstance(result, t)

    
    def test_JobLoaderFactoryThrowsExceptionOnUnknownSearchParamType(self):
        with self.assertRaises(TypeError):
            # arrange
            searchParams = 'some search params'
            factory = JobLoaderFactory()

            # act
            factory.createJobLoader(searchParams, None, None, 0)