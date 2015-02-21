import os
import sys
import unittest
from unittest import TestCase

eveapi_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
sys.path.insert(0, eveapi_path)


class ImportTestCase(TestCase):
    """
    Tests that eveapi has still same import paths.
    """

    def test_imports(self):
        import eveapi


if __name__ == '__main__':
    unittest.main()
