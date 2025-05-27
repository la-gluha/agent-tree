import unittest
import sys
import os
import json
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from tools import ExampleTool # Assuming Tool is ABC, test concrete ExampleTool

class TestExampleTool(unittest.TestCase):
    def setUp(self):
        self.tool = ExampleTool()

    def test_get_description(self):
        desc_str = self.tool.get_description()
        desc_json = json.loads(desc_str)
        self.assertEqual(desc_json["name"], "ExampleTool")
        self.assertIn("description", desc_json)
        self.assertIn("parameters", desc_json)
        self.assertIn("returns", desc_json)

    def test_call(self):
        tool_input_str = '{"echo_value": "Test Echo"}'
        output_str = self.tool.call(tool_input_str)
        output_json = json.loads(output_str)
        self.assertEqual(output_json["original_input"], "Test Echo")

    def test_call_invalid_json(self):
        tool_input_str = '{"echo_value": "Test Echo"' # Invalid JSON
        output_str = self.tool.call(tool_input_str)
        output_json = json.loads(output_str)
        self.assertIn("error", output_json)
        self.assertIn("JSONDecodeError", output_json["error"])
           
    def test_call_missing_key(self):
        tool_input_str = '{"wrong_key": "Test Echo"}'
        output_str = self.tool.call(tool_input_str)
        output_json = json.loads(output_str)
        # ExampleTool's current implementation would return original_input: ""
        # This test depends on how strictly you want to define behavior for missing keys.
        # For now, let's check if it doesn't crash and returns the expected structure.
        self.assertIn("original_input", output_json)
        self.assertEqual(output_json["original_input"], "")


if __name__ == '__main__':
    unittest.main()
