import json
from abc import ABC, abstractmethod

class Tool(ABC):
    @abstractmethod
    def get_description(self) -> str:
        """Returns a JSON string describing the tool."""
        pass

    @abstractmethod
    def call(self, tool_input: str) -> str:
        """
        Calls the tool with the given input.
        
        Args:
            tool_input: A string, expected to be JSON or structured input.
            
        Returns:
            A JSON string representing the tool's output.
        """
        pass

class ExampleTool(Tool):
    def get_description(self) -> str:
        description = {
            "name": "ExampleTool",
            "description": "A simple example tool that echoes the input.",
            "parameters": {"type": "object", "properties": {"echo_value": {"type": "string"}}},
            "returns": {"type": "object", "properties": {"original_input": {"type": "string"}}}
        }
        return json.dumps(description)

    def call(self, tool_input: str) -> str:
        try:
            parsed_input = json.loads(tool_input)
            echo_value = parsed_input.get("echo_value", "")
            output = {"original_input": echo_value}
            return json.dumps(output)
        except json.JSONDecodeError:
            # Handle cases where tool_input is not valid JSON
            return json.dumps({"error": "Invalid JSON input", "received_input": tool_input})
