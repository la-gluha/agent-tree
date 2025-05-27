import unittest
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from prompt import CustomPrompt

class TestCustomPrompt(unittest.TestCase):

    def test_creation(self):
        p = CustomPrompt("Hello, {name}!")
        self.assertIsInstance(p, CustomPrompt)
        self.assertEqual(str(p), "Hello, {name}!")

    def test_get_placeholders_named(self):
        p = CustomPrompt("Hello, {name}! Welcome to {city}.")
        placeholders = p.get_placeholders()
        self.assertCountEqual(placeholders, ["name", "city"])

    def test_get_placeholders_indexed(self):
        p = CustomPrompt("Item {0}, Quantity {1}, Item {0} again.")
        placeholders = p.get_placeholders()
        self.assertCountEqual(placeholders, ["0", "1"])

    def test_get_placeholders_mixed(self):
        p = CustomPrompt("Hello, {name}, your order {0} is ready in {city}, item {1}.")
        placeholders = p.get_placeholders()
        self.assertCountEqual(placeholders, ["name", "0", "city", "1"])

    def test_get_placeholders_none(self):
        p = CustomPrompt("Just a plain string.")
        placeholders = p.get_placeholders()
        self.assertEqual(placeholders, [])

    def test_format_full_kwargs(self):
        p = CustomPrompt("Hello, {name}! Welcome to {city}.")
        formatted_str, filled = p.format(name="Alice", city="Wonderland")
        self.assertIsInstance(formatted_str, CustomPrompt)
        self.assertEqual(str(formatted_str), "Hello, Alice! Welcome to Wonderland.")
        self.assertEqual(filled, {"name": "Alice", "city": "Wonderland"})

    def test_format_partial_kwargs(self):
        p = CustomPrompt("Hello, {name}! Welcome to {city}.")
        formatted_str, filled = p.format(name="Bob")
        self.assertIsInstance(formatted_str, CustomPrompt)
        self.assertEqual(str(formatted_str), "Hello, Bob! Welcome to {city}.")
        self.assertEqual(filled, {"name": "Bob"})

    def test_format_full_args(self):
        p = CustomPrompt("Order: {0}, Item: {1}.")
        formatted_str, filled = p.format("123", "Book")
        self.assertIsInstance(formatted_str, CustomPrompt)
        self.assertEqual(str(formatted_str), "Order: 123, Item: Book.")
        self.assertEqual(filled, {"0": "123", "1": "Book"})

    def test_format_partial_args(self):
        p = CustomPrompt("Order: {0}, Item: {1}, Status: {2}.")
        formatted_str, filled = p.format("456", "Pen") # Only {0} and {1} filled
        self.assertIsInstance(formatted_str, CustomPrompt)
        self.assertEqual(str(formatted_str), "Order: 456, Item: Pen, Status: {2}.")
        self.assertEqual(filled, {"0": "456", "1": "Pen"})
        
    def test_format_mixed_args_kwargs(self):
        p = CustomPrompt("User: {name}, Order ID: {0}, Status: {status}, Item: {1}.")
        formatted_str, filled = p.format("A123", "Gadget", name="Charlie", status="Shipped")
        self.assertIsInstance(formatted_str, CustomPrompt)
        self.assertEqual(str(formatted_str), "User: Charlie, Order ID: A123, Status: Shipped, Item: Gadget.")
        self.assertEqual(filled, {"name": "Charlie", "0": "A123", "status": "Shipped", "1": "Gadget"})

    def test_format_kwargs_preferred_over_args(self):
        # If a numeric key is in kwargs, it should be used instead of args index.
        p = CustomPrompt("Value: {0}")
        formatted_str, filled = p.format("arg_value", **{"0": "kwarg_value"})
        self.assertEqual(str(formatted_str), "Value: kwarg_value")
        self.assertEqual(filled, {"0": "kwarg_value"})

    def test_format_no_placeholders(self):
        p = CustomPrompt("A simple string.")
        formatted_str, filled = p.format(name="Test")
        self.assertIsInstance(formatted_str, CustomPrompt)
        self.assertEqual(str(formatted_str), "A simple string.")
        self.assertEqual(filled, {})

    def test_format_empty_string(self):
        p = CustomPrompt("")
        formatted_str, filled = p.format(name="Test")
        self.assertIsInstance(formatted_str, CustomPrompt)
        self.assertEqual(str(formatted_str), "")
        self.assertEqual(filled, {})
        
    def test_format_with_curly_braces_not_placeholders(self):
        p = CustomPrompt("This is a set: {{1, 2}} and a dict: {{{'key': 'value'}}}. Format {var}.")
        formatted_str, filled = p.format(var="test")
        self.assertEqual(str(formatted_str), "This is a set: {1, 2} and a dict: {{'key': 'value'}}. Format test.")
        self.assertEqual(filled, {"var": "test"})

if __name__ == '__main__':
    unittest.main()
