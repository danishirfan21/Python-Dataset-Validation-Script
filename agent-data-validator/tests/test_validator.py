"""
Test suite for Agent Data Validator.
"""

import pytest
import json
import tempfile
import os
from pathlib import Path
from validator import AgentDataValidator, ValidationConfig, ErrorType, ValidationResult


class TestValidationConfig:
    """Test ValidationConfig class."""
    
    def test_default_config(self):
        """Test default configuration values."""
        config = ValidationConfig()
        assert config.min_turns == 1
        assert config.max_turns == 100
        assert config.min_message_length == 1
        assert config.max_message_length == 5000
        assert 'turn_id' in config.required_fields
        assert 'speaker' in config.required_fields
        assert 'user' in config.allowed_speakers
        assert 'assistant' in config.allowed_speakers
    
    def test_custom_config(self):
        """Test custom configuration values."""
        config = ValidationConfig(
            min_turns=5,
            max_turns=20,
            required_fields=['turn_id', 'speaker', 'message'],
            allowed_speakers=['user', 'bot']
        )
        assert config.min_turns == 5
        assert config.max_turns == 20
        assert config.required_fields == ['turn_id', 'speaker', 'message']
        assert config.allowed_speakers == ['user', 'bot']


class TestAgentDataValidator:
    """Test AgentDataValidator class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.validator = AgentDataValidator()
        self.config = ValidationConfig()
    
    def test_valid_conversation(self):
        """Test validation of valid conversation data."""
        valid_data = [
            {
                "turn_id": 1,
                "speaker": "user",
                "message": "Hello, how are you?"
            },
            {
                "turn_id": 2,
                "speaker": "assistant",
                "assistant_reply": "I'm doing well, thank you! How can I help you today?"
            }
        ]
        
        result = self.validator.validate_data(valid_data)
        assert result.is_valid
        assert result.total_turns == 2
        assert len(result.errors) == 0
    
    def test_empty_data(self):
        """Test validation of empty data."""
        result = self.validator.validate_data([])
        assert not result.is_valid
        assert any(error.error_type == ErrorType.STRUCTURE_ERROR for error in result.errors)
    
    def test_non_list_data(self):
        """Test validation of non-list data."""
        result = self.validator.validate_data({"not": "a list"})
        assert not result.is_valid
        assert any(error.error_type == ErrorType.STRUCTURE_ERROR for error in result.errors)
    
    def test_missing_required_fields(self):
        """Test validation when required fields are missing."""
        invalid_data = [
            {
                "speaker": "user",
                "message": "Hello"
                # Missing turn_id
            }
        ]
        
        result = self.validator.validate_data(invalid_data)
        assert not result.is_valid
        assert any(error.error_type == ErrorType.REQUIRED_FIELD_MISSING and 
                  error.field == 'turn_id' for error in result.errors)
    
    def test_invalid_speaker(self):
        """Test validation with invalid speaker."""
        invalid_data = [
            {
                "turn_id": 1,
                "speaker": "invalid_speaker",
                "message": "Hello"
            }
        ]
        
        result = self.validator.validate_data(invalid_data)
        assert not result.is_valid
        assert any(error.error_type == ErrorType.INVALID_FIELD_VALUE and 
                  error.field == 'speaker' for error in result.errors)
    
    def test_invalid_turn_id_type(self):
        """Test validation with invalid turn_id type."""
        invalid_data = [
            {
                "turn_id": "not_an_int",
                "speaker": "user",
                "message": "Hello"
            }
        ]
        
        result = self.validator.validate_data(invalid_data)
        assert not result.is_valid
        assert any(error.error_type == ErrorType.INVALID_FIELD_TYPE and 
                  error.field == 'turn_id' for error in result.errors)
    
    def test_user_turn_validation(self):
        """Test user turn specific validation."""
        # Valid user turn
        valid_data = [
            {
                "turn_id": 1,
                "speaker": "user",
                "message": "This is a valid message"
            }
        ]
        result = self.validator.validate_data(valid_data)
        assert result.is_valid
        
        # User turn missing message
        invalid_data = [
            {
                "turn_id": 1,
                "speaker": "user"
                # Missing message
            }
        ]
        result = self.validator.validate_data(invalid_data)
        assert not result.is_valid
        assert any(error.error_type == ErrorType.REQUIRED_FIELD_MISSING and 
                  error.field == 'message' for error in result.errors)
    
    def test_assistant_turn_validation(self):
        """Test assistant turn specific validation."""
        # Valid assistant turn
        valid_data = [
            {
                "turn_id": 1,
                "speaker": "assistant",
                "assistant_reply": "This is a valid assistant reply"
            }
        ]
        result = self.validator.validate_data(valid_data)
        assert result.is_valid
        
        # Assistant turn missing reply
        invalid_data = [
            {
                "turn_id": 1,
                "speaker": "assistant"
                # Missing assistant_reply
            }
        ]
        result = self.validator.validate_data(invalid_data)
        assert not result.is_valid
        assert any(error.error_type == ErrorType.REQUIRED_FIELD_MISSING and 
                  error.field == 'assistant_reply' for error in result.errors)
    
    def test_confidence_score_validation(self):
        """Test confidence score validation."""
        # Valid confidence score
        valid_data = [
            {
                "turn_id": 1,
                "speaker": "assistant",
                "assistant_reply": "Valid reply",
                "confidence_score": 0.85
            }
        ]
        result = self.validator.validate_data(valid_data)
        assert result.is_valid
        
        # Invalid confidence score (out of range)
        invalid_data = [
            {
                "turn_id": 1,
                "speaker": "assistant",
                "assistant_reply": "Valid reply",
                "confidence_score": 1.5  # Out of range
            }
        ]
        result = self.validator.validate_data(invalid_data)
        assert not result.is_valid
        assert any(error.error_type == ErrorType.INVALID_FIELD_VALUE and 
                  error.field == 'confidence_score' for error in result.errors)
    
    def test_tool_usage_validation(self):
        """Test tool usage validation."""
        # Valid tool usage
        valid_data = [
            {
                "turn_id": 1,
                "speaker": "assistant",
                "assistant_reply": "Let me search for that",
                "tool_used": "web_search",
                "tool_input": {"query": "test query"},
                "tool_output": {"results": ["result1", "result2"]}
            }
        ]
        result = self.validator.validate_data(valid_data)
        assert result.is_valid
        
        # Tool usage without required input/output
        invalid_data = [
            {
                "turn_id": 1,
                "speaker": "assistant",
                "assistant_reply": "Let me search for that",
                "tool_used": "web_search"
                # Missing tool_input and tool_output
            }
        ]
        result = self.validator.validate_data(invalid_data)
        assert not result.is_valid
        assert any(error.error_type == ErrorType.TOOL_ERROR for error in result.errors)
    
    def test_turn_sequence_validation(self):
        """Test turn sequence validation."""
        # Valid sequence
        valid_data = [
            {"turn_id": 1, "speaker": "user", "message": "Hello"},
            {"turn_id": 2, "speaker": "assistant", "assistant_reply": "Hi"},
            {"turn_id": 3, "speaker": "user", "message": "How are you?"}
        ]
        result = self.validator.validate_data(valid_data)
        assert result.is_valid
        
        # Invalid sequence
        invalid_data = [
            {"turn_id": 1, "speaker": "user", "message": "Hello"},
            {"turn_id": 3, "speaker": "assistant", "assistant_reply": "Hi"},  # Skipped 2
            {"turn_id": 4, "speaker": "user", "message": "How are you?"}
        ]
        result = self.validator.validate_data(invalid_data)
        assert not result.is_valid
        assert any(error.error_type == ErrorType.SEQUENCE_ERROR for error in result.errors)
    
    def test_message_length_validation(self):
        """Test message length validation."""
        config = ValidationConfig(min_message_length=10, max_message_length=50)
        validator = AgentDataValidator(config)
        
        # Message too short
        short_data = [
            {
                "turn_id": 1,
                "speaker": "user",
                "message": "Hi"  # Too short
            }
        ]
        result = validator.validate_data(short_data)
        assert not result.is_valid
        assert any(error.error_type == ErrorType.CONTENT_ERROR for error in result.errors)
        
        # Message too long
        long_data = [
            {
                "turn_id": 1,
                "speaker": "user",
                "message": "x" * 100  # Too long
            }
        ]
        result = validator.validate_data(long_data)
        assert not result.is_valid
        assert any(error.error_type == ErrorType.CONTENT_ERROR for error in result.errors)
    
    def test_file_validation(self):
        """Test file validation functionality."""
        # Create temporary file with valid data
        valid_data = [
            {
                "turn_id": 1,
                "speaker": "user",
                "message": "Hello world"
            },
            {
                "turn_id": 2,
                "speaker": "assistant",
                "assistant_reply": "Hi there! How can I help you?"
            }
        ]
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(valid_data, f, indent=2)
            temp_file = f.name
        
        try:
            result = self.validator.validate_file(temp_file)
            assert result.is_valid
            assert result.total_turns == 2
        finally:
            os.unlink(temp_file)
    
    def test_file_not_found(self):
        """Test validation of non-existent file."""
        result = self.validator.validate_file("nonexistent_file.json")
        assert not result.is_valid
        assert any(error.error_type == ErrorType.STRUCTURE_ERROR for error in result.errors)
    
    def test_custom_configuration(self):
        """Test validator with custom configuration."""
        config = ValidationConfig(
            min_turns=3,
            max_turns=5,
            allowed_speakers=['human', 'ai']
        )
        validator = AgentDataValidator(config)
        
        # Data with too few turns
        short_data = [
            {"turn_id": 1, "speaker": "human", "message": "Hello"}
        ]
        result = validator.validate_data(short_data)
        assert not result.is_valid
        
        # Data with custom speakers
        custom_data = [
            {"turn_id": 1, "speaker": "human", "message": "Hello"},
            {"turn_id": 2, "speaker": "ai", "assistant_reply": "Hi"},
            {"turn_id": 3, "speaker": "human", "message": "How are you?"}
        ]
        result = validator.validate_data(custom_data)
        assert result.is_valid


class TestValidationResult:
    """Test ValidationResult class."""
    
    def test_validation_result_creation(self):
        """Test ValidationResult creation and methods."""
        result = ValidationResult(is_valid=True, total_turns=5)
        assert result.is_valid
        assert result.total_turns == 5
        assert len(result.errors) == 0
        assert len(result.warnings) == 0
    
    def test_add_error(self):
        """Test adding errors to validation result."""
        result = ValidationResult(is_valid=True, total_turns=1)
        result.add_error(ErrorType.REQUIRED_FIELD_MISSING, "Test error", 1, "test_field")
        
        assert not result.is_valid  # Should become False after adding error
        assert len(result.errors) == 1
        assert result.errors[0].error_type == ErrorType.REQUIRED_FIELD_MISSING
        assert result.errors[0].message == "Test error"
        assert result.errors[0].turn_id == 1
        assert result.errors[0].field == "test_field"
    
    def test_add_warning(self):
        """Test adding warnings to validation result."""
        result = ValidationResult(is_valid=True, total_turns=1)
        result.add_warning("Test warning")
        
        assert result.is_valid  # Should remain True for warnings
        assert len(result.warnings) == 1
        assert result.warnings[0] == "Test warning"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
