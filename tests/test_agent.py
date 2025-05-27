import unittest
import sys
import os
import json
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from agent import Agent
from model import Model
from context import Context
from tools import ExampleTool, Tool

# Mock Model for Agent testing
class MockModel(Model):
    def __init__(self, model_type="mock", model_name="mock_model", api_url=""):
        super().__init__(model_type, model_name, api_url)
        self.responses = [] # Predefined responses for step method
        self.call_count = 0

    def set_responses(self, responses):
        self.responses = responses
        self.call_count = 0
           
    def step(self, user_message: str, context: Context) -> str:
        # Add user message to context (as Agent's prompt)
        context.add_message("user", user_message) # Agent's prompt is "user" to model
           
        response = ""
        if self.call_count < len(self.responses):
            response = self.responses[self.call_count]
        else:
            response = "Thought: No more pre-defined responses. Action: End" # Default fallback
        
        self.call_count += 1
        # Add model response to context
        context.add_message("assistant", response)
        return response

class TestAgent(unittest.TestCase):
    def setUp(self):
        self.example_tool = ExampleTool()
        self.mock_model = MockModel()
        self.agent = Agent(model=self.mock_model, task="Test task", tools=[self.example_tool], max_iterations=3)

    def test_agent_initialization(self):
        self.assertEqual(self.agent.task, "Test task")
        self.assertIsInstance(self.agent.model, MockModel)
        self.assertIn("ExampleTool", self.agent.tool_map)
        self.assertIsInstance(self.agent.tool_map["ExampleTool"], ExampleTool)

    def test_agent_run_simple_response(self):
        # Model responds directly without tool
        self.mock_model.set_responses(["Thought: Task is simple. Final Answer: All done."])
        final_response = self.agent.run("User starts conversation")
           
        self.assertIn("Final Answer: All done", final_response)
        # Check context for initial user message, model's prompt, and model's response
        history = self.agent.context.get_history()
        self.assertEqual(history[0]["role"], "user")
        self.assertEqual(history[0]["content"], "User starts conversation")
        self.assertTrue(history[1]["role"] == "user") # Agent's prompt to model
        self.assertTrue("Task: Test task" in history[1]["content"])
        self.assertEqual(history[2]["role"], "assistant")
        self.assertEqual(history[2]["content"], "Thought: Task is simple. Final Answer: All done.")

    def test_agent_run_with_tool_call(self):
        tool_call_action = 'Action: ExampleTool({"echo_value": "Hello from agent"})'
        model_responses = [
            f"Thought: I need to use ExampleTool. {tool_call_action}",
            "Thought: Tool executed. Final Answer: Tool said hi."
        ]
        self.mock_model.set_responses(model_responses)
           
        final_response = self.agent.run("User wants to test ExampleTool")
           
        self.assertIn("Final Answer: Tool said hi.", final_response)
        history = self.agent.context.get_history()
           
        # Expected sequence: user initial, agent prompt1, model response1 (tool call), system (tool output), agent prompt2, model response2 (final)
        self.assertEqual(history[0]["content"], "User wants to test ExampleTool") # Initial User
        self.assertIn(tool_call_action, history[2]["content"]) # Model response with tool action
        self.assertEqual(history[3]["role"], "system") # Tool output
        tool_output_json = json.loads(history[3]["content"].split("output: ", 1)[1]) # crude split
        self.assertEqual(tool_output_json["original_input"], "Hello from agent")
        self.assertIn("Final Answer: Tool said hi.", history[5]["content"]) # Final model response

    def test_agent_run_max_iterations(self):
        # Model keeps responding without "Final Answer" or a clear end
        model_responses = [
            "Thought: Thinking...",
            "Thought: Still thinking...",
            "Thought: Almost there..."
        ]
        self.mock_model.set_responses(model_responses)
           
        final_response = self.agent.run("User asks a complex question")
        self.assertEqual(final_response, "Thought: Almost there...") # Returns last model response
        self.assertEqual(self.mock_model.call_count, 3) # Reached max_iterations

if __name__ == '__main__':
    unittest.main()
