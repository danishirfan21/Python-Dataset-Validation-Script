"""
Demo script showing the agent-data-validator in action.
Run this script to see examples of validation with both valid and invalid data.
"""

import json
import tempfile
import os
from validator import AgentDataValidator, ValidationConfig


def create_demo_data():
    """Create demonstration data for validation examples."""
    
    # Valid conversation data
    valid_conversation = [
        {
            "turn_id": 1,
            "speaker": "user",
            "message": "Hi! Can you help me find information about Python?"
        },
        {
            "turn_id": 2,
            "speaker": "assistant",
            "assistant_reply": "I'd be happy to help you learn about Python! Let me search for some information.",
            "tool_used": "web_search",
            "tool_input": {"query": "Python programming language basics"},
            "tool_output": {
                "results": [
                    "Python is a high-level programming language",
                    "Created by Guido van Rossum in 1991",
                    "Known for its simple and readable syntax"
                ]
            }
        },
        {
            "turn_id": 3,
            "speaker": "assistant", 
            "assistant_reply": "Based on my search, Python is a high-level programming language created by Guido van Rossum in 1991. It's known for its simple and readable syntax, making it great for beginners!"
        },
        {
            "turn_id": 4,
            "speaker": "user",
            "message": "That's great! Can you show me a simple example?"
        },
        {
            "turn_id": 5,
            "speaker": "assistant",
            "assistant_reply": "Here's a simple Python example:\n\nprint('Hello, World!')\nname = input('What is your name? ')\nprint(f'Nice to meet you, {name}!')\n\nThis code prints a greeting, asks for your name, and then greets you personally!"
        }
    ]
    
    # Invalid conversation data (multiple errors for demonstration)
    invalid_conversation = [
        {
            # Missing turn_id
            "speaker": "user",
            "message": "Hello"
        },
        {
            "turn_id": 2,
            # Missing speaker
            "message": "Hi there!"
        },
        {
            "turn_id": 3,
            "speaker": "assistant",
            # Missing assistant_reply
            "tool_used": "search",
            "tool_input": "invalid input - should be dict"
        }
    ]
    
    return valid_conversation, invalid_conversation


def run_validation_demo():
    """Run a comprehensive demo of the validation system."""
    
    print("=== Agent Data Validator Demo ===\n")
    
    # Create temporary files for demo
    valid_data, invalid_data = create_demo_data()
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(valid_data, f, indent=2)
        valid_file = f.name
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(invalid_data, f, indent=2)
        invalid_file = f.name
    
    try:
        # Create validator with custom config
        config = ValidationConfig(
            min_turns=2,
            max_turns=10,
            min_message_length=5,
            max_message_length=1000,
            required_fields=['turn_id', 'speaker'],
            allowed_speakers=['user', 'assistant']
        )
        
        validator = AgentDataValidator(config)
        
        print("1. Validating VALID conversation data:")
        print("-" * 40)
        result = validator.validate_file(valid_file)
        print(f"[VALID]: {result.is_valid}")
        print(f"Total turns: {result.total_turns}")
        print(f"Errors found: {len(result.errors)}")
        print(f"Warnings: {len(result.warnings)}")
        if result.warnings:
            print("Warnings:")
            for warning in result.warnings:
                print(f"  - {warning}")
        print()
        
        print("2. Validating INVALID conversation data:")
        print("-" * 40)
        result = validator.validate_file(invalid_file)
        print(f"[INVALID]: {result.is_valid}")
        print(f"Total turns: {result.total_turns}")
        print(f"Errors found: {len(result.errors)}")
        print("\nDetailed errors:")
        for error in result.errors:
            turn_info = f" (Turn {error.turn_id})" if error.turn_id else ""
            field_info = f" [{error.field}]" if error.field else ""
            print(f"  - {error.error_type.value}{turn_info}{field_info}: {error.message}")
        
        if result.warnings:
            print("\nWarnings:")
            for warning in result.warnings:
                print(f"  - {warning}")
        print()
        
        print("3. Configuration details:")
        print("-" * 40)
        print(f"Minimum turns required: {config.min_turns}")
        print(f"Maximum turns allowed: {config.max_turns}")
        print(f"Message length range: {config.min_message_length}-{config.max_message_length}")
        print(f"Required fields: {', '.join(config.required_fields)}")
        print(f"Allowed speakers: {', '.join(config.allowed_speakers)}")
        
        print("\n=== Demo Complete ===")
        print("\nTry running the validator on your own data:")
        print("python validator.py your_data.json")
        print("\nOr create example files to experiment with:")
        print("python validator.py --create-examples")
        
    finally:
        # Clean up temporary files
        os.unlink(valid_file)
        os.unlink(invalid_file)


if __name__ == "__main__":
    run_validation_demo()
