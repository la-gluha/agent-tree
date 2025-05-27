import unittest
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from model import Model
from context import Context

class TestModel(unittest.TestCase):
    def setUp(self):
        self.model = Model("test_type", "test_name", "http://fakeapi.com")

    def test_chat(self):
        response = self.model.chat("Hello model")
        self.assertEqual(response, "Model response to: Hello model")

    def test_step(self):
        ctx = Context()
        response = self.model.step("User message for step", ctx)
        self.assertEqual(response, "Model step response based on context. Last user message: User message for step")
        history = ctx.get_history()
        self.assertEqual(len(history), 2)
        self.assertEqual(history[0], {"role": "user", "content": "User message for step"})
        self.assertEqual(history[1], {"role": "assistant", "content": response})

if __name__ == '__main__':
    unittest.main()
