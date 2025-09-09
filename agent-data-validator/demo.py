#!/usr/bin/env python3
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
            "turn_id": "2",  # Should be integer, not string
            "speaker": "bot",  # Invalid speaker (should be "assistant")
            "assistant_reply": "Hi there!"
        },
        {
            "turn_id": 4,  # Wrong sequence (should be 3)
            "speaker": "user",
            "message": "Can you search for something?"
        },
        {
            "turn_id": 4,  # Duplicate turn_id
            "speaker": "assistant",
            "assistant_reply": "I'll search for that information.",
            "tool_used": "search",
            "tool_input": {"query": "example"}
            # Missing tool_output - incomplete tool usage
        }
    ]
    
    return valid_conversation, invalid_conversation


def demonstrate_validation():
    """Demonstrate the validator with various scenarios."""
    
    print("=" * 60)
    print("🚀 AGENT DATA VALIDATOR DEMONSTRATION")
    print("=" * 60)
    
    # Create demo data
    valid_data, invalid_data = create_demo_data()
    
    # Create temporary files
    valid_file = tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False)
    invalid_file = tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False)
    
    try:
        # Write demo data to files
        json.dump(valid_data, valid_file, indent=2)
        json.dump(invalid_data, invalid_file, indent=2)
        valid_file.close()
        invalid_file.close()
        
        # Initialize validator
        validator = AgentDataValidator()
        
        print("\n📋 SCENARIO 1: Validating VALID conversation data")
        print("-" * 50)
        
        errors = validator.validate_file(valid_file.name)
        print(f"Errors found: {len(errors)}")
        print(validator.generate_report("console"))
        
        print("\n📋 SCENARIO 2: Validating INVALID conversation data")
        print("-" * 50)
        
        errors = validator.validate_file(invalid_file.name)
        print(f"Errors found: {len(errors)}")
        print(validator.generate_report("console"))
        
        print("\n📋 SCENARIO 3: Custom configuration example")
        print("-" * 50)
        
        # Create custom config that allows "system" speaker
        custom_config = ValidationConfig(
            valid_speakers=["user", "assistant", "system"],
            optional_keys=["tool_used", "tool_input", "tool_output", "metadata", "timestamp"]
        )
        
        # Create data with system message
        system_conversation = [
            {
                "turn_id": 1,
                "speaker": "system",
                "message": "You are a helpful assistant."
            },
            {
                "turn_id": 2,
                "speaker": "user", 
                "message": "Hello!"
            },
            {
                "turn_id": 3,
                "speaker": "assistant",
                "assistant_reply": "Hello! How can I help you today?"
            }
        ]
        
        system_file = tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False)
        json.dump(system_conversation, system_file, indent=2)
        system_file.close()
        
        # Validate with default config (should fail)
        default_validator = AgentDataValidator()
        errors_default = default_validator.validate_file(system_file.name)
        print(f"With default config - Errors: {len(errors_default)}")
        if errors_default:
            print("❌ System speaker not allowed in default config")
        
        # Validate with custom config (should pass)
        custom_validator = AgentDataValidator(custom_config)
        errors_custom = custom_validator.validate_file(system_file.name)
        print(f"With custom config - Errors: {len(errors_custom)}")
        if not errors_custom:
            print("✅ System speaker allowed in custom config")
        
        # Clean up system file
        os.unlink(system_file.name)
        
    finally:
        # Clean up temporary files
        os.unlink(valid_file.name)
        os.unlink(invalid_file.name)
    
    print("\n" + "=" * 60)
    print("✅ DEMONSTRATION COMPLETE")
    print("=" * 60)
    print("\nTo use the validator on your own data:")
    print("1. python validator.py your_file.json")
    print("2. python validator.py your_file.json --config custom_config.yaml")
    print("3. python validator.py your_file.json --format markdown --output report.md")
    print("\nTo create example files:")
    print("python validator.py --create-examples")


if __name__ == "__main__":
    demonstrate_validation()