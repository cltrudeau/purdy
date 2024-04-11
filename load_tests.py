#!/usr/bin/env python
import unittest, sys
from waelstow import discover_tests

def get_suite(labels=[]):
#    breakpoint()
#    return discover_tests('tests', labels)
    tests = discover_tests('tests', labels)
    return tests


if __name__ == '__main__':
    suite = get_suite(sys.argv[1:])
    unittest.TextTestRunner(verbosity=1).run(suite)
