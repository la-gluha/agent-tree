import json
from model import Model
from context import Context
from tools import Tool, ExampleTool # ExampleTool for type hinting or direct use

class Agent:
    def __init__(self, model: Model, task: str, tools: list[Tool], max_iterations: int = 5):
        self.model = model
        self.task = task
        self.tools = tools
        self.max_iterations = max_iterations
        self.context = Context()
        
        self.tool_map: dict[str, Tool] = {}
        for tool in self.tools:
            try:
                description = json.loads(tool.get_description())
                self.tool_map[description['name']] = tool
            except (json.JSONDecodeError, KeyError) as e:
                # Handle cases where description is not valid JSON or 'name' is missing
                print(f"Warning: Could not register tool {tool} due to error: {e}")


    def run(self, initial_user_input: str) -> str:
        self.context.add_message("user", initial_user_input)

        for iteration in range(self.max_iterations):
            # Reason
            tool_descriptions = "\n".join([tool.get_description() for tool in self.tools])
            # Constructing a more structured history string for the prompt
            history_messages = []
            for msg in self.context.get_history():
                history_messages.append(f"{msg['role']}: {msg['content']}")
            history_str = "\n".join(history_messages)

            prompt_for_model = f"Task: {self.task}\n\nHistory:\n{history_str}\n\nAvailable Tools:\n{tool_descriptions}\n\nBased on the task and history, provide your thought process and the next action to take. If the task is complete, provide the final answer directly."
            
            # The model.step method already adds its own "user" (this prompt) and "assistant" (its response) messages to the context
            model_response_raw = self.model.step(prompt_for_model, self.context)

            # Parse Model Response
            action_prefix = "Action: "
            thought_prefix = "Thought: "
            
            action_str_full = None
            if action_prefix in model_response_raw:
                # Simplistic extraction, assumes Action: is followed by the action
                action_start_index = model_response_raw.find(action_prefix) + len(action_prefix)
                action_str_full = model_response_raw[action_start_index:].strip()
            
            if not action_str_full:
                # If no "Action:" or if it's empty, assume the response is a final answer.
                # model.step already added the assistant message to context.
                return model_response_raw # Or a more refined part of it

            # Act
            try:
                # Expecting format: ToolName(json_input)
                tool_name_end_idx = action_str_full.find("(")
                if tool_name_end_idx == -1:
                    raise ValueError("Invalid action format: Missing '('. Expected ToolName(json_input).")

                tool_name = action_str_full[:tool_name_end_idx].strip()
                
                if not action_str_full.endswith(")"):
                    raise ValueError("Invalid action format: Missing ')'. Expected ToolName(json_input).")

                tool_input_json_string = action_str_full[tool_name_end_idx+1:-1].strip()

                if tool_name in self.tool_map:
                    tool_to_call = self.tool_map[tool_name]
                    tool_output = tool_to_call.call(tool_input_json_string)
                    self.context.add_message("system", f"Tool {tool_name} output: {tool_output}")
                else:
                    error_message = f"Error: Tool {tool_name} not found."
                    self.context.add_message("system", error_message)
                    # Optionally, we could return or raise an error here if a tool is critical
            
            except ValueError as e:
                # Error in parsing the action string
                error_message = f"Error parsing action string '{action_str_full}': {e}"
                self.context.add_message("system", error_message)
            except Exception as e: # Catch other unexpected errors during action processing
                error_message = f"An unexpected error occurred while processing action '{action_str_full}': {e}"
                self.context.add_message("system", error_message)

            # Check for task completion (e.g., based on keywords in model_response_raw or if a specific condition is met)
            # This is a simplified check. A more robust check might involve the model explicitly stating completion.
            if "final answer" in model_response_raw.lower() and not action_str_full: # Check if model explicitly states final answer and no action
                 return model_response_raw

        # Loop finished due to max_iterations
        # Get the latest assistant message from context or return a summary
        final_history = self.context.get_history()
        if final_history and final_history[-1]["role"] == "assistant":
            return f"Reached max iterations. Last model response: {final_history[-1]['content']}"
        return "Reached max iterations."
