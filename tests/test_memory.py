import unittest
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from memory import Memory

class TestMemory(unittest.TestCase):
    def test_add_and_query_memory(self):
        mem = Memory()
        self.assertEqual(mem.query("test"), [])
        mem.add("This is a test entry.")
        mem.add("Another entry here.")
        mem.add("Testing is important.")
        self.assertEqual(mem.query("test"), ["This is a test entry.", "Testing is important."])
        self.assertEqual(mem.query("entry"), ["This is a test entry.", "Another entry here."])
        self.assertEqual(mem.query("nonexistent"), [])

if __name__ == '__main__':
    unittest.main()
