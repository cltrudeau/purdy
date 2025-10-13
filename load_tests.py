#!/usr/bin/env python
import unittest, sys
from waelstow import discover_tests

sys.path.append('./src')

def get_suite(labels=[]):
    return discover_tests('tests', labels)

if __name__ == '__main__':
    suite = get_suite(sys.argv[1:])
    unittest.TextTestRunner(verbosity=1).run(suite)
