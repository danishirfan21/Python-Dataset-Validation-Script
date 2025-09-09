#!/usr/bin/env python3
"""
Agent Data Validator
A tool for validating multi-turn assistant conversation datasets for LLM training.
"""

import json
import yaml
import argparse
import sys
from typing import Dict, List, Any, Optional, Union
from pathlib import Path
from dataclasses import dataclass, field
from enum import Enum


class ErrorType(Enum):
    MISSING_REQUIRED_KEY = "missing_required_key"
    INVALID_TYPE = "invalid_type"
    INVALID_VALUE = "invalid_value"
    TURN_ID_SEQUENCE = "turn_id_sequence_error"
    TOOL_VALIDATION = "tool_validation_error"
    JSON_PARSE = "json_parse_error"


@dataclass
class ValidationError:
    line_number: int
    turn_id: Optional[int]
    error_type: ErrorType
    message: str
    suggestion: str
    field_name: Optional[str] = None


@dataclass
class ValidationConfig:
    """Configuration for validation rules, can be loaded from YAML."""
    required_keys_user: List[str] = field(default_factory=lambda: ["turn_id", "speaker"])
    required_keys_assistant: List[str] = field(default_factory=lambda: ["turn_id", "speaker", "assistant_reply"])
    optional_keys: List[str] = field(default_factory=lambda: ["tool_used", "tool_input", "tool_output"])
    valid_speakers: List[str] = field(default_factory=lambda: ["user", "assistant"])
    tool_keys_required_together: List[str] = field(default_factory=lambda: ["tool_input", "tool_output"])
    
    @classmethod
    def from_yaml(cls, yaml_path: str) -> 'ValidationConfig':
        """Load validation config from YAML file."""
        with open(yaml_path, 'r') as f:
            data = yaml.safe_load(f)
        return cls(**data)


class AgentDataValidator:
    """Main validator class for agent conversation datasets."""
    
    def __init__(self, config: Optional[ValidationConfig] = None):
        self.config = config or ValidationConfig()
        self.errors: List[ValidationError] = []
    
    def validate_file(self, file_path: str) -> List[ValidationError]:
        """Validate a JSON file containing conversation turns."""
        self.errors = []
        file_path = Path(file_path)
        
        if not file_path.exists():
            self.errors.append(ValidationError(
                line_number=0,
                turn_id=None,
                error_type=ErrorType.JSON_PARSE,
                message=f"File not found: {file_path}",
                suggestion="Check the file path and ensure the file exists."
            ))
            return self.errors
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Try to parse as JSON array or JSONL
            if content.strip().startswith('['):
                data = json.loads(content)
            else:
                # Handle JSONL format
                data = []
                for line_num, line in enumerate(content.strip().split('\n'), 1):
                    if line.strip():
                        try:
                            data.append(json.loads(line))
                        except json.JSONDecodeError as e:
                            self.errors.append(ValidationError(
                                line_number=line_num,
                                turn_id=None,
                                error_type=ErrorType.JSON_PARSE,
                                message=f"Invalid JSON on line {line_num}: {str(e)}",
                                suggestion="Fix the JSON syntax error."
                            ))
                            continue
                            
        except json.JSONDecodeError as e:
            self.errors.append(ValidationError(
                line_number=getattr(e, 'lineno', 0),
                turn_id=None,
                error_type=ErrorType.JSON_PARSE,
                message=f"Invalid JSON: {str(e)}",
                suggestion="Fix the JSON syntax error."
            ))
            return self.errors
        
        if not isinstance(data, list):
            self.errors.append(ValidationError(
                line_number=1,
                turn_id=None,
                error_type=ErrorType.INVALID_TYPE,
                message="Root data structure must be an array/list",
                suggestion="Wrap your data in square brackets [] to create a JSON array."
            ))
            return self.errors
        
        return self._validate_conversation_turns(data)
    
    def _validate_conversation_turns(self, turns: List[Dict[str, Any]]) -> List[ValidationError]:
        """Validate individual conversation turns."""
        expected_turn_id = 1
        
        for idx, turn in enumerate(turns, 1):
            if not isinstance(turn, dict):
                self.errors.append(ValidationError(
                    line_number=idx,
                    turn_id=None,
                    error_type=ErrorType.INVALID_TYPE,
                    message=f"Turn {idx} must be an object/dictionary",
                    suggestion="Ensure each conversation turn is a JSON object with key-value pairs."
                ))
                continue
            
            # Validate turn_id
            turn_id = self._validate_turn_id(turn, idx, expected_turn_id)
            if turn_id is not None:
                expected_turn_id = turn_id + 1
            
            # Validate speaker and related fields
            self._validate_speaker_and_content(turn, idx, turn_id)
            
            # Validate tool usage
            self._validate_tool_usage(turn, idx, turn_id)
        
        return self.errors
    
    def _validate_turn_id(self, turn: Dict[str, Any], line_num: int, expected: int) -> Optional[int]:
        """Validate turn_id field."""
        if "turn_id" not in turn:
            self.errors.append(ValidationError(
                line_number=line_num,
                turn_id=None,
                error_type=ErrorType.MISSING_REQUIRED_KEY,
                message="Missing required field: turn_id",
                suggestion="Add a 'turn_id' field with an integer value."
            ))
            return None
        
        turn_id = turn["turn_id"]
        if not isinstance(turn_id, int):
            self.errors.append(ValidationError(
                line_number=line_num,
                turn_id=turn_id,
                error_type=ErrorType.INVALID_TYPE,
                message=f"turn_id must be an integer, got {type(turn_id).__name__}",
                suggestion="Change turn_id to an integer value."
            ))
            return None
        
        if turn_id != expected:
            self.errors.append(ValidationError(
                line_number=line_num,
                turn_id=turn_id,
                error_type=ErrorType.TURN_ID_SEQUENCE,
                message=f"Expected turn_id {expected}, got {turn_id}",
                suggestion=f"Update turn_id to {expected} to maintain sequence."
            ))
        
        return turn_id
    
    def _validate_speaker_and_content(self, turn: Dict[str, Any], line_num: int, turn_id: Optional[int]):
        """Validate speaker field and related content requirements."""
        if "speaker" not in turn:
            self.errors.append(ValidationError(
                line_number=line_num,
                turn_id=turn_id,
                error_type=ErrorType.MISSING_REQUIRED_KEY,
                message="Missing required field: speaker",
                suggestion="Add a 'speaker' field with value 'user' or 'assistant'."
            ))
            return
        
        speaker = turn["speaker"]
        if not isinstance(speaker, str):
            self.errors.append(ValidationError(
                line_number=line_num,
                turn_id=turn_id,
                error_type=ErrorType.INVALID_TYPE,
                message=f"speaker must be a string, got {type(speaker).__name__}",
                suggestion="Change speaker to a string value."
            ))
            return
        
        if speaker not in self.config.valid_speakers:
            self.errors.append(ValidationError(
                line_number=line_num,
                turn_id=turn_id,
                error_type=ErrorType.INVALID_VALUE,
                message=f"Invalid speaker value: '{speaker}'. Must be one of {self.config.valid_speakers}",
                suggestion=f"Change speaker to one of: {', '.join(self.config.valid_speakers)}"
            ))
            return
        
        # Validate speaker-specific requirements
        if speaker == "assistant":
            if "assistant_reply" not in turn:
                self.errors.append(ValidationError(
                    line_number=line_num,
                    turn_id=turn_id,
                    error_type=ErrorType.MISSING_REQUIRED_KEY,
                    message="Assistant turns must include 'assistant_reply' field",
                    suggestion="Add an 'assistant_reply' field with the assistant's response."
                ))
            elif not isinstance(turn["assistant_reply"], str):
                self.errors.append(ValidationError(
                    line_number=line_num,
                    turn_id=turn_id,
                    error_type=ErrorType.INVALID_TYPE,
                    message=f"assistant_reply must be a string, got {type(turn['assistant_reply']).__name__}",
                    suggestion="Change assistant_reply to a string value."
                ))
        
        elif speaker == "user":
            if "assistant_reply" in turn:
                self.errors.append(ValidationError(
                    line_number=line_num,
                    turn_id=turn_id,
                    error_type=ErrorType.INVALID_VALUE,
                    message="User turns should not include 'assistant_reply' field",
                    suggestion="Remove the 'assistant_reply' field from user turns."
                ))
    
    def _validate_tool_usage(self, turn: Dict[str, Any], line_num: int, turn_id: Optional[int]):
        """Validate tool usage fields."""
        has_tool_used = "tool_used" in turn
        has_tool_input = "tool_input" in turn
        has_tool_output = "tool_output" in turn
        
        # If any tool field is present, validate tool_used
        if has_tool_input or has_tool_output:
            if not has_tool_used:
                self.errors.append(ValidationError(
                    line_number=line_num,
                    turn_id=turn_id,
                    error_type=ErrorType.TOOL_VALIDATION,
                    message="tool_input or tool_output present but tool_used is missing",
                    suggestion="Add 'tool_used' field when using tools."
                ))
            
            # If tool is used, both input and output should be present
            if not (has_tool_input and has_tool_output):
                missing = []
                if not has_tool_input:
                    missing.append("tool_input")
                if not has_tool_output:
                    missing.append("tool_output")
                
                self.errors.append(ValidationError(
                    line_number=line_num,
                    turn_id=turn_id,
                    error_type=ErrorType.TOOL_VALIDATION,
                    message=f"When using tools, both tool_input and tool_output are required. Missing: {', '.join(missing)}",
                    suggestion=f"Add the missing fields: {', '.join(missing)}"
                ))
        
        # Validate types if fields are present
        if has_tool_used and not isinstance(turn["tool_used"], str):
            self.errors.append(ValidationError(
                line_number=line_num,
                turn_id=turn_id,
                error_type=ErrorType.INVALID_TYPE,
                message=f"tool_used must be a string, got {type(turn['tool_used']).__name__}",
                suggestion="Change tool_used to a string value."
            ))
        
        if has_tool_input and not isinstance(turn["tool_input"], dict):
            self.errors.append(ValidationError(
                line_number=line_num,
                turn_id=turn_id,
                error_type=ErrorType.INVALID_TYPE,
                message=f"tool_input must be an object/dict, got {type(turn['tool_input']).__name__}",
                suggestion="Change tool_input to a JSON object."
            ))
        
        if has_tool_output and not isinstance(turn["tool_output"], dict):
            self.errors.append(ValidationError(
                line_number=line_num,
                turn_id=turn_id,
                error_type=ErrorType.INVALID_TYPE,
                message=f"tool_output must be an object/dict, got {type(turn['tool_output']).__name__}",
                suggestion="Change tool_output to a JSON object."
            ))
    
    def generate_report(self, format_type: str = "console") -> str:
        """Generate a validation report in console or markdown format."""
        if not self.errors:
            return "✅ All validations passed! Dataset is properly formatted.\n"
        
        if format_type == "markdown":
            return self._generate_markdown_report()
        else:
            return self._generate_console_report()
    
    def _generate_console_report(self) -> str:
        """Generate a console-formatted validation report."""
        report = f"\n❌ Found {len(self.errors)} validation error(s):\n"
        report += "=" * 60 + "\n\n"
        
        for error in self.errors:
            turn_info = f"Turn {error.turn_id}" if error.turn_id else "Unknown turn"
            report += f"🔴 Line {error.line_number} ({turn_info})\n"
            report += f"   Error: {error.message}\n"
            report += f"   Type: {error.error_type.value}\n"
            report += f"   💡 Suggestion: {error.suggestion}\n\n"
        
        return report
    
    def _generate_markdown_report(self) -> str:
        """Generate a markdown-formatted validation report."""
        if not self.errors:
            return "# Validation Report\n\n✅ **All validations passed!** Dataset is properly formatted.\n"
        
        report = f"# Validation Report\n\n"
        report += f"❌ **Found {len(self.errors)} validation error(s)**\n\n"
        
        # Group errors by type
        error_groups = {}
        for error in self.errors:
            error_type = error.error_type.value
            if error_type not in error_groups:
                error_groups[error_type] = []
            error_groups[error_type].append(error)
        
        for error_type, errors in error_groups.items():
            report += f"## {error_type.replace('_', ' ').title()}\n\n"
            
            for error in errors:
                turn_info = f"Turn {error.turn_id}" if error.turn_id else "Unknown turn"
                report += f"- **Line {error.line_number}** ({turn_info})\n"
                report += f"  - Error: {error.message}\n"
                report += f"  - 💡 Suggestion: {error.suggestion}\n\n"
        
        return report


def create_example_files():
    """Create example files for testing the validator."""
    
    # Valid example
    valid_data = [
        {
            "turn_id": 1,
            "speaker": "user",
            "message": "What's the weather like today?"
        },
        {
            "turn_id": 2,
            "speaker": "assistant",
            "assistant_reply": "I'll help you check the weather.",
            "tool_used": "weather_api",
            "tool_input": {"location": "current"},
            "tool_output": {"temperature": "72°F", "condition": "sunny"}
        },
        {
            "turn_id": 3,
            "speaker": "user",
            "message": "Thanks!"
        },
        {
            "turn_id": 4,
            "speaker": "assistant",
            "assistant_reply": "You're welcome! Is there anything else I can help you with?"
        }
    ]
    
    # Invalid example (for testing)
    invalid_data = [
        {
            "turn_id": 1,
            "speaker": "user",
            "message": "Hello"
        },
        {
            # Missing turn_id
            "speaker": "assistant",
            "assistant_reply": "Hi there!"
        },
        {
            "turn_id": "3",  # Should be integer
            "speaker": "invalid_speaker",  # Invalid speaker
            "assistant_reply": "This has errors"
        },
        {
            "turn_id": 5,  # Wrong sequence (should be 4)
            "speaker": "assistant",
            "assistant_reply": "Using a tool",
            "tool_used": "search",
            "tool_input": {"query": "test"}
            # Missing tool_output
        }
    ]
    
    # Save example files
    with open("valid_example.json", "w") as f:
        json.dump(valid_data, f, indent=2)
    
    with open("invalid_example.json", "w") as f:
        json.dump(invalid_data, f, indent=2)
    
    # Create example config
    config_data = {
        "required_keys_user": ["turn_id", "speaker"],
        "required_keys_assistant": ["turn_id", "speaker", "assistant_reply"],
        "optional_keys": ["tool_used", "tool_input", "tool_output", "message"],
        "valid_speakers": ["user", "assistant"],
        "tool_keys_required_together": ["tool_input", "tool_output"]
    }
    
    with open("validation_config.yaml", "w") as f:
        yaml.dump(config_data, f, default_flow_style=False)
    
    print("Created example files:")
    print("- valid_example.json")
    print("- invalid_example.json") 
    print("- validation_config.yaml")


def main():
    """Main CLI interface."""
    parser = argparse.ArgumentParser(
        description="Validate agent conversation datasets for LLM training"
    )
    parser.add_argument("file", help="JSON file to validate")
    parser.add_argument(
        "--config", "-c",
        help="YAML config file with validation rules"
    )
    parser.add_argument(
        "--format", "-f",
        choices=["console", "markdown"],
        default="console",
        help="Output format for the report"
    )
    parser.add_argument(
        "--output", "-o",
        help="Output file for the report (optional)"
    )
    parser.add_argument(
        "--create-examples",
        action="store_true",
        help="Create example files for testing"
    )
    
    args = parser.parse_args()
    
    if args.create_examples:
        create_example_files()
        return
    
    # Load configuration
    config = None
    if args.config:
        try:
            config = ValidationConfig.from_yaml(args.config)
        except Exception as e:
            print(f"Error loading config file: {e}")
            sys.exit(1)
    
    # Run validation
    validator = AgentDataValidator(config)
    errors = validator.validate_file(args.file)
    
    # Generate report
    report = validator.generate_report(args.format)
    
    if args.output:
        with open(args.output, 'w') as f:
            f.write(report)
        print(f"Report saved to {args.output}")
    else:
        print(report)
    
    # Exit with error code if validation failed
    sys.exit(1 if errors else 0)


if __name__ == "__main__":
    main()