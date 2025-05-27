import json
from typing import Optional, List, Dict, Any, Union 

from model import Model
from context import Context
from tools import Tool # Keep ExampleTool for now, or remove if not directly used
from prompt import CustomPrompt # ADD this
from agent_tree import RedBlackTree # ADD this


class Agent:
    def __init__(self, model: Model, task: str, tools: List[Union[Tool, str]], 
                 agent_id: str = "default_agent", # Added agent_id
                 agent_tree_instance: Optional[RedBlackTree] = None, 
                 max_iterations: int = 5):
        self.model = model
        self.task = task
        self.agent_id = agent_id # Store agent_id
        self.tools_input_list = tools # Store the original list
        self.agent_tree = agent_tree_instance
        self.max_iterations = max_iterations
        self.context = Context()
        self.tool_map: Dict[str, Union[Tool, str]] = {} # Stores Tool objects or agent_ids

        for tool_or_id in self.tools_input_list: # Iterate over the stored input list
            if isinstance(tool_or_id, Tool):
                try:
                    desc = json.loads(tool_or_id.get_description())
                    tool_name = desc.get("name")
                    if tool_name:
                        self.tool_map[tool_name] = tool_or_id
                    else:
                        print(f"Warning: Tool {tool_or_id} has no name in description.")
                except json.JSONDecodeError:
                    print(f"Warning: Could not parse description for tool {tool_or_id}.")
            elif isinstance(tool_or_id, str): # Assume it's an agent_id
                if self.agent_tree and self.agent_tree.search(tool_or_id):
                    # Store the ID, resolve to Agent object at call time
                    self.tool_map[tool_or_id] = tool_or_id 
                elif self.agent_tree:
                    print(f"Warning: Agent ID '{tool_or_id}' not found in provided agent tree.")
                else:
                    # If it's an agent_id string but no tree is provided, it's an issue.
                    # However, we might want to allow registration of agent_ids even if tree is not yet populated,
                    # if the tree can be populated later. For now, strict check.
                    print(f"Warning: Agent ID '{tool_or_id}' provided but no agent tree instance or agent not in tree.")
            else:
                print(f"Warning: Invalid item {tool_or_id} in tools list.")

    def get_agent_description_for_tool_list(self) -> str:
        """
        Returns a JSON string describing the agent for use in a tool list.
        """
        return json.dumps({
            "name": self.agent_id, 
            "description": f"An agent specializing in: {self.task}. Use this agent for tasks related to its specialization.",
            "parameters": {
                "type": "object", 
                "properties": {"task_input": {"type": "string", "description": "The specific task or question for this agent."}},
                "required": ["task_input"]
            },
            "returns": {"type": "string", "description": "Result of the agent's execution."}
        })

    def run(self, initial_user_input: str) -> str:
        self.context.add_message("user", initial_user_input)

        for iteration in range(self.max_iterations):
            # Reason Phase
            tool_descriptions_list = []
            for tool_name, tool_ref in self.tool_map.items():
                if isinstance(tool_ref, Tool):
                    tool_descriptions_list.append(tool_ref.get_description())
                elif isinstance(tool_ref, str): # It's an agent_id
                    if self.agent_tree:
                        # Assuming agent_id is tool_ref
                        fetched_agent = self.agent_tree.search(tool_ref) 
                        if fetched_agent and isinstance(fetched_agent, Agent): # Check if it's an Agent instance
                            tool_descriptions_list.append(fetched_agent.get_agent_description_for_tool_list())
                        else:
                            # Fallback if agent not found or not an Agent instance (e.g. if tree stores other things)
                            tool_descriptions_list.append(json.dumps({
                                "name": tool_ref, 
                                "description": f"Agent with ID '{tool_ref}' (details unavailable, might be misconfigured).",
                                "parameters": {"type": "object", "properties": {"task_input": {"type": "string"}}},
                                "returns": {"type": "string"}
                            }))
                    else: # No agent tree, but an agent_id was in tool_map
                         tool_descriptions_list.append(json.dumps({
                                "name": tool_ref, 
                                "description": f"Agent with ID '{tool_ref}' (Agent Tree not available).",
                                "parameters": {"type": "object", "properties": {"task_input": {"type": "string"}}},
                                "returns": {"type": "string"}
                            }))


            tool_descriptions_str = "\n".join(tool_descriptions_list)
            
            history_messages = []
            for msg in self.context.get_history():
                history_messages.append(f"{msg['role']}: {msg['content']}")
            history_str = "\n".join(history_messages)

            # Using CustomPrompt - the prompt string itself. Model.step will wrap it.
            prompt_template = CustomPrompt(
                "Task: {task}\n\nHistory:\n{history}\n\nAvailable Tools:\n{tools}\n\nBased on the task and history, provide your thought process and the next action to take (e.g., Action: ToolName(json_input)). If the task is complete, provide the final answer directly starting with 'Final Answer:'."
            )
            # For now, not using .format() as the string is constructed directly.
            # If we had placeholders in the template above, we'd use .format()
            prompt_for_model_str = f"Task: {self.task}\n\nHistory:\n{history_str}\n\nAvailable Tools:\n{tool_descriptions_str}\n\nBased on the task and history, provide your thought process and the next action to take (e.g., Action: ToolName(json_input)). If the task is complete, provide the final answer directly starting with 'Final Answer:'."

            model_response_raw = self.model.step(prompt_for_model_str, self.context)

            # Parse Model Response
            action_prefix = "Action: "
            thought_prefix = "Thought: " # Not explicitly used for parsing action, but good to note
            final_answer_prefix = "Final Answer:"

            if final_answer_prefix in model_response_raw:
                # If model indicates final answer, return it.
                # Model.step already added the assistant message to context.
                return model_response_raw 

            action_str_full = None
            if action_prefix in model_response_raw:
                action_start_index = model_response_raw.find(action_prefix) + len(action_prefix)
                action_str_full = model_response_raw[action_start_index:].strip()
            
            if not action_str_full:
                # If no "Action:" and no "Final Answer:", model might be just thinking or task is done implicitly.
                # Let's assume if no action is specified, the response is the final answer or continuation.
                # Model.step already added the assistant message.
                return model_response_raw

            # Act Phase
            try:
                tool_name_end_idx = action_str_full.find("(")
                if tool_name_end_idx == -1 or not action_str_full.endswith(")"):
                    raise ValueError("Invalid action format: Missing '(' or ')'. Expected ToolName(json_input).")

                tool_name = action_str_full[:tool_name_end_idx].strip()
                tool_input_json_string = action_str_full[tool_name_end_idx+1:-1].strip()
                
                tool_ref = self.tool_map.get(tool_name)

                if isinstance(tool_ref, Tool):
                    tool_output = tool_ref.call(tool_input_json_string)
                    self.context.add_message("system", f"Tool {tool_name} output: {tool_output}")
                elif isinstance(tool_ref, str): # It's an agent_id
                    if self.agent_tree:
                        target_agent: Optional[Agent] = self.agent_tree.search(tool_ref)
                        if target_agent and isinstance(target_agent, Agent):
                            # Assuming tool_input_json_string is a JSON string with "task_input"
                            try:
                                sub_agent_task_input_dict = json.loads(tool_input_json_string)
                                sub_agent_task = sub_agent_task_input_dict.get("task_input", "")
                                if not sub_agent_task: # Or if it's just a plain string
                                     sub_agent_task = tool_input_json_string # Fallback if "task_input" not found
                            except json.JSONDecodeError:
                                # If not JSON, assume the whole string is the task input
                                sub_agent_task = tool_input_json_string

                            tool_output = target_agent.run(initial_user_input=sub_agent_task)
                            self.context.add_message("system", f"Agent {tool_name} output: {tool_output}")
                        else:
                            tool_output_str = f"Error: Agent {tool_name} (ID: {tool_ref}) not found in agent tree or is not a valid Agent object."
                            self.context.add_message("system", tool_output_str)
                    else:
                        tool_output_str = f"Error: Agent tree not available to run agent {tool_name}."
                        self.context.add_message("system", tool_output_str)
                else: # Tool not found in map
                    error_message = f"Error: Tool or Agent {tool_name} not found."
                    self.context.add_message("system", error_message)
            
            except ValueError as e:
                error_message = f"Error parsing action string '{action_str_full}': {e}"
                self.context.add_message("system", error_message)
            except Exception as e: 
                error_message = f"An unexpected error occurred while processing action for '{tool_name}': {e}"
                self.context.add_message("system", error_message)

            # Check for task completion based on keywords in model_response_raw (already handled by Final Answer: check)
            # No explicit "final answer" keyword check here as it's handled at the beginning of parsing.

        # Loop finished due to max_iterations
        final_history = self.context.get_history()
        if final_history and final_history[-1]["role"] == "assistant":
            return f"Reached max iterations. Last model response: {final_history[-1]['content']}"
        return "Reached max iterations. No response generated."
