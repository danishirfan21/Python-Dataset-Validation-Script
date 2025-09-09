# Data Schema Documentation

This document describes the expected data schema for conversation datasets that can be validated using the Agent Data Validator.

## Overview

The validator expects conversation data as a JSON or YAML list containing conversation turns. Each turn represents either a user message or an assistant response in a multi-turn conversation.

## Schema Structure

### Root Level
```json
[
  // Array of turn objects
]
```

The root level must be an array/list containing turn objects.

### Turn Object Schema

Each turn object has the following structure:

#### Required Fields

| Field | Type | Description |
|-------|------|-------------|
| `turn_id` | integer | Unique sequential identifier for the turn (starting from 1) |
| `speaker` | string | Who is speaking: "user" or "assistant" |

#### Conditional Required Fields

| Field | Type | Required When | Description |
|-------|------|---------------|-------------|
| `message` | string | speaker = "user" | The user's message/input |
| `assistant_reply` | string | speaker = "assistant" | The assistant's response |

#### Optional Fields

| Field | Type | Description | Validation Rules |
|-------|------|-------------|------------------|
| `tool_used` | string | Name of tool used by assistant | Must be from allowed tools list (if configured) |
| `tool_input` | object | Input parameters for the tool | Required if `tool_used` is present; must be a valid JSON object |
| `tool_output` | any | Output returned by the tool | Required if `tool_used` is present; can be any valid JSON value |
| `confidence_score` | number | Assistant's confidence in response | Must be between 0.0 and 1.0 |
| `metadata` | object | Additional metadata | Can contain any valid JSON object |

## Validation Rules

### Basic Structure Rules

1. **Root Structure**: Data must be a valid JSON/YAML array
2. **Turn Structure**: Each turn must be a JSON object
3. **Non-empty**: Data cannot be empty
4. **Turn Count**: Must be within configured min/max turn limits

### Field Validation Rules

#### turn_id
- Must be a positive integer
- Must be unique within the conversation
- Should be sequential starting from 1 (if `check_turn_sequence` is enabled)

#### speaker
- Must be a string
- Must be one of the allowed speakers (default: "user", "assistant")
- Case-sensitive

#### message (User Turns)
- Required for user turns
- Must be a string
- Length must be within configured bounds
- Cannot be empty (unless `allow_empty_messages` is true)

#### assistant_reply (Assistant Turns)
- Required for assistant turns
- Must be a string
- Length must be within configured bounds
- Cannot be empty (unless `allow_empty_messages` is true)

#### tool_used
- Must be a string
- Must be from allowed tools list (if configured)
- If present, typically requires `tool_input` and `tool_output`

#### tool_input
- Must be a valid JSON object (dictionary)
- Required if `tool_used` is present (configurable)

#### tool_output
- Can be any valid JSON value
- Required if `tool_used` is present (configurable)

#### confidence_score
- Must be a number (integer or float)
- Must be between configured min/max values (default: 0.0-1.0)

## Example Valid Conversation

```json
[
  {
    "turn_id": 1,
    "speaker": "user",
    "message": "Hello! Can you help me learn about Python programming?"
  },
  {
    "turn_id": 2,
    "speaker": "assistant",
    "assistant_reply": "I'd be happy to help you learn Python! Let me search for some beginner resources.",
    "tool_used": "web_search",
    "tool_input": {
      "query": "Python beginner tutorial",
      "num_results": 5
    },
    "tool_output": {
      "results": [
        {"title": "Python.org Official Tutorial", "url": "https://docs.python.org/3/tutorial/"},
        {"title": "Real Python Beginner Guide", "url": "https://realpython.com/python-first-steps/"}
      ]
    },
    "confidence_score": 0.9
  },
  {
    "turn_id": 3,
    "speaker": "user",
    "message": "Great! Can you show me a simple example?"
  },
  {
    "turn_id": 4,
    "speaker": "assistant",
    "assistant_reply": "Here's a simple Python example:\n\n```python\nprint('Hello, World!')\nname = input('What is your name? ')\nprint(f'Nice to meet you, {name}!')\n```\n\nThis code prints a greeting, asks for your name, and then greets you personally!",
    "confidence_score": 0.95,
    "metadata": {
      "code_language": "python",
      "example_type": "basic"
    }
  }
]
```

## Common Validation Errors

### Structure Errors
- **Invalid root type**: Data is not an array/list
- **Empty data**: No turns provided
- **Invalid turn type**: Turn is not an object
- **Turn count violation**: Too few or too many turns

### Required Field Errors
- **Missing turn_id**: Turn object lacks `turn_id` field
- **Missing speaker**: Turn object lacks `speaker` field
- **Missing message**: User turn lacks `message` field
- **Missing assistant_reply**: Assistant turn lacks `assistant_reply` field

### Field Type Errors
- **Invalid turn_id type**: `turn_id` is not an integer
- **Invalid speaker type**: `speaker` is not a string
- **Invalid message type**: `message` is not a string
- **Invalid tool_input type**: `tool_input` is not an object

### Field Value Errors
- **Invalid speaker value**: Speaker not in allowed list
- **Invalid turn_id value**: `turn_id` is not positive
- **Invalid confidence_score**: Score outside allowed range
- **Invalid tool name**: Tool not in allowed tools list

### Content Errors
- **Empty message**: Message or reply is empty when not allowed
- **Message too short**: Below minimum length requirement
- **Message too long**: Above maximum length requirement

### Sequence Errors
- **Non-sequential turn_ids**: Turn IDs are not consecutive
- **Duplicate turn_ids**: Same turn_id appears multiple times

### Tool Errors
- **Missing tool_input**: `tool_used` present but `tool_input` missing
- **Missing tool_output**: `tool_used` present but `tool_output` missing
- **Invalid tool_input**: `tool_input` is not a valid JSON object

## Configuration Impact on Schema

The validation behavior can be customized through configuration:

### Turn Count Limits
```python
ValidationConfig(
    min_turns=2,     # Minimum required turns
    max_turns=50     # Maximum allowed turns
)
```

### Message Length Limits
```python
ValidationConfig(
    min_message_length=5,         # Minimum message length
    max_message_length=1000,      # Maximum message length
    min_assistant_reply_length=10, # Minimum assistant reply length
    max_assistant_reply_length=2000 # Maximum assistant reply length
)
```

### Required Fields
```python
ValidationConfig(
    required_fields=['turn_id', 'speaker', 'timestamp'],  # Custom required fields
    optional_fields=['message', 'assistant_reply', 'metadata']
)
```

### Speaker Validation
```python
ValidationConfig(
    allowed_speakers=['human', 'ai', 'system']  # Custom speaker types
)
```

### Tool Validation
```python
ValidationConfig(
    allowed_tools=['web_search', 'calculator', 'code_exec'],  # Allowed tools
    require_tool_input=True,   # tool_input required when tool_used present
    require_tool_output=True   # tool_output required when tool_used present
)
```

### Behavior Flags
```python
ValidationConfig(
    strict_mode=True,           # Enable strict validation
    check_turn_sequence=True,   # Validate turn_id sequence
    allow_empty_messages=False  # Allow empty messages/replies
)
```

## Schema Evolution

This schema is designed to be flexible and extensible. New optional fields can be added without breaking existing validation, but changes to required fields or validation rules should be carefully considered for backward compatibility.
