from abc import ABC, abstractmethod
from typing import List, Dict, Any # Python 3.9+ use list, dict instead of List, Dict
import json

class CustomMessage(ABC):
    def __init__(self, raw_response: Any):
        self.raw_response = raw_response
        self._parsed_content: list[dict] = [] # Stores [{"role": ..., "content": ...}]
        self.parse(raw_response) # Call parse in constructor

    @abstractmethod
    def parse(self, raw_response: Any) -> None:
        '''
        Parses the raw model response and populates internal structured representation.
        This method should populate self._parsed_content.
        '''
        pass

    @abstractmethod
    def get_content(self) -> list[dict]:
        '''
        Returns the parsed message content as a list of dictionaries,
        each with "role" and "content" keys.
        Example: [{"role": "assistant", "content": "Hello there!"}]
                 [{"role": "assistant", "content": "Thought: ..."}, {"role": "tool_call", ...}] 
        '''
        pass

    def __str__(self) -> str:
        # Provides a simple string representation, often the first assistant message.
        content = self.get_content()
        if content and isinstance(content, list) and content[0].get("role") == "assistant":
            return content[0].get("content", "No primary content")
        return f"CustomMessage({json.dumps(self.raw_response)[:50]}...)"

class OpenAIMessage(CustomMessage):
    def parse(self, raw_response: Any) -> None:
        '''
        Parses a typical OpenAI API response.
        Handles chat completions and potentially other formats if extended.
        Populates self._parsed_content.
        '''
        self._parsed_content = []
        if not isinstance(raw_response, dict):
            # If the raw response is just a string or something unexpected, treat it as simple content
            self._parsed_content.append({"role": "assistant", "content": str(raw_response)})
            return

        # Example for Chat Completion format
        if raw_response.get("object") == "chat.completion":
            choices = raw_response.get("choices", [])
            if choices:
                message = choices[0].get("message", {})
                role = message.get("role", "assistant") # Default to assistant
                content = message.get("content")
                
                if content is not None:
                    self._parsed_content.append({"role": role, "content": content})
                
                # Check for tool calls (OpenAI specific)
                tool_calls = message.get("tool_calls")
                if tool_calls:
                    for tool_call in tool_calls:
                        self._parsed_content.append({
                            "role": "tool_call", # Or a more specific role like "assistant_tool_call"
                            "id": tool_call.get("id"),
                            "tool_name": tool_call.get("function", {}).get("name"),
                            "tool_arguments": tool_call.get("function", {}).get("arguments")
                        })
            else: # No choices, maybe an error message or unexpected structure
                error_content = raw_response.get("error", {}).get("message", "Unknown error or empty response")
                self._parsed_content.append({"role": "system", "content": f"Error from API: {error_content}"})
        
        elif "error" in raw_response: # Top-level error
            error_content = raw_response.get("error", {}).get("message", "Unknown error")
            self._parsed_content.append({"role": "system", "content": f"Error from API: {error_content}"})
            
        else: # Fallback for other structures or direct string content
            # This could be more sophisticated, e.g. if the raw_response is just a string.
            self._parsed_content.append({"role": "assistant", "content": str(raw_response)})


    def get_content(self) -> list[dict]:
        return self._parsed_content
