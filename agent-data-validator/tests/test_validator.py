import unittest
import json
import tempfile
import os
from pathlib import Path
from validator import AgentDataValidator, ValidationConfig, ErrorType


class TestAgentDataValidator(unittest.TestCase):
    
    def setUp(self):
        """Set up test fixtures."""
        self.validator = AgentDataValidator()
        
    def create_temp_file(self, data):
        """Create a temporary JSON file with test data."""
        temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False)
        json.dump(data, temp_file, indent=2)
        temp_file.close()
        return temp_file.name
    
    def test_valid_conversation(self):
        """Test validation of a properly formatted conversation."""
        valid_data = [
            {
                "turn_id": 1,
                "speaker": "user",
                "message": "Hello"
            },
            {
                "turn_id": 2,
                "speaker": "assistant", 
                "assistant_reply": "Hi there!"
            }
        ]
        
        temp_file = self.create_temp_file(valid_data)
        try:
            errors = self.validator.validate_file(temp_file)
            self.assertEqual(len(errors), 0, "Valid conversation should have no errors")
        finally:
            os.unlink(temp_file)
    
    def test_missing_turn_id(self):
        """Test detection of missing turn_id."""
        invalid_data = [
            {
                "speaker": "user",
                "message": "Hello"
            }
        ]
        
        temp_file = self.create_temp_file(invalid_data)
        try:
            errors = self.validator.validate_file(temp_file)
            self.assertEqual(len(errors), 1)
            self.assertEqual(errors[0].error_type, ErrorType.MISSING_REQUIRED_KEY)
            self.assertIn("turn_id", errors[0].message)
        finally:
            os.unlink(temp_file)
    
    def test_tool_validation_complete(self):
        """Test valid tool usage."""
        valid_data = [
            {
                "turn_id": 1,
                "speaker": "assistant",
                "assistant_reply": "Using a tool",
                "tool_used": "search",
                "tool_input": {"query": "test"},
                "tool_output": {"results": ["result1", "result2"]}
            }
        ]
        
        temp_file = self.create_temp_file(valid_data)
        try:
            errors = self.validator.validate_file(temp_file)
            tool_errors = [e for e in errors if e.error_type == ErrorType.TOOL_VALIDATION]
            self.assertEqual(len(tool_errors), 0, "Complete tool usage should have no errors")
        finally:
            os.unlink(temp_file)


if __name__ == "__main__":
    unittest.main()