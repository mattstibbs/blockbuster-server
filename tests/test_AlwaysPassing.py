import unittest

class PassingTests(unittest.TestCase):

    def setUp(self):
        self.a = 1
        self.b = 1

    def test_passes(self):
        """Should always pass to prove test runner is running tests"""
        self.assertEqual(self.a,self.b)

if __name__ == '__main__':
    unittest.main()