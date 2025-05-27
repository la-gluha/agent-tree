from requester import ModelRequester
from prompt import CustomPrompt
from message import CustomMessage 
from context import Context

class Model:
    def __init__(self, model_requester: ModelRequester, additional_params: dict = None):
        self.model_requester = model_requester
        self.additional_params = additional_params or {}

    def chat(self, user_message: str) -> str:
        prompt = CustomPrompt(user_message)
        custom_message_response: CustomMessage = self.model_requester.request(prompt, **self.additional_params)
        
        parsed_content = custom_message_response.get_content()
        response_str = ""
        if parsed_content and parsed_content[0].get("role") == "assistant":
            response_str = parsed_content[0].get("content", "Error: No content")
        elif parsed_content: # If there's something, try to stringify the first part
             response_str = parsed_content[0].get("content", "Error: No content / Unknown role")
        else:
            response_str = "Error: Invalid message structure"
        return response_str

    def step(self, user_message: str, context: Context) -> str:
        # user_message is assumed to be the full prompt string for the model
        context.add_message("user", user_message)
        
        prompt = CustomPrompt(user_message)
        custom_message_response: CustomMessage = self.model_requester.request(prompt, **self.additional_params)
        
        parsed_content = custom_message_response.get_content()
        model_response_str = ""
        if parsed_content and parsed_content[0].get("role") == "assistant": 
            model_response_str = parsed_content[0].get("content", "Error: No content")
        elif parsed_content: 
             model_response_str = parsed_content[0].get("content", "Error: No content / Unknown role")
        else:
            model_response_str = "Error: Invalid message structure from model"
            
        context.add_message("assistant", model_response_str)
        return model_response_str
