import unittest
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from context import Context

class TestContext(unittest.TestCase):
    def test_add_and_get_history(self):
        ctx = Context()
        self.assertEqual(ctx.get_history(), [])
        ctx.add_message("user", "Hello")
        self.assertEqual(ctx.get_history(), [{"role": "user", "content": "Hello"}])
        ctx.add_message("assistant", "Hi there")
        self.assertEqual(ctx.get_history(), [
            {"role": "user", "content": "Hello"},
            {"role": "assistant", "content": "Hi there"}
        ])

if __name__ == '__main__':
    unittest.main()
