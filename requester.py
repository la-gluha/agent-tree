from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Optional, Dict, Any
import json # For potential request/response bodies
# It's good practice to use TYPE_CHECKING for circular dependencies with type hints.
from message import OpenAIMessage # Add this direct import

if TYPE_CHECKING:
    from prompt import CustomPrompt # Assuming CustomPrompt is in prompt.py
    from message import CustomMessage # Assuming CustomMessage is in message.py (will be created next)

class ModelRequester(ABC):
    @abstractmethod
    def __init__(self, model_name: str, api_url_base: Optional[str] = None, **kwargs):
        self.model_name = model_name
        self.api_url_base = api_url_base
        self.additional_config = kwargs

    @abstractmethod
    def request(self, prompt: 'CustomPrompt', api_key: Optional[str] = None, **kwargs) -> 'CustomMessage':
        '''
        Makes a request to the specified model.
        
        Args:
            prompt: The CustomPrompt object containing the formatted prompt.
            api_key: Optional API key.
            **kwargs: Additional parameters for the request (e.g., temperature, max_tokens).
            
        Returns:
            A CustomMessage object containing the model's response.
        '''
        pass

    # Optional factory method (can be omitted if direct instantiation is preferred)
    # @staticmethod
    # @abstractmethod
    # def get_instance(cls, model_type: str, model_name: str, **config) -> 'ModelRequester':
    #     pass 

class OpenAIRequester(ModelRequester):
    DEFAULT_API_URL_BASE = "https://api.openai.com/v1" # Example, adjust as needed

    def __init__(self, model_name: str, api_url_base: Optional[str] = None, **kwargs):
        super().__init__(model_name, api_url_base or self.DEFAULT_API_URL_BASE, **kwargs)
        # For a real implementation, you'd likely use a library like 'requests' or 'httpx'.
        # For this task, we'll mock the actual HTTP call.
        # import httpx # Example, not actually used in mock

    def request(self, prompt: 'CustomPrompt', api_key: Optional[str] = None, **kwargs) -> 'OpenAIMessage': # MODIFIED return type
        print(f"--- OpenAIRequester: Making request for model {self.model_name} ---")
        print(f"URL Base: {self.api_url_base}")
        print(f"Prompt: {str(prompt)}")
        
        if api_key:
            print("API Key provided (mock usage)")
        else:
            print("Warning: API Key not provided for OpenAIRequester.")

        # Constructing a mock request payload
        request_payload = {
            "model": self.model_name,
            "messages": [{"role": "user", "content": str(prompt)}],
            **self.additional_config, # from __init__
            **kwargs # from request method
        }
        print(f"Request Payload (mock): {json.dumps(request_payload, indent=2)}")

        # MOCK RESPONSE (simulating an API call)
        # In a real scenario, this would be an HTTP request and response handling.
        # For example:
        # headers = {"Authorization": f"Bearer {api_key}"} if api_key else {}
        # try:
        #     with httpx.Client() as client:
        #         response = client.post(f"{self.api_url_base}/chat/completions", json=request_payload, headers=headers)
        #         response.raise_for_status() # Raise an exception for bad status codes
        #         raw_api_response = response.json()
        # except Exception as e:
        #     print(f"API Call Error (mock): {e}")
        #     raw_api_response = {"error": str(e)}
        
        # For now, just a fixed mock response structure
        mock_api_response = {
            "id": "chatcmpl-mock123",
            "object": "chat.completion",
            "created": 1677652288,
            "model": self.model_name,
            "choices": [{
                "index": 0,
                "message": {
                    "role": "assistant",
                    "content": f"Mocked OpenAI response to: '{str(prompt)}'. Params: temp={kwargs.get('temperature', 'default')}"
                },
                "finish_reason": "stop"
            }],
            "usage": {
                "prompt_tokens": len(str(prompt).split()),
                "completion_tokens": 10, # mock
                "total_tokens": len(str(prompt).split()) + 10
            }
        }
        print(f"Mock API Response: {json.dumps(mock_api_response, indent=2)}")
        
        # Wrap the raw response in our CustomMessage (OpenAIMessage)
        # The CustomMessage object is responsible for parsing this raw_api_response
        return OpenAIMessage(mock_api_response) # MODIFIED instantiation
