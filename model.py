from context import Context

class Model:
    def __init__(self, model_type: str, model_name: str, api_url: str, api_key: str = None, additional_params: dict = None):
        self.model_type = model_type
        self.model_name = model_name
        self.api_url = api_url
        self.api_key = api_key
        self.additional_params = additional_params if additional_params is not None else {}

    def chat(self, user_message: str) -> str:
        # Simulate a single API call
        # Does not use or modify any context object
        return f"Model response to: {user_message}"

    def step(self, user_message: str, context: 'Context') -> str:
        # Add the user_message to the passed context object
        context.add_message("user", user_message)

        # Simulate an API call (prompt could be built from context.get_history())
        # For now, using a canned response
        model_response = f"Model step response based on context. Last user message: {user_message}"

        # Add this model's response to the context object
        context.add_message("assistant", model_response)

        return model_response
