# example_advanced.py
import json # For printing dicts nicely
import sys
import os

# Ensure root directory is in path for imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '.')))

from agent_tree import RedBlackTree
from agent import Agent
from model import Model
from requester import OpenAIRequester # Using the mocked one
from tools import ExampleTool
from prompt import CustomPrompt # Though not explicitly used in this simplified main flow, good to show it's part of the ecosystem

def main():
    print("--- Advanced Multi-Agent Framework Example ---")

    # 1. Setup Model and Requester
    # Using the mocked OpenAIRequester
    openai_requester = OpenAIRequester(model_name="gpt-3.5-turbo-mock")
    shared_model = Model(model_requester=openai_requester)
    print("Model and Requester initialized.")

    # 2. Create Agent Tree
    agent_storage_tree = RedBlackTree()
    print("Agent Tree initialized.")

    # 3. Define Agents
    # Note: The 'task' for these agents will inform the mock model's behavior if it were more sophisticated.
    # For the current mock, the responses are fairly static.
    researcher_agent = Agent(
        agent_id="researcher001",
        model=shared_model,
        task="You are a research assistant. Your job is to find information based on a query. The information you find should be concise and factual.",
        tools=[], 
        agent_tree_instance=agent_storage_tree
    )
    agent_storage_tree.insert(researcher_agent.agent_id, researcher_agent)
    print(f"Agent '{researcher_agent.agent_id}' (Task: '{researcher_agent.task}') added to RBT.")

    writer_agent = Agent(
        agent_id="writer002",
        model=shared_model,
        task="You are a content writer. Your job is to write a brief summary based on provided text. The summary should be engaging and clear.",
        tools=[],
        agent_tree_instance=agent_storage_tree
    )
    agent_storage_tree.insert(writer_agent.agent_id, writer_agent)
    print(f"Agent '{writer_agent.agent_id}' (Task: '{writer_agent.task}') added to RBT.")
    
    calculator_tool_desc = {
        "name": "CalculatorExample",
        "description": "A simple example tool that echoes the input, pretending to be a calculator.",
        "parameters": {"type": "object", "properties": {"expression": {"type": "string", "description": "The mathematical expression to evaluate."}}},
        "returns": {"type": "object", "properties": {"result": {"type": "string"}}}
    }
    
    # Using ExampleTool but giving its description a more specific name for the demo
    class Calculator(ExampleTool):
        def get_description(self) -> str:
            return json.dumps(calculator_tool_desc)
        def call(self, tool_input: str) -> str:
            try:
                parsed_input = json.loads(tool_input)
                expression = parsed_input.get("expression", "N/A")
                # In a real calculator, you'd evaluate. Here, we just echo.
                return json.dumps({"result": f"Mock result for: {expression}"})
            except json.JSONDecodeError as e:
                return json.dumps({"error": "Invalid JSON input for Calculator", "details": str(e)})

    calculator_named_tool = Calculator()

    # 4. Define Coordinator Agent
    coordinator_task = (
        "You are a project coordinator. Your goal is to produce a short report on 'the benefits of unit testing'. "
        "First, use the 'researcher001' to find information on this topic. "
        "Then, use the 'writer002' to summarize the findings. "
        "If you need to calculate something simple, use the 'CalculatorExample'. "
        "Present the final report."
    )
    coordinator_agent = Agent(
        agent_id="coordinator007",
        model=shared_model, 
        task=coordinator_task,
        tools=["researcher001", "writer002", calculator_named_tool], # Agent IDs and a regular Tool
        agent_tree_instance=agent_storage_tree,
        max_iterations=7 # Allow more iterations for a multi-step task
    )
    agent_storage_tree.insert(coordinator_agent.agent_id, coordinator_agent)
    print(f"Agent '{coordinator_agent.agent_id}' (Task: '{coordinator_agent.task}') added to RBT.")

    print("\n--- Running Coordinator Agent ---")
    # The success of this run depends heavily on the mocked responses from OpenAIRequester.
    # The mock model needs to generate "Action: researcher001(...)" then "Action: writer002(...)" etc.
    # The current OpenAIRequester mock is generic: 
    # "Mocked OpenAI response to: '{prompt}'. Params: temp={kwargs.get('temperature', 'default')}"
    # This means the agent will likely not use tools effectively without more sophisticated mocking.
    # However, this example demonstrates the setup and potential.
    
    initial_task_for_coordinator = "Generate a report on 'the benefits of unit testing'."
    print(f"Giving task to coordinator: '{initial_task_for_coordinator}'")
    
    # To make the demo more illustrative, we'd ideally configure the shared_model's underlying
    # OpenAIRequester to provide a sequence of responses that trigger tool use.
    # E.g., first call -> "Action: researcher001(...)", second call -> "Action: writer002(...)", etc.
    # This is beyond the scope of the current static mock in OpenAIRequester.
    
    final_output = coordinator_agent.run(initial_user_input=initial_task_for_coordinator)

    print("\n--- Coordinator Agent Finished ---")
    print(f"Final Output from Coordinator: {final_output}")

    print("\n--- Verifying Agent Descriptions (as tools available to coordinator) ---")
    # This part shows how the coordinator agent perceives its available tools
    coordinator_tool_descs = []
    for tool_name_in_map, tool_instance_or_id in coordinator_agent.tool_map.items():
        if isinstance(tool_instance_or_id, str): # agent_id
            agent_in_tree = coordinator_agent.agent_tree.search(tool_instance_or_id)
            if agent_in_tree:
                 coordinator_tool_descs.append(agent_in_tree.get_agent_description_for_tool_list())
        elif hasattr(tool_instance_or_id, 'get_description'): # Tool object
            coordinator_tool_descs.append(tool_instance_or_id.get_description())
            
    print("Coordinator's parsed tool descriptions for its model prompt:")
    for desc_str in coordinator_tool_descs:
        print(json.dumps(json.loads(desc_str), indent=2)) # Pretty print

if __name__ == "__main__":
    main()
