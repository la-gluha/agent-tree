import re
from typing import Any, Dict, List, Tuple, Union

class CustomPrompt(str):
    """
    A custom string class that allows for advanced formatting capabilities,
    tracking of filled placeholders, and inspection of available placeholders.
    """

    def __new__(cls, value: object, *args: Any, **kwargs: Any) -> 'CustomPrompt':
        """
        Creates a new instance of CustomPrompt.
        Since str is immutable, __new__ is used for actual instance creation.
        """
        # The value is the string content itself. args and kwargs are not typically
        # used by str.__new__ when just a value is provided, but we accept them
        # to match a more general constructor signature if needed elsewhere, though
        # they are not used in this specific __new__ implementation for str.
        obj = str.__new__(cls, value)
        # No explicit call to super().__init__() is needed for str,
        # as immutable types are fully initialized by __new__.
        return obj

    def format(self, *args: Any, **kwargs: Any) -> Tuple['CustomPrompt', Dict[str, Any]]:
        """
        Formats the string using provided positional and keyword arguments.
        Returns the new formatted string (as CustomPrompt) and a dictionary of
        placeholders that were successfully filled.
        """
        filled_placeholders: Dict[str, Any] = {}

        def replace_callback(match_obj: re.Match) -> str:
            placeholder_key_full = match_obj.group(0) # e.g., "{name}" or "{0}"
            placeholder_key_inner = match_obj.group(1) # e.g., "name" or "0"

            value_to_substitute = None
            found = False

            if placeholder_key_inner in kwargs:
                value_to_substitute = kwargs[placeholder_key_inner]
                filled_placeholders[placeholder_key_inner] = value_to_substitute
                found = True
            else:
                try:
                    idx = int(placeholder_key_inner)
                    if 0 <= idx < len(args):
                        value_to_substitute = args[idx]
                        filled_placeholders[placeholder_key_inner] = value_to_substitute
                        found = True
                except ValueError:
                    # Not an integer, so not a positional argument index
                    pass
            
            if found:
                return str(value_to_substitute)
            else:
                # Return the original placeholder if not found in args or kwargs
                return placeholder_key_full

        # Regex to find placeholders like {key} or {0}
        # It captures the inner key/index in group 1
        placeholder_regex = r'{([a-zA-Z_]\w*|\d+)}'
        
        # Use self (the string content) for re.sub
        new_formatted_string = re.sub(placeholder_regex, replace_callback, self)
        
        return CustomPrompt(new_formatted_string), filled_placeholders

    def get_placeholders(self) -> List[str]:
        """
        Identifies all unique placeholders within the string.
        Returns a list of unique placeholder keys (e.g., "name", "0").
        """
        # Regex to find placeholders like {key} or {0}
        # It captures the inner key/index in group 1
        placeholder_regex = r'{([a-zA-Z_]\w*|\d+)}'
        
        # Find all matches in self (the string content)
        matches = re.findall(placeholder_regex, self)
        
        # Return a list of unique placeholder keys
        return sorted(list(set(matches)))

if __name__ == '__main__':
    # Example Usage:
    prompt_template = CustomPrompt("Hello {name}, your task is '{task}'. This is item {0} of {1}.")

    print(f"Original Prompt: '{prompt_template}'")
    print(f"Placeholders: {prompt_template.get_placeholders()}")

    formatted_prompt, filled = prompt_template.format("one", 2, name="Alice", task="review code")
    print(f"Formatted Prompt: '{formatted_prompt}'")
    print(f"Filled Placeholders: {filled}")

    formatted_prompt_partial, filled_partial = prompt_template.format(name="Bob")
    print(f"Partially Formatted Prompt: '{formatted_prompt_partial}'")
    print(f"Partially Filled Placeholders: {filled_partial}")
    print(f"Placeholders in partially formatted: {formatted_prompt_partial.get_placeholders()}")

    formatted_prompt_positional, filled_positional = prompt_template.format("first", 100)
    print(f"Positional Formatted Prompt: '{formatted_prompt_positional}'")
    print(f"Positional Filled Placeholders: {filled_positional}")
    print(f"Placeholders in positional: {formatted_prompt_positional.get_placeholders()}")

    no_fill_prompt, no_fill_filled = prompt_template.format()
    print(f"No Fill Formatted Prompt: '{no_fill_prompt}'")
    print(f"No Fill Filled Placeholders: {no_fill_filled}")
    print(f"Placeholders in no_fill_prompt: {no_fill_prompt.get_placeholders()}")

    # Test with CustomPrompt instance being formatted
    cp_instance = CustomPrompt("Test {var}")
    formatted_cp, filled_cp = cp_instance.format(var="value")
    print(f"Formatted CP: '{formatted_cp}', Type: {type(formatted_cp)}")
    print(f"Filled CP: {filled_cp}")
    
    # Test edge cases
    edge_case_prompt = CustomPrompt("No placeholders here.")
    print(f"Edge Case (no placeholders) Placeholders: {edge_case_prompt.get_placeholders()}")
    formatted_edge, filled_edge = edge_case_prompt.format(name="Test")
    print(f"Edge Case Formatted: '{formatted_edge}'")
    print(f"Edge Case Filled: {filled_edge}")

    empty_prompt = CustomPrompt("")
    print(f"Empty Prompt Placeholders: {empty_prompt.get_placeholders()}")
    formatted_empty, filled_empty = empty_prompt.format(name="Test")
    print(f"Empty Prompt Formatted: '{formatted_empty}'")
    print(f"Empty Prompt Filled: {filled_empty}")

    # Test with non-string values for substitution
    complex_prompt = CustomPrompt("Value: {0}, Data: {data}")
    formatted_complex, filled_complex = complex_prompt.format(123, data={"key": "value"})
    print(f"Complex Formatted: {formatted_complex}") # Should be "Value: 123, Data: {'key': 'value'}"
    print(f"Complex Filled: {filled_complex}")
    # Ensure it's still a CustomPrompt
    print(f"Type of complex_formatted: {type(formatted_complex)}")
